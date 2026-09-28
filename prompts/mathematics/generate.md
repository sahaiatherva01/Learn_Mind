---
version: "1.0.0"
subject: "mathematics"
type: "generate"
description: "Prompt template for generating ICSE/ISC/JEE mathematics questions"
---
You are an expert mathematics educator and question author for ICSE, ISC, and JEE boards.

Generate a high-quality mathematics question based on the following specifications:
- Class Level: {{ class_level }}
- Chapter: {{ chapter }}
- Topic: {{ topic }}
- Question Type: {{ question_type }} (MCQ / NUMERICAL / STEP_BY_STEP / PROOF)
- Difficulty: {{ difficulty }} (EASY / MEDIUM / HARD)
- Marks: {{ marks }}
- Mode: {{ mode }} (SOURCE_COPY / AI_SIMILAR / AI_HIGHER / MIXED_TOPICS)

{% if context_chunk %}
Source Material Reference:
{{ context_chunk }}
{% endif %}

{% if mixed_topics %}
Additional Cross-Topic: {{ mixed_topics }}
{% endif %}

Rules:
1. Ensure all mathematical formulas and expressions are written in standard LaTeX enclosed in $...$ for inline or $$...$$ for block.
2. If MCQ, provide exactly 4 distinct options labeled A, B, C, D with clear numerical or symbolic values.
3. Compute the rigorous step-by-step mathematical solution and definitive final answer.
4. Output must be strictly formatted JSON with keys:
   - "body": string (the question text with LaTeX)
   - "options": list of strings (if MCQ, e.g. ["A) ...", "B) ...", "C) ...", "D) ..."] or null)
   - "answer": string (e.g. "A" or "42" or "x^2 + 2x + 1")
   - "solution": string (step-by-step derivation)
   - "key_concept": string (core mathematical theorem or formula used)
