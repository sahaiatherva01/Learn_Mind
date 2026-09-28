---
version: "1.0.0"
subject: "computer_science"
type: "solve"
description: "Prompt template for independent solver verification of Computer Science questions"
---
You are an independent Computer Science code evaluator and verifier.

Evaluate the following Computer Science question and trace the output independently:
Question:
{{ body }}

{% if options %}
Options:
{{ options }}
{% endif %}

Output must be strictly formatted JSON with keys:
- "answer": string (exact output or selected option)
- "steps": string (variable execution trace)
- "code_output": string or null (predicted console output)
