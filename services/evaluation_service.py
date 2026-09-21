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
        "GROQ_API_KEY was not found. Please check your .env file."
    )


client = Groq(
    api_key=GROQ_API_KEY
)


# ============================================================
# EVALUATE PROPOSALS
# ============================================================

def evaluate_proposals(
    problem_brief,
    proposals
):

    if not proposals:

        raise ValueError(
            "No solution proposals were submitted."
        )


    # --------------------------------------------------------
    # CONVERT DATA TO JSON
    # --------------------------------------------------------

    problem_text = json.dumps(
        problem_brief,
        indent=2
    )


    proposals_text = json.dumps(
        proposals,
        indent=2
    )


    # --------------------------------------------------------
    # AI PROMPT
    # --------------------------------------------------------

    prompt = f"""
You are SolveNet's AI Solution Evaluation Engine.

SolveNet has ONE real-world problem and multiple
independent solution proposals.

Your job is to evaluate EVERY submitted proposal
individually and then select EXACTLY ONE of those
submitted proposals.

IMPORTANT:

You are evaluating SOLUTION PROPOSALS.

You are NOT evaluating people.

You must NOT combine proposals.

You must NOT create a new solution.

You must NOT synthesize multiple proposals.

You must select ONE proposal exactly as submitted.

==================================================
ORIGINAL PROBLEM
==================================================

{problem_text}


==================================================
SUBMITTED PROPOSALS
==================================================

{proposals_text}


==================================================
EVALUATION CRITERIA
==================================================

Evaluate EVERY proposal using these six criteria:

1. Technical Feasibility
2. Expected Impact
3. Innovation
4. Scalability
5. Resource Requirements
6. Problem Alignment

Give every proposal an overall_score from 0 to 100.


==================================================
SELECTION RULE
==================================================

After evaluating EVERY proposal:

SELECT EXACTLY ONE submitted proposal.

The selected proposal MUST already exist in the
submitted proposals above.

Do NOT combine proposals.

Do NOT create a hybrid solution.

Do NOT modify a proposal.

Do NOT invent a new proposal.

Do NOT select multiple proposals.

Do NOT select multiple contributors.

The contributor associated with the selected proposal
is the selected contributor.

==================================================
REQUIRED JSON FORMAT
==================================================

Return ONLY valid JSON.

Use EXACTLY this structure:

{{
    "selected_person_id": "P001",

    "selection_reason":
        "Explain why this submitted proposal was selected.",

    "proposal_evaluations": [

        {{
            "person_id": "P001",

            "person_name": "Person name",

            "proposal_summary":
                "Short summary of this submitted proposal.",

            "technical_feasibility":
                "Evaluation of technical feasibility.",

            "expected_impact":
                "Evaluation of expected impact.",

            "innovation":
                "Evaluation of innovation.",

            "scalability":
                "Evaluation of scalability.",

            "resource_requirements":
                "Evaluation of resource requirements.",

            "problem_alignment":
                "Evaluation of alignment with the original problem.",

            "overall_score": 85,

            "strengths": [
                "Strength 1",
                "Strength 2"
            ],

            "limitations": [
                "Limitation 1",
                "Limitation 2"
            ],

            "overall_reasoning":
                "Overall evaluation of this proposal."
        }}
    ]
}}


==================================================
MANDATORY RULES
==================================================

1. Evaluate EVERY submitted proposal.

2. There must be exactly ONE evaluation for every
   submitted proposal.

3. Every evaluation MUST contain:

   person_id
   person_name
   proposal_summary
   technical_feasibility
   expected_impact
   innovation
   scalability
   resource_requirements
   problem_alignment
   overall_score
   strengths
   limitations
   overall_reasoning

4. overall_score must be between 0 and 100.

5. selected_person_id MUST match one of the submitted
   proposal person_id values.

6. The selected proposal MUST already exist in the
   submitted proposals.

7. Do NOT return an "evaluated_solution" object.

8. Do NOT return "contributing_proposals".

9. Do NOT return "synthesis_reasoning".

10. Do NOT combine proposals.

11. Do NOT create a new solution.

12. Do NOT evaluate contributors as people.

13. Select exactly ONE submitted proposal.

14. Return valid JSON only.

Before returning the answer, verify that:

selected_person_id

matches one of the submitted proposal person_id values.
"""


    # ========================================================
    # CALL GROQ
    # ========================================================

    response = client.chat.completions.create(

        model="openai/gpt-oss-120b",

        messages=[
            {
                "role": "system",
                "content": (
                    "You are SolveNet's AI Solution Evaluation "
                    "Engine. Evaluate every submitted proposal "
                    "and select exactly one submitted proposal. "
                    "Never combine proposals. Return valid "
                    "JSON only."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.1,

        response_format={
            "type": "json_object"
        }
    )


    # ========================================================
    # READ RESPONSE
    # ========================================================

    content = (
        response
        .choices[0]
        .message
        .content
    )


    print(
        "\n=========================================="
    )

    print(
        "NEW AI EVALUATION RESPONSE"
    )

    print(
        "=========================================="
    )

    print(content)

    print(
        "==========================================\n"
    )


    # ========================================================
    # PARSE JSON
    # ========================================================

    try:

        result = json.loads(
            content
        )

    except json.JSONDecodeError as error:

        raise ValueError(
            "AI returned invalid JSON."
        ) from error


    # ========================================================
    # GET EVALUATIONS
    # ========================================================

    evaluations = result.get(
        "proposal_evaluations",
        []
    )


    if not evaluations:

        raise ValueError(
            "AI did not return proposal evaluations."
        )


    # ========================================================
    # VERIFY ALL PROPOSALS WERE EVALUATED
    # ========================================================

    submitted_ids = {
        str(
            proposal.get(
                "person_id",
                ""
            )
        ).strip()

        for proposal in proposals
    }


    evaluated_ids = {
        str(
            item.get(
                "person_id",
                ""
            )
        ).strip()

        for item in evaluations
    }


    missing_ids = (
        submitted_ids - evaluated_ids
    )


    if missing_ids:

        raise ValueError(
            "AI did not evaluate every submitted proposal. "
            f"Missing: {missing_ids}"
        )


    # ========================================================
    # GET SELECTED PERSON ID
    # ========================================================

    selected_person_id = str(
        result.get(
            "selected_person_id",
            ""
        )
    ).strip()


    # ========================================================
    # FIND SELECTED PROPOSAL
    # ========================================================

    selected_proposal = None


    for proposal in proposals:

        proposal_id = str(
            proposal.get(
                "person_id",
                ""
            )
        ).strip()


        if proposal_id == selected_person_id:

            selected_proposal = proposal

            break


    # ========================================================
    # VERIFY SELECTION
    # ========================================================

    if not selected_proposal:

        raise ValueError(
            "AI did not select a valid submitted proposal."
        )


    # ========================================================
    # FIND SELECTED EVALUATION
    # ========================================================

    selected_evaluation = None


    for evaluation in evaluations:

        evaluation_id = str(
            evaluation.get(
                "person_id",
                ""
            )
        ).strip()


        if evaluation_id == selected_person_id:

            selected_evaluation = evaluation

            break


    if not selected_evaluation:

        raise ValueError(
            "Selected proposal does not have an evaluation."
        )


    # ========================================================
    # BUILD SELECTED SOLUTION
    # ========================================================
    #
    # IMPORTANT:
    #
    # Python takes the ORIGINAL proposal from the database.
    #
    # We do not allow the AI to invent or modify the
    # selected proposal.
    #
    # ========================================================

    selected_solution = {

        "person_id":
            selected_proposal.get(
                "person_id",
                ""
            ),

        "person_name":
            selected_proposal.get(
                "person_name",
                ""
            ),

        "proposal":
            selected_proposal.get(
                "proposal",
                ""
            ),

        "overall_score":
            selected_evaluation.get(
                "overall_score",
                0
            ),

        "technical_feasibility":
            selected_evaluation.get(
                "technical_feasibility",
                ""
            ),

        "expected_impact":
            selected_evaluation.get(
                "expected_impact",
                ""
            ),

        "innovation":
            selected_evaluation.get(
                "innovation",
                ""
            ),

        "scalability":
            selected_evaluation.get(
                "scalability",
                ""
            ),

        "resource_requirements":
            selected_evaluation.get(
                "resource_requirements",
                ""
            ),

        "problem_alignment":
            selected_evaluation.get(
                "problem_alignment",
                ""
            ),

        "selection_reason":
            result.get(
                "selection_reason",
                ""
            )
    }


    # ========================================================
    # FINAL RESULT
    # ========================================================

    final_result = {

        "selected_solution":
            selected_solution,

        "proposal_evaluations":
            evaluations,

        "selection_summary":
            result.get(
                "selection_reason",
                ""
            ),

        "recommended_next_step":
            (
                "Move the selected submitted solution "
                "from "
                + selected_proposal.get(
                    "person_name",
                    "the selected contributor"
                )
                + " to Stage 5."
            )
    }


    # ========================================================
    # PRINT FINAL RESULT
    # ========================================================

    print(
        "\n=========================================="
    )

    print(
        "FINAL SELECTED SOLUTION"
    )

    print(
        "=========================================="
    )

    print(
        "Contributor:",
        selected_solution["person_name"]
    )

    print(
        "Contributor ID:",
        selected_solution["person_id"]
    )

    print(
        "Overall Score:",
        selected_solution["overall_score"]
    )

    print(
        "Proposal:"
    )

    print(
        selected_solution["proposal"]
    )

    print(
        "==========================================\n"
    )


    return final_result