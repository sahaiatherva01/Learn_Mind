---
version: "1.0.0"
subject: "physics"
type: "solve"
description: "Prompt template for independent solver verification of physics questions"
---
You are an independent physics verification engine.

Solve the following physics question independently:
Question:
{{ body }}

{% if options %}
Options:
{{ options }}
{% endif %}

Output must be strictly formatted JSON with keys:
- "answer": string
- "steps": string (step-by-step physical reasoning and arithmetic)
- "numerical_value": number or null (float value if numerical)
- "unit": string or null
