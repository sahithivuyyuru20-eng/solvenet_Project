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
# SAMPLE SOLUTION COMMUNITY
# ============================================================
#
# These are demo profiles for the hackathon.
# Later this can be replaced with a database.
#

TALENT_CATALOG = [

    {
        "id": "P001",
        "name": "Aarav Sharma",
        "type": "Student",
        "skills": [
            "IoT",
            "Arduino",
            "ESP32",
            "Sensors",
            "Embedded Systems"
        ],
        "projects": [
            "Smart Traffic Monitoring System",
            "IoT-based Waste Bin"
        ],
        "courses": [
            "Internet of Things",
            "Embedded Systems"
        ],
        "research": [
            "Low-cost IoT sensing systems"
        ]
    },

    {
        "id": "P002",
        "name": "Meera Reddy",
        "type": "Student",
        "skills": [
            "Python",
            "Machine Learning",
            "Data Analysis",
            "Computer Vision"
        ],
        "projects": [
            "Road Damage Detection using Computer Vision",
            "Traffic Pattern Prediction"
        ],
        "courses": [
            "Machine Learning",
            "Data Science"
        ],
        "research": [
            "Computer vision for urban infrastructure"
        ]
    },

    {
        "id": "P003",
        "name": "Rahul Verma",
        "type": "Student",
        "skills": [
            "Web Development",
            "Flask",
            "React",
            "Python",
            "APIs"
        ],
        "projects": [
            "Citizen Complaint Portal",
            "Municipal Service Dashboard"
        ],
        "courses": [
            "Web Technologies",
            "Software Engineering"
        ],
        "research": [
            "Digital platforms for public services"
        ]
    },

    {
        "id": "P004",
        "name": "Ananya Rao",
        "type": "Researcher",
        "skills": [
            "GIS",
            "Geospatial Analysis",
            "Urban Planning",
            "Data Visualization"
        ],
        "projects": [
            "Urban Road Condition Mapping",
            "GIS-based City Planning"
        ],
        "courses": [
            "Geographic Information Systems",
            "Urban Analytics"
        ],
        "research": [
            "Geospatial methods for urban infrastructure"
        ]
    },

    {
        "id": "P005",
        "name": "Vikram Singh",
        "type": "Student",
        "skills": [
            "Mobile Development",
            "Flutter",
            "Firebase",
            "UI/UX"
        ],
        "projects": [
            "Community Reporting Mobile App",
            "Emergency Alert Application"
        ],
        "courses": [
            "Mobile Application Development",
            "Human Computer Interaction"
        ],
        "research": [
            "Mobile interfaces for community participation"
        ]
    },

    {
        "id": "P006",
        "name": "Ishita Nair",
        "type": "Researcher",
        "skills": [
            "Data Science",
            "Statistics",
            "Predictive Analytics",
            "Python"
        ],
        "projects": [
            "Urban Infrastructure Risk Prediction",
            "Public Service Analytics"
        ],
        "courses": [
            "Statistics",
            "Data Mining"
        ],
        "research": [
            "Predictive models for public infrastructure"
        ]
    },

    {
        "id": "P007",
        "name": "Karthik Kumar",
        "type": "Student",
        "skills": [
            "Blockchain",
            "Backend Development",
            "Python",
            "Databases"
        ],
        "projects": [
            "Transparent Public Grievance System",
            "Decentralized Records Platform"
        ],
        "courses": [
            "Blockchain Technology",
            "Database Systems"
        ],
        "research": [
            "Transparent digital governance systems"
        ]
    },

    {
        "id": "P008",
        "name": "Sneha Patel",
        "type": "Student",
        "skills": [
            "AI",
            "Natural Language Processing",
            "Python",
            "LLMs"
        ],
        "projects": [
            "AI Citizen Assistant",
            "Complaint Classification System"
        ],
        "courses": [
            "Artificial Intelligence",
            "Natural Language Processing"
        ],
        "research": [
            "AI-assisted public service systems"
        ]
    }

]


# ============================================================
# AI MATCHING ENGINE
# ============================================================

def find_matches(problem_brief):

    catalog_text = json.dumps(
        TALENT_CATALOG,
        indent=2
    )

    brief_text = json.dumps(
        problem_brief,
        indent=2
    )

    prompt = f"""
You are SolveNet's AI Matchmaking Engine.

Your task is to match a real-world problem with
people from a solution community.

PROBLEM BRIEF:

{brief_text}


AVAILABLE PEOPLE / PROJECTS:

{catalog_text}


MATCHING RULES:

1. Understand the actual problem.
2. Identify the technical and domain skills required.
3. Compare the problem with the skills, projects,
   courses and research of each person.
4. Select the 5 most relevant people.
5. Give every selected person a match score from 0 to 100.
6. Explain WHY the person matches.
7. Mention the specific skills or previous projects
   that make them relevant.
8. Identify what they could contribute.
9. Do not invent skills or projects.
10. Do not select someone simply because their name
    sounds relevant.
11. Prefer strong evidence from their existing profile.

Return ONLY valid JSON.

Required format:

{{
    "matches": [
        {{
            "id": "P001",
            "name": "Person name",
            "type": "Student or Researcher",
            "match_score": 92,
            "match_reason": "Why this person matches",
            "relevant_skills": [
                "skill 1",
                "skill 2"
            ],
            "relevant_projects": [
                "project 1"
            ],
            "potential_contribution": "What they could contribute"
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
                    "You are SolveNet's AI matchmaking engine. "
                    "Return only valid JSON."
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

    return result.get("matches", [])