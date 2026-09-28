# Prompt template management per Rules.md D.4
import re
from pathlib import Path
from typing import Any

import yaml


class PromptManager:
    """
    Loads and renders versioned markdown prompts with YAML frontmatter.
    Rules.md D.4: Prompts are versioned files (/prompts/<subject>/<type>.md)
    """

    def __init__(self, base_dir: Path | None = None):
        if base_dir is None:
            # Try repo root prompts or backend relative
            possible_roots = [
                Path(__file__).resolve().parents[4] / "prompts",
                Path(__file__).resolve().parents[3] / "prompts",
                Path(__file__).resolve().parents[2] / "prompts",
                Path.cwd() / "prompts",
                Path.cwd().parent / "prompts",
            ]
            for candidate in possible_roots:
                if candidate.exists() and candidate.is_dir():
                    base_dir = candidate
                    break
            if base_dir is None:
                base_dir = possible_roots[0]

        self.base_dir = base_dir

    def load_prompt(self, subject: str, prompt_type: str) -> tuple[dict[str, Any], str]:
        """
        Loads the frontmatter metadata and template body from /prompts/<subject>/<type>.md
        """
        # Normalize subject (e.g. "Computer Science" -> "computer_science")
        normalized_subject = subject.lower().replace(" ", "_")
        target_file = self.base_dir / normalized_subject / f"{prompt_type}.md"

        if not target_file.exists():
            # Fallback to general if subject-specific not found
            general_file = self.base_dir / "general" / f"{prompt_type}.md"
            if general_file.exists():
                target_file = general_file
            else:
                raise FileNotFoundError(f"Prompt template not found at {target_file} or {general_file}")

        content = target_file.read_text(encoding="utf-8")
        meta = {}
        body = content

        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                try:
                    meta = yaml.safe_load(parts[1]) or {}
                except Exception:
                    meta = {}
                body = parts[2].strip()

        return meta, body

    def render(self, subject: str = "general", prompt_type: str = "generate", **variables: Any) -> str:
        """
        Renders the prompt template substituting variables.
        Supports simple jinja-like {{ key }} and {% if key %} blocks.
        """
        target_subject = variables.pop("subject", subject) or subject
        variables["subject"] = target_subject
        _, body = self.load_prompt(target_subject, prompt_type)

        # Handle simple {% if var %} ... {% endif %} blocks
        def replace_if(match: re.Match) -> str:
            var_name = match.group(1).strip()
            inner_content = match.group(2)
            val = variables.get(var_name)
            if val and str(val).strip():
                return inner_content
            return ""

        body = re.sub(r"{%\s*if\s+([a-zA-Z0-9_]+)\s*%}(.*?){%\s*endif\s*%}", replace_if, body, flags=re.DOTALL)

        # Substitute {{ key }}
        for key, value in variables.items():
            pattern = re.compile(r"{{\s*" + re.escape(key) + r"\s*}}")
            body = pattern.sub(str(value) if value is not None else "", body)

        # Clean remaining unmatched variables
        body = re.sub(r"{{\s*[a-zA-Z0-9_]+\s*}}", "", body)

        return body.strip()


prompt_manager = PromptManager()
