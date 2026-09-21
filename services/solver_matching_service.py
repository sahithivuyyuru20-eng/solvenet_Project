import json
import os

from dotenv import load_dotenv
from groq import Groq

from services.database_service import get_open_problems

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def find_problem_matches(solver_profile):
    """
    Match a solver with the most relevant open civic problems.

    Returns 3-5 real problems from the database.
    """

    # Get all currently open problems
    problems = get_open_problems()

    if not problems:
        return []

    # Prepare solver information
    solver_name = solver_profile.get("name", "")
    skills = solver_profile.get("skills", [])
    interests = solver_profile.get("interests", [])
    experience = solver_profile.get("experience", "")

    # Prepare problem information for AI
    problem_data = []

    for problem in problems:
        problem_data.append({
            "problem_id": problem["id"],
            "title": problem["title"],
            "problem": problem["problem"],
            "problem_brief": problem.get("problem_brief", {}),
            "domain": problem.get("domain", []),
            "required_skills": problem.get("required_skills", [])
        })

    prompt = f"""
You are SolveNet's AI Problem Matchmaker.

Your job is to match a solver with real-world civic problems
that are available in SolveNet's problem database.

SOLVER PROFILE
---------------
Name:
{solver_name}

Skills:
{json.dumps(skills)}

Interests:
{json.dumps(interests)}

Projects / Experience:
{experience}


AVAILABLE PROBLEMS
------------------
{json.dumps(problem_data, indent=2)}


TASK
----
Select the 3 to 5 most relevant problems for this solver.

Consider:

1. Skill compatibility
2. Interest/domain compatibility
3. Previous experience
4. Technical relevance
5. Potential contribution the solver can realistically make

IMPORTANT RULES
---------------
- Only select problems from the AVAILABLE PROBLEMS list.
- Never invent a problem.
- Never invent a problem ID.
- A problem ID must exactly match one of the provided IDs.
- Return between 3 and 5 problems when possible.
- If fewer than 3 problems exist, return all available problems.
- Give a match score from 0 to 100.
- Explain why the problem matches the solver.
- List the specific solver skills that match the problem.
- Do not evaluate the solver as a person.
- Evaluate only compatibility between the solver and the problem.

Return ONLY valid JSON in this format:

{{
    "matches": [
        {{
            "problem_id": 1,
            "match_score": 92,
            "match_reason": "The problem requires Python and data analysis, which match the solver's technical background.",
            "matched_skills": [
                "Python",
                "Data Analysis"
            ]
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
                    "You are a precise AI matchmaking engine. "
                    "Return only valid JSON and never invent "
                    "problem IDs or problem information."
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

    result = json.loads(content)

    ai_matches = result.get("matches", [])

    # Create a lookup of actual database problems
    problem_lookup = {
        problem["id"]: problem
        for problem in problems
    }

    valid_matches = []

    for match in ai_matches:

        problem_id = match.get("problem_id")

        # Ignore IDs that do not exist in our database
        if problem_id not in problem_lookup:
            continue

        actual_problem = problem_lookup[problem_id]

        valid_match = {
            "problem_id": problem_id,
            "title": actual_problem["title"],
            "problem": actual_problem["problem"],
            "problem_brief": actual_problem.get(
                "problem_brief", {}
            ),
            "domain": actual_problem.get(
                "domain", []
            ),
            "required_skills": actual_problem.get(
                "required_skills", []
            ),
            "match_score": match.get(
                "match_score", 0
            ),
            "match_reason": match.get(
                "match_reason",
                "This problem matches the solver's profile."
            ),
            "matched_skills": match.get(
                "matched_skills", []
            )
        }

        valid_matches.append(valid_match)

    # Limit to 5 matches
    return valid_matches[:5]