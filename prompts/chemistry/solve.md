---
version: "1.0.0"
subject: "chemistry"
type: "solve"
description: "Prompt template for independent solver verification of chemistry questions"
---
You are an independent chemistry verification solver.

Solve the following chemistry problem:
Question:
{{ body }}

{% if options %}
Options:
{{ options }}
{% endif %}

Output must be strictly formatted JSON with keys:
- "answer": string
- "steps": string (reaction pathway or calculation steps)
- "balanced_equation": string or null
- "reaction_smiles": string or null
