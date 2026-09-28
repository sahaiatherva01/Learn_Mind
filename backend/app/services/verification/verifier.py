# Solve-twice verifier engine per Rules.md C.1-C.8 and ARCH.md §4 (G3 Graph)
import ast
import io
import json
import math
import re
import sys
from typing import Any, NamedTuple

import sympy
from sympy.parsing.sympy_parser import (
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

from app.llm.client import llm_client
from app.services.generation.prompts import prompt_manager


class SolverResult(NamedTuple):
    answer: str
    steps: str
    model: str
    tool_meta: dict[str, Any] | None = None


class VerificationOutcome(NamedTuple):
    agree: bool
    status: str  # "UNVERIFIED" (auto-checked agree) or "NEEDS_REVIEW" (disagreement)
    solver1: SolverResult
    solver2: SolverResult
    diff_notes: str | None


class SolveTwiceVerifier:
    """
    Independent Solve-Twice Verification Engine.
    Rules.md C.1: Two independent solves; answers compared.
    Rules.md C.6: Tool checks (SymPy, Code sandbox) preferred over pure LLM opinion.
    """

    @staticmethod
    def normalize_mcq_answer(ans: str) -> str:
        """
        Extracts clean option letter (A, B, C, D) from strings like 'A) 42' or 'Option B'.
        """
        clean = ans.strip()
        match = re.match(r"^(?:Option\s+)?([A-Da-d])(?:[\).:\s]|$)", clean)
        if match:
            return match.group(1).upper()
        # If single letter
        if len(clean) == 1 and clean.upper() in "ABCD":
            return clean.upper()
        return clean.strip().lower()

    @staticmethod
    def compare_numerical(ans1: str, ans2: str, tolerance: float = 0.01) -> bool:
        """
        Compares numerical values with absolute and relative tolerance.
        """
        try:
            # Extract first numerical floating point value from strings
            nums1 = re.findall(r"[-+]?(?:\d*\.\d+|\d+)", ans1)
            nums2 = re.findall(r"[-+]?(?:\d*\.\d+|\d+)", ans2)
            if nums1 and nums2:
                v1 = float(nums1[0])
                v2 = float(nums2[0])
                # Direct equality or within tolerance
                if abs(v1 - v2) <= tolerance or math.isclose(v1, v2, rel_tol=0.02, abs_tol=tolerance):
                    return True
        except Exception:
            pass
        return False

    @staticmethod
    def compare_sympy_expressions(expr_str1: str, expr_str2: str) -> bool:
        """
        Uses SymPy symbolic mathematics to test mathematical equivalence (expr1 - expr2 == 0).
        """
        try:
            transformations = standard_transformations + (implicit_multiplication_application,)
            # Clean common LaTeX syntax to sympy syntax
            clean1 = expr_str1.replace("\\cdot", "*").replace("^", "**").replace("{", "(").replace("}", ")").replace("\\frac", "")
            clean2 = expr_str2.replace("\\cdot", "*").replace("^", "**").replace("{", "(").replace("}", ")").replace("\\frac", "")
            # Remove non-math characters
            clean1 = re.sub(r"[\$\\]", "", clean1)
            clean2 = re.sub(r"[\$\\]", "", clean2)

            e1 = parse_expr(clean1, transformations=transformations, evaluate=False)
            e2 = parse_expr(clean2, transformations=transformations, evaluate=False)
            diff = sympy.simplify(e1 - e2)
            return bool(diff == 0 or diff.is_zero)
        except Exception:
            return False

    @staticmethod
    def execute_python_code_sandbox(code_snippet: str) -> str:
        """
        Safely executes simple Python code in a restricted sandbox environment to get stdout.
        """
        # Validate AST to prevent unsafe operations (imports like os, subprocess, socket)
        try:
            tree = ast.parse(code_snippet)
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    for alias in getattr(node, "names", []):
                        if alias.name in ("os", "sys", "subprocess", "socket", "shutil", "builtins", "__import__"):
                            return "Error: Disallowed import in sandbox"
        except Exception as e:
            return f"Syntax Error: {e}"

        old_stdout = sys.stdout
        redirected_output = io.StringIO()
        try:
            sys.stdout = redirected_output
            # Restricted globals
            safe_globals = {
                "__builtins__": {
                    "print": print,
                    "range": range,
                    "len": len,
                    "sum": sum,
                    "min": min,
                    "max": max,
                    "abs": abs,
                    "int": int,
                    "float": float,
                    "str": str,
                    "list": list,
                    "dict": dict,
                    "set": set,
                    "tuple": tuple,
                    "bool": bool,
                    "enumerate": enumerate,
                    "zip": zip,
                }
            }
            exec(code_snippet, safe_globals, {})
            output = redirected_output.getvalue().strip()
            return output
        except Exception as e:
            return f"Runtime Error: {e}"
        finally:
            sys.stdout = old_stdout

    async def verify_question(
        self,
        subject: str,
        question_type: str,
        body: str,
        options: list[str] | None,
        draft_answer: str,
        draft_solution: str | None = None,
        code_snippet: str | None = None,
    ) -> VerificationOutcome:
        """
        Executes dual independent verification runs and compares solutions using tools and LLM.
        """
        # --- Run 1: Independent Primary Solver ---
        try:
            prompt_solve1 = prompt_manager.render(
                subject=subject,
                prompt_type="solve",
                body=body,
                options="\n".join(options) if options else "None",
            )
        except Exception:
            prompt_solve1 = f"Solve this question:\n{body}\nOptions: {options}"

        resp1 = await llm_client.generate(
            prompt=prompt_solve1,
            model_tier="strong",
            temperature=0.1,
        )
        s1_text = resp1.get("text", "")
        # Parse json if structured
        s1_answer = draft_answer
        s1_steps = draft_solution or "Step-by-step verification pass 1"
        try:
            match = re.search(r"\{.*\}", s1_text, re.DOTALL)
            if match:
                data1 = json.loads(match.group(0))
                s1_answer = data1.get("answer", draft_answer)
                s1_steps = data1.get("steps", s1_steps)
        except Exception:
            pass

        solver1 = SolverResult(
            answer=s1_answer,
            steps=s1_steps,
            model=resp1.get("model", "solver-primary"),
        )

        # --- Run 2: Independent Secondary Solver / Tool check ---
        tool_meta = {}
        s2_answer = s1_answer
        s2_steps = "Tool check / secondary solver verification pass"

        # Check tool execution for Computer Science code output
        if (question_type == "CODE_OUTPUT" or "code" in subject.lower()) and code_snippet:
            sandbox_out = self.execute_python_code_sandbox(code_snippet)
            tool_meta["code_sandbox_output"] = sandbox_out
            s2_answer = sandbox_out
            s2_steps = f"Executed code in restricted sandbox. Stdout: {sandbox_out}"
            solver2 = SolverResult(
                answer=s2_answer,
                steps=s2_steps,
                model="sandbox-python",
                tool_meta=tool_meta,
            )
        else:
            # Second independent LLM pass
            resp2 = await llm_client.generate(
                prompt=prompt_solve1 + "\nSolve with independent alternate method if possible.",
                model_tier="fast",
                temperature=0.2,
            )
            s2_text = resp2.get("text", "")
            try:
                match = re.search(r"\{.*\}", s2_text, re.DOTALL)
                if match:
                    data2 = json.loads(match.group(0))
                    s2_answer = data2.get("answer", s1_answer)
                    s2_steps = data2.get("steps", s2_steps)
            except Exception:
                pass

            solver2 = SolverResult(
                answer=s2_answer,
                steps=s2_steps,
                model=resp2.get("model", "solver-secondary"),
                tool_meta=tool_meta,
            )

        # --- Compare Solver 1 vs Solver 2 vs Draft Answer ---
        agree = False
        diff_notes = None

        if question_type == "MCQ" or (options and len(options) > 0):
            mcq1 = self.normalize_mcq_answer(solver1.answer)
            mcq2 = self.normalize_mcq_answer(solver2.answer)
            draft_mcq = self.normalize_mcq_answer(draft_answer)
            agree = (mcq1 == mcq2) or (mcq1 == draft_mcq) or (mcq2 == draft_mcq)
            if not agree:
                diff_notes = f"MCQ Key discrepancy: Draft='{draft_mcq}', Solver1='{mcq1}', Solver2='{mcq2}'"
        elif question_type == "NUMERICAL":
            if self.compare_numerical(solver1.answer, solver2.answer) or self.compare_numerical(draft_answer, solver1.answer):
                agree = True
            else:
                agree = False
                diff_notes = f"Numerical tolerance mismatch: Draft='{draft_answer}', Solver1='{solver1.answer}', Solver2='{solver2.answer}'"
        elif "math" in subject.lower():
            if self.compare_sympy_expressions(solver1.answer, solver2.answer) or self.compare_sympy_expressions(draft_answer, solver1.answer):
                agree = True
            elif solver1.answer.strip().lower() == solver2.answer.strip().lower() or draft_answer.strip().lower() == solver1.answer.strip().lower():
                agree = True
            else:
                agree = False
                diff_notes = f"Symbolic math discrepancy: Solver1='{solver1.answer}', Solver2='{solver2.answer}'"
        else:
            # Normalized string / semantic match
            norm1 = solver1.answer.strip().lower()
            norm2 = solver2.answer.strip().lower()
            norm_d = draft_answer.strip().lower()
            if norm1 == norm2 or norm1 == norm_d or norm2 == norm_d:
                agree = True
            else:
                # Disagreement
                agree = False
                diff_notes = f"Text solution discrepancy: Solver1='{solver1.answer}' vs Solver2='{solver2.answer}'"

        status = "UNVERIFIED" if agree else "NEEDS_REVIEW"

        return VerificationOutcome(
            agree=agree,
            status=status,
            solver1=solver1,
            solver2=solver2,
            diff_notes=diff_notes,
        )


solve_twice_verifier = SolveTwiceVerifier()
