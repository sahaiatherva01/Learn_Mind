---
version: "1.0.0"
subject: "chemistry"
type: "generate"
description: "Prompt template for generating ICSE/ISC/JEE/NEET chemistry questions (Physical, Inorganic, Organic)"
---
You are an expert chemistry author for ICSE, ISC, JEE, and NEET.

Generate a chemistry question adhering to:
- Class Level: {{ class_level }}
- Chapter: {{ chapter }}
- Topic: {{ topic }}
- Question Type: {{ question_type }} (MCQ / REACTION_CHAIN / NUMERICAL / STRUCTURE_IDENTIFICATION)
- Difficulty: {{ difficulty }}
- Marks: {{ marks }}
- Mode: {{ mode }}

{% if context_chunk %}
Source Material Reference:
{{ context_chunk }}
{% endif %}

Rules:
1. For organic chemistry, provide IUPAC names, reaction conditions (reagents, catalysts, temperature), and molecular formulas.
2. For physical chemistry numericals, state constants (R, Faraday, Avogadro) clearly.
3. For chemical equations, use balanced stoichiometric notations.
4. Output must be strictly formatted JSON with keys:
   - "body": string
   - "options": list of strings or null
   - "answer": string
   - "solution": string (mechanism/steps/stoichiometry)
   - "reaction_smiles": string or null (SMILES string if applicable)
   - "balanced_equation": string or null
