import json
import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def evaluate_solver_proposal(problem, solver_profile, proposal):

    prompt = f"""
You are SolveNet's AI Solution Evaluator.

Evaluate a proposed solution for a real-world civic problem.

IMPORTANT:
- Evaluate the SOLUTION, not the person.
- Do not judge the solver's intelligence, ability, personality,
  or worth.
- Do not compare the solver with other people.
- Decide whether the proposed solution is sufficiently aligned
  with the selected problem to move forward.
- Be practical and evidence-based.

PROBLEM
-------
Title:
{problem.get("title", "")}

Description:
{problem.get("problem", "")}

Problem Brief:
{json.dumps(problem.get("problem_brief", {}), indent=2)}

Domain:
{json.dumps(problem.get("domain", []))}

Required Skills:
{json.dumps(problem.get("required_skills", []))}


SOLVER PROFILE
--------------
Skills:
{json.dumps(solver_profile.get("skills", []))}

Interests:
{json.dumps(solver_profile.get("interests", []))}

Experience:
{solver_profile.get("experience", "")}


PROPOSED SOLUTION
-----------------
{proposal}


EVALUATION CRITERIA
-------------------
Evaluate the proposal on:

1. Problem Alignment
2. Technical Feasibility
3. Expected Impact
4. Innovation
5. Scalability
6. Resource Requirements

Give each criterion a score from 0 to 100.

Then calculate an overall score.

Decision rules:

PASS:
Overall score >= 65 AND
Problem Alignment >= 60 AND
Technical Feasibility >= 60

NOT PASS:
Anything below those conditions.

If NOT PASS, explain what should be improved.

If PASS, explain why the proposal is sufficiently aligned
and feasible to move forward.

Return ONLY valid JSON:

{{
    "decision": "PASS",
    "overall_score": 82,
    "problem_alignment": {{
        "score": 85,
        "feedback": "..."
    }},
    "technical_feasibility": {{
        "score": 80,
        "feedback": "..."
    }},
    "expected_impact": {{
        "score": 84,
        "feedback": "..."
    }},
    "innovation": {{
        "score": 78,
        "feedback": "..."
    }},
    "scalability": {{
        "score": 76,
        "feedback": "..."
    }},
    "resource_requirements": {{
        "score": 82,
        "feedback": "..."
    }},
    "summary": "...",
    "improvements": [
        "...",
        "..."
    ]
}}
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a careful solution evaluation engine. "
                    "Evaluate only the proposed solution. "
                    "Return valid JSON only."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
        response_format={
            "type": "json_object"
        }
    )

    content = response.choices[0].message.content

    return json.loads(content)