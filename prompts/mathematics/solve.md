---
version: "1.0.0"
subject: "mathematics"
type: "solve"
description: "Prompt template for independent solver verification of mathematics questions"
---
You are an independent, highly rigorous mathematical solver and verifier.

Solve the following question independently from first principles. Do not guess. Show step-by-step working and state the exact final answer.

Question:
{{ body }}

{% if options %}
Options:
{{ options }}
{% endif %}

Output must be strictly formatted JSON with keys:
- "answer": string (the exact final answer or option key, e.g. "B" or "3/4" or "2*pi")
- "steps": string (step-by-step mathematical derivation)
- "sympy_expression": string or null (equivalent Python SymPy expression for symbolic verification if applicable)
