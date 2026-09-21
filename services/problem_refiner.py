import json
import os

from dotenv import load_dotenv
from groq import Groq


# Load .env from the main project folder
BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_PATH)


# Get API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# Check API key
if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY was not found. "
        "Please check your .env file."
    )


# Create Groq client
client = Groq(
    api_key=GROQ_API_KEY
)


def process_interview(problem, conversation):

    conversation_text = ""

    for message in conversation:
        conversation_text += (
            f"{message['role'].upper()}: "
            f"{message['content']}\n"
        )

    prompt = f"""
You are SolveNet's AI Problem Refiner.

Your job is to interview a person who has a real-world
problem and turn their vague idea into a structured,
actionable project brief.

ORIGINAL PROBLEM:
{problem}

CONVERSATION SO FAR:
{conversation_text}

You need to understand these six areas:

1. Problem
2. People affected
3. Current approach
4. Available data/resources
5. Constraints
6. Desired outcome / success criteria

Rules:

- Ask ONE question at a time.
- Ask only questions that are still needed.
- Do not ask for information that the user already provided.
- If the user says they don't know something, accept that.
- Keep questions simple and conversational.
- Do not suggest a solution too early.
- Once enough information is available, finish the interview.
- Never invent facts that the user did not provide.

If more information is needed, return:

{{
    "status": "question",
    "question": "Your next question here"
}}

If enough information is available, return:

{{
    "status": "complete",
    "brief": {{
        "title": "...",
        "problem": "...",
        "affected_users": ["..."],
        "current_approach": "...",
        "available_data": ["..."],
        "constraints": ["..."],
        "desired_outcome": "...",
        "success_metrics": ["..."],
        "domain": ["..."],
        "assumptions": ["..."],
        "missing_information": ["..."]
    }}
}}

Return ONLY valid JSON.
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",

        messages=[
            {
                "role": "system",
                "content": (
                    "You are a careful problem-refinement "
                    "interview agent. Return only valid JSON."
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