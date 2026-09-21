import json
import os

from dotenv import load_dotenv
from groq import Groq


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY was not found. "
        "Please check your .env file."
    )


client = Groq(
    api_key=GROQ_API_KEY
)


# ============================================================
# GENERATE STARTER KIT
# ============================================================

def generate_starter_kit(problem_brief, matches):

    problem_text = json.dumps(
        problem_brief,
        indent=2
    )

    matches_text = json.dumps(
        matches,
        indent=2
    )


    prompt = f"""
You are SolveNet's AI Solution Starter Kit Generator.

SolveNet helps people turn real-world problems into
actionable projects.

You have received:

1. A structured problem brief.
2. A list of relevant people/projects identified
   by the AI matchmaking engine.

Your job is to generate a practical STARTER KIT
that helps a project team begin solving the problem.

==================================================
STRUCTURED PROBLEM
==================================================

{problem_text}


==================================================
RELEVANT MATCHES
==================================================

{matches_text}


==================================================
GENERATE THE FOLLOWING
==================================================

1. Problem Summary

Explain the problem clearly in 2-4 sentences.

2. Proposed Solution Direction

Describe a possible technical direction.

Do NOT claim that this is the only solution.

3. Literature Review

Give 3-5 relevant research directions or concepts.

Do not invent paper titles, authors or citations.

Use broad research topics when exact references
are not available.

4. Similar Case Studies

Give 3-5 examples of similar types of systems,
projects or approaches.

Do not invent specific organizations or statistics.

5. Suggested Technology Stack

Recommend technologies for:

- Frontend
- Backend
- AI/ML
- Database
- APIs
- Hardware, if relevant
- Deployment

Only recommend technologies that make sense
for the problem.

6. System Architecture

Describe the major components and how data
flows between them.

7. Implementation Roadmap

Give 5-7 practical implementation steps.

8. Starter Code

Provide a small useful code example that helps
a developer begin the project.

The code should be simple and focused on the
core technical idea.

9. Success Metrics

Give measurable ways to determine whether
the solution works.

10. Risks and Challenges

Identify important technical or practical risks.

11. Recommended Team Roles

Suggest roles based on the problem and
the available matches.

==================================================
IMPORTANT RULES
==================================================

- Do not invent facts.
- Do not invent research papers.
- Do not invent organizations.
- Clearly distinguish suggestions from established facts.
- Keep the solution practical.
- Prefer simple technologies for a prototype.
- Use the available people's skills when suggesting
  team roles.
- The starter code must be valid.
- Return ONLY valid JSON.

Required JSON structure:

{{
    "problem_summary": "...",

    "solution_direction": "...",

    "literature_review": [
        {{
            "topic": "...",
            "why_relevant": "..."
        }}
    ],

    "case_studies": [
        {{
            "title": "...",
            "description": "..."
        }}
    ],

    "technology_stack": {{
        "frontend": ["..."],
        "backend": ["..."],
        "ai_ml": ["..."],
        "database": ["..."],
        "apis": ["..."],
        "hardware": ["..."],
        "deployment": ["..."]
    }},

    "architecture": [
        {{
            "component": "...",
            "description": "..."
        }}
    ],

    "implementation_roadmap": [
        "Step 1...",
        "Step 2..."
    ],

    "starter_code": {{
        "language": "...",
        "filename": "...",
        "code": "..."
    }},

    "success_metrics": [
        "..."
    ],

    "risks": [
        "..."
    ],

    "team_roles": [
        {{
            "role": "...",
            "suggested_match": "...",
            "responsibility": "..."
        }}
    ]
}}
"""


    response = client.chat.completions.create(

        model="openai/gpt-oss-120b",

        messages=[

            {
                "role": "system",
                "content": (
                    "You are SolveNet's solution planning "
                    "and starter kit generation engine. "
                    "Return only valid JSON."
                )
            },

            {
                "role": "user",
                "content": prompt
            }

        ],

        temperature=0.3,

        response_format={
            "type": "json_object"
        }
    )


    content = (
        response
        .choices[0]
        .message
        .content
    )


    result = json.loads(content)

    return result