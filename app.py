import os
import json

from dotenv import load_dotenv
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    session,
    redirect,
    url_for
)

from services.database_service import init_db
from services.problem_refiner import process_interview
from services.matching_service import find_matches
from services.evaluation_service import evaluate_proposals
from services.starter_kit_service import generate_starter_kit


load_dotenv()


app = Flask(__name__)

app.secret_key = os.getenv(
    "FLASK_SECRET_KEY",
    "solvenet-secret-key"
)


init_db()


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    return render_template(
        "login.html"
    )


# ============================================================
# PROBLEM RAISER
# ============================================================

@app.route("/intake")
def intake():

    return render_template(
        "intake.html"
    )


@app.route(
    "/analyze-problem",
    methods=["POST"]
)
def analyze_problem():

    data = request.get_json()

    if not data:

        return jsonify({
            "success": False,
            "message": "No problem data received."
        }), 400

    problem = data.get(
        "problem",
        ""
    ).strip()

    if not problem:

        return jsonify({
            "success": False,
            "message": "Please describe the problem."
        }), 400

    session["original_problem"] = problem

    return jsonify({
        "success": True,
        "message": "Problem received."
    })


# ============================================================
# START INTERVIEW
# ============================================================

@app.route(
    "/start-interview",
    methods=["POST"]
)
def start_interview():

    data = request.get_json()

    if not data:

        return jsonify({
            "success": False,
            "message": "No problem data received."
        }), 400

    problem = data.get(
        "problem",
        ""
    ).strip()

    if not problem:

        return jsonify({
            "success": False,
            "message": "Please describe the problem."
        }), 400

    session["original_problem"] = problem

    session["interview"] = []

    try:

        result = process_interview(
            problem,
            []
        )

        if result.get(
            "status"
        ) == "question":

            session["interview"].append({
                "role": "assistant",
                "content": result.get(
                    "question",
                    ""
                )
            })

        return jsonify({
            "success": True,
            "result": result
        })

    except Exception as error:

        print(
            "ERROR STARTING INTERVIEW:",
            error
        )

        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


# ============================================================
# INTERVIEW MESSAGE
# ============================================================

@app.route(
    "/interview-message",
    methods=["POST"]
)
def interview_message():

    data = request.get_json()

    if not data:

        return jsonify({
            "success": False,
            "message": "No message received."
        }), 400

    user_message = data.get(
        "message",
        ""
    ).strip()

    if not user_message:

        return jsonify({
            "success": False,
            "message": "Please enter a response."
        }), 400

    problem = session.get(
        "original_problem"
    )

    if not problem:

        return jsonify({
            "success": False,
            "message": "No active problem found."
        }), 400

    conversation = session.get(
        "interview",
        []
    )

    conversation.append({
        "role": "user",
        "content": user_message
    })

    try:

        result = process_interview(
            problem,
            conversation
        )

        if result.get(
            "status"
        ) == "question":

            conversation.append({
                "role": "assistant",
                "content": result.get(
                    "question",
                    ""
                )
            })

            session["interview"] = conversation

        elif result.get(
            "status"
        ) == "complete":

            session["problem_brief"] = result.get(
                "brief",
                {}
            )

            session["interview"] = conversation

        return jsonify({
            "success": True,
            "result": result
        })

    except Exception as error:

        print(
            "ERROR DURING INTERVIEW:",
            error
        )

        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


# ============================================================
# PUBLISH PROBLEM
# ============================================================

@app.route(
    "/publish-problem",
    methods=["POST"]
)
def publish_problem():

    data = request.get_json()

    if not data:

        return jsonify({
            "success": False,
            "message": "No problem data received."
        }), 400

    title = data.get(
        "title",
        ""
    ).strip()

    problem = data.get(
        "problem",
        ""
    ).strip()

    brief = data.get(
        "brief",
        {}
    )

    if not title:

        return jsonify({
            "success": False,
            "message": "Problem title is required."
        }), 400

    if not problem:

        return jsonify({
            "success": False,
            "message": "Problem description is required."
        }), 400

    try:

        from services.database_service import create_problem

        problem_id = create_problem(
            title=title,
            problem=problem,
            problem_brief=brief
        )

        session["published_problem_id"] = problem_id

        return jsonify({
            "success": True,
            "problem_id": problem_id,
            "message": "Problem published successfully."
        })

    except Exception as error:

        print(
            "ERROR PUBLISHING PROBLEM:",
            error
        )

        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


# ============================================================
# OLD MATCHES FLOW
# ============================================================

@app.route("/matches")
def matches():

    draft_id = session.get(
        "draft_id"
    )

    if not draft_id:

        return redirect(
            url_for("intake")
        )

    from services.database_service import get_draft

    draft = get_draft(
        draft_id
    )

    if not draft:

        return redirect(
            url_for("intake")
        )

    return render_template(
        "matches.html",
        draft=draft
    )


@app.route(
    "/find-matches",
    methods=["POST"]
)
def find_matches_route():

    data = request.get_json()

    if not data:

        return jsonify({
            "success": False,
            "message": "No data received."
        }), 400

    problem = data.get(
        "problem",
        ""
    ).strip()

    brief = data.get(
        "brief",
        {}
    )

    if not problem:

        return jsonify({
            "success": False,
            "message": "Problem is required."
        }), 400

    try:

        matches = find_matches(
            problem,
            brief
        )

        session["matches"] = matches

        return jsonify({
            "success": True,
            "matches": matches
        })

    except Exception as error:

        print(
            "ERROR FINDING MATCHES:",
            error
        )

        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


# ============================================================
# SOLVER PROFILE
# ============================================================

@app.route("/solve")
def solve():

    return render_template(
        "solve.html"
    )


@app.route(
    "/find-problems",
    methods=["POST"]
)
def find_problems():

    data = request.get_json()

    if not data:

        return jsonify({
            "success": False,
            "message": "No solver profile received."
        }), 400

    name = data.get(
        "name",
        ""
    ).strip()

    skills = data.get(
        "skills",
        []
    )

    interests = data.get(
        "interests",
        []
    )

    experience = data.get(
        "experience",
        ""
    ).strip()

    if not name:

        return jsonify({
            "success": False,
            "message": "Please enter your name."
        }), 400

    if not skills:

        return jsonify({
            "success": False,
            "message": "Please select at least one skill."
        }), 400

    if not interests:

        return jsonify({
            "success": False,
            "message": "Please select at least one interest."
        }), 400

    solver_profile = {
        "name": name,
        "skills": skills,
        "interests": interests,
        "experience": experience
    }

    session["solver_profile"] = solver_profile

    try:

        from services.solver_matching_service import (
            find_problem_matches
        )

        matches = find_problem_matches(
            solver_profile
        )

        session["solver_matches"] = matches

        return jsonify({
            "success": True,
            "matches": matches
        })

    except Exception as error:

        print(
            "ERROR FINDING SOLVER PROBLEMS:",
            error
        )

        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


# ============================================================
# MATCHED PROBLEMS
# ============================================================

@app.route("/matched-problems")
def matched_problems():

    solver_profile = session.get(
        "solver_profile"
    )

    matches = session.get(
        "solver_matches",
        []
    )

    if not solver_profile:

        return render_template(
            "solve.html"
        )

    return render_template(
        "matched_problems.html",
        solver_profile=solver_profile,
        matches=matches
    )


# ============================================================
# CHOOSE PROBLEM
# ============================================================

@app.route(
    "/choose-problem",
    methods=["POST"]
)
def choose_problem():

    data = request.get_json()

    if not data:

        return jsonify({
            "success": False,
            "message": "No problem selected."
        }), 400

    problem_id = data.get(
        "problem_id"
    )

    if not problem_id:

        return jsonify({
            "success": False,
            "message": "Problem ID is required."
        }), 400

    try:

        from services.database_service import get_problem

        problem = get_problem(
            int(problem_id)
        )

        if not problem:

            return jsonify({
                "success": False,
                "message": "Problem not found."
            }), 404

        session["selected_problem_id"] = int(
            problem_id
        )

        session["selected_problem"] = problem

        return jsonify({
            "success": True,
            "problem_id": int(problem_id)
        })

    except Exception as error:

        print(
            "ERROR CHOOSING PROBLEM:",
            error
        )

        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


# ============================================================
# SOLVER PROPOSAL PAGE
# ============================================================

@app.route("/solver-proposal")
def solver_proposal():

    problem = session.get(
        "selected_problem"
    )

    solver_profile = session.get(
        "solver_profile"
    )

    if not problem or not solver_profile:

        return redirect(
            url_for("matched_problems")
        )

    return render_template(
        "solver_proposal.html",
        problem=problem,
        solver_profile=solver_profile
    )


# ============================================================
# SUBMIT SOLVER PROPOSAL
# ============================================================

@app.route(
    "/submit-solver-proposal",
    methods=["POST"]
)
def submit_solver_proposal():

    data = request.get_json()

    if not data:

        return jsonify({
            "success": False,
            "message": "No proposal received."
        }), 400

    proposal = data.get(
        "proposal",
        ""
    ).strip()

    if not proposal:

        return jsonify({
            "success": False,
            "message": "Proposal cannot be empty."
        }), 400

    problem = session.get(
        "selected_problem"
    )

    solver_profile = session.get(
        "solver_profile"
    )

    if not problem:

        return jsonify({
            "success": False,
            "message": "No problem has been selected."
        }), 400

    if not solver_profile:

        return jsonify({
            "success": False,
            "message": "Solver profile not found."
        }), 400

    try:

        from services.database_service import (
            create_solver_profile,
            save_solver_proposal
        )

        solver_id = create_solver_profile(
            name=solver_profile["name"],
            skills=solver_profile["skills"],
            interests=solver_profile["interests"],
            experience=solver_profile["experience"]
        )

        proposal_id = save_solver_proposal(
            problem_id=problem["id"],
            solver_id=solver_id,
            solver_name=solver_profile["name"],
            proposal=proposal
        )

        session["solver_id"] = solver_id

        session["solver_proposal_id"] = proposal_id

        session["solver_proposal"] = proposal

        return jsonify({
            "success": True,
            "proposal_id": proposal_id
        })

    except Exception as error:

        print(
            "ERROR SAVING SOLVER PROPOSAL:",
            error
        )

        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


# ============================================================
# SOLVER EVALUATION PAGE
# ============================================================

@app.route("/solver-evaluation")
def solver_evaluation():

    problem = session.get(
        "selected_problem"
    )

    solver_profile = session.get(
        "solver_profile"
    )

    proposal = session.get(
        "solver_proposal"
    )

    if not problem or not solver_profile or not proposal:

        return redirect(
            url_for("matched_problems")
        )

    return render_template(
        "solver_evaluation.html",
        problem=problem,
        solver_profile=solver_profile,
        proposal=proposal
    )


# ============================================================
# EVALUATE SOLVER PROPOSAL
# ============================================================

@app.route(
    "/evaluate-solver-proposal",
    methods=["POST"]
)
def evaluate_solver_proposal_route():

    problem = session.get(
        "selected_problem"
    )

    solver_profile = session.get(
        "solver_profile"
    )

    proposal = session.get(
        "solver_proposal"
    )

    proposal_id = session.get(
        "solver_proposal_id"
    )

    solver_id = session.get(
        "solver_id"
    )

    if not problem:

        return jsonify({
            "success": False,
            "message": "No selected problem."
        }), 400

    if not solver_profile:

        return jsonify({
            "success": False,
            "message": "Solver profile not found."
        }), 400

    if not proposal:

        return jsonify({
            "success": False,
            "message": "No proposal found."
        }), 400

    if not proposal_id:

        return jsonify({
            "success": False,
            "message": "Proposal ID not found."
        }), 400

    if not solver_id:

        return jsonify({
            "success": False,
            "message": "Solver ID not found."
        }), 400

    try:

        from services.solver_evaluation_service import (
            evaluate_solver_proposal
        )

        from services.database_service import (
            update_solver_proposal_evaluation,
            create_assignment
        )

        result = evaluate_solver_proposal(
            problem,
            solver_profile,
            proposal
        )

        decision = result.get(
            "decision",
            "NOT PASS"
        ).upper()

        update_solver_proposal_evaluation(
            proposal_id,
            result,
            decision
        )

        print(
            "===================================="
        )

        print(
            "AI EVALUATION SAVED"
        )

        print(
            "Proposal ID:",
            proposal_id
        )

        print(
            "Decision:",
            decision
        )

        print(
            "Overall Score:",
            result.get(
                "overall_score"
            )
        )

        print(
            "===================================="
        )

        if decision == "PASS":

            assignment_id = create_assignment(
                problem_id=problem["id"],
                solver_id=solver_id,
                proposal_id=proposal_id
            )

            session["assignment_id"] = assignment_id

            session["solver_decision"] = "PASS"

            print(
                "ASSIGNMENT CREATED:",
                assignment_id
            )

        else:

            session["solver_decision"] = "NOT PASS"

        session["evaluation_completed"] = True

        return jsonify({
            "success": True,
            "evaluation": result
        })

    except Exception as error:

        print(
            "ERROR EVALUATING SOLVER PROPOSAL:",
            error
        )

        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


# ============================================================
# STARTER KIT PAGE
# ============================================================

@app.route("/starter-kit")
def starter_kit():

    from services.database_service import (
        get_solver_proposal,
        get_problem
    )

    proposal_id = session.get(
        "solver_proposal_id"
    )

    solver_id = session.get(
        "solver_id"
    )

    problem_id = session.get(
        "selected_problem_id"
    )

    decision = session.get(
        "solver_decision"
    )

    print(
        "===================================="
    )

    print(
        "STARTER KIT PAGE REQUESTED"
    )

    print(
        "proposal_id:",
        proposal_id
    )

    print(
        "solver_id:",
        solver_id
    )

    print(
        "problem_id:",
        problem_id
    )

    print(
        "decision:",
        decision
    )

    print(
        "===================================="
    )

    if not proposal_id:

        print(
            "No proposal ID found."
        )

        return redirect(
            url_for("solver_evaluation")
        )

    if not solver_id:

        print(
            "No solver ID found."
        )

        return redirect(
            url_for("solver_evaluation")
        )

    if not problem_id:

        print(
            "No problem ID found."
        )

        return redirect(
            url_for("solver_evaluation")
        )

    if decision != "PASS":

        print(
            "Solver proposal has not passed evaluation."
        )

        return redirect(
            url_for("solver_evaluation")
        )

    proposal_data = get_solver_proposal(
        proposal_id
    )

    problem = get_problem(
        problem_id
    )

    if not proposal_data:

        print(
            "Proposal not found."
        )

        return redirect(
            url_for("solver_evaluation")
        )

    if not problem:

        print(
            "Problem not found."
        )

        return redirect(
            url_for("solver_evaluation")
        )

    solver_profile = session.get(
        "solver_profile"
    )

    evaluation = None

    evaluation_text = proposal_data.get(
        "evaluation"
    )

    if evaluation_text:

        try:

            evaluation = json.loads(
                evaluation_text
            )

        except Exception as error:

            print(
                "ERROR READING EVALUATION:",
                error
            )

            evaluation = {}

    if not evaluation:

        print(
            "No solver evaluation found."
        )

        return redirect(
            url_for("solver_evaluation")
        )

    return render_template(
        "starter_kit.html",
        evaluation=evaluation,
        solver_evaluation=evaluation,
        problem=problem,
        solver_profile=solver_profile,
        proposal=proposal_data.get(
            "proposal",
            ""
        )
    )


# ============================================================
# GENERATE STARTER KIT
# ============================================================

@app.route(
    "/generate-starter-kit",
    methods=["POST"]
)
def generate_starter_kit_route():

    print(
        "===================================="
    )

    print(
        "GENERATE STARTER KIT REQUEST"
    )

    try:

        data = request.get_json(
            silent=True
        )

        if not data:

            print(
                "No JSON body received."
            )

            problem = session.get(
                "selected_problem"
            )

            solver_profile = session.get(
                "solver_profile"
            )

            solver_proposal = session.get(
                "solver_proposal"
            )

            solver_evaluation = None

            proposal_id = session.get(
                "solver_proposal_id"
            )

            if proposal_id:

                from services.database_service import (
                    get_solver_proposal
                )

                proposal_data = get_solver_proposal(
                    proposal_id
                )

                if proposal_data:

                    evaluation_text = proposal_data.get(
                        "evaluation"
                    )

                    if evaluation_text:

                        try:

                            solver_evaluation = json.loads(
                                evaluation_text
                            )

                        except Exception as error:

                            print(
                                "ERROR READING EVALUATION:",
                                error
                            )

            data = {
                "problem": problem,
                "solver_profile": solver_profile,
                "proposal": solver_proposal,
                "evaluation": solver_evaluation
            }

        matches = session.get(
            "solver_matches",
            []
        )

        print(
            "Starter Kit input:"
        )

        print(
            data
        )

        print(
            "Matches:"
        )

        print(
            matches
        )

        print(
            "===================================="
        )

        if not data.get(
            "problem"
        ):

            return jsonify({
                "success": False,
                "message": "Problem information is missing."
            }), 400

        if not data.get(
            "proposal"
        ):

            return jsonify({
                "success": False,
                "message": "Solution proposal is missing."
            }), 400

        result = generate_starter_kit(
            data,
            matches
        )

        session["starter_kit"] = result

        session.modified = True

        print(
            "===================================="
        )

        print(
            "STARTER KIT GENERATED SUCCESSFULLY"
        )

        print(
            result
        )

        print(
            "===================================="
        )

        return jsonify({
            "success": True,
            "starter_kit": result
        })

    except Exception as error:

        print(
            "===================================="
        )

        print(
            "ERROR GENERATING STARTER KIT:",
            error
        )

        print(
            "===================================="
        )

        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


# ============================================================
# OLD PROPOSAL FLOW
# ============================================================

@app.route("/proposals")
def proposals():

    draft_id = session.get(
        "draft_id"
    )

    if not draft_id:

        return redirect(
            url_for("intake")
        )

    from services.database_service import get_draft

    draft = get_draft(
        draft_id
    )

    if not draft:

        return redirect(
            url_for("intake")
        )

    return render_template(
        "proposals.html",
        draft=draft
    )


@app.route(
    "/submit-proposal",
    methods=["POST"]
)
def submit_proposal():

    data = request.get_json()

    if not data:

        return jsonify({
            "success": False,
            "message": "No proposal received."
        }), 400

    draft_id = data.get(
        "draft_id"
    )

    person_id = data.get(
        "person_id"
    )

    person_name = data.get(
        "person_name"
    )

    proposal = data.get(
        "proposal",
        ""
    ).strip()

    if not proposal:

        return jsonify({
            "success": False,
            "message": "Proposal cannot be empty."
        }), 400

    try:

        from services.database_service import save_proposal

        proposal_id = save_proposal(
            draft_id,
            person_id,
            person_name,
            proposal
        )

        return jsonify({
            "success": True,
            "proposal_id": proposal_id
        })

    except Exception as error:

        print(
            "ERROR SAVING PROPOSAL:",
            error
        )

        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


# ============================================================
# OLD EVALUATION FLOW
# ============================================================

@app.route("/evaluation")
def evaluation():

    draft_id = session.get(
        "draft_id"
    )

    if not draft_id:

        return redirect(
            url_for("intake")
        )

    from services.database_service import get_evaluation

    evaluation_data = get_evaluation(
        draft_id
    )

    return render_template(
        "evaluation.html",
        evaluation=evaluation_data
    )


@app.route(
    "/evaluate-proposals",
    methods=["POST"]
)
def evaluate_proposals_route():

    data = request.get_json()

    if not data:

        return jsonify({
            "success": False,
            "message": "No proposal data received."
        }), 400

    draft_id = data.get(
        "draft_id"
    )

    if not draft_id:

        return jsonify({
            "success": False,
            "message": "Draft ID is required."
        }), 400

    try:

        from services.database_service import (
            get_draft_proposals,
            save_evaluation
        )

        proposals = get_draft_proposals(
            draft_id
        )

        if not proposals:

            return jsonify({
                "success": False,
                "message": "No proposals found."
            }), 400

        result = evaluate_proposals(
            proposals
        )

        save_evaluation(
            draft_id,
            result
        )

        return jsonify({
            "success": True,
            "evaluation": result
        })

    except Exception as error:

        print(
            "ERROR EVALUATING PROPOSALS:",
            error
        )

        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


# ============================================================
# SAVE SOLUTION TO MARKETPLACE
# ============================================================

@app.route(
    "/save-solution",
    methods=["POST"]
)
def save_solution():

    data = request.get_json()

    if not data:

        return jsonify({
            "success": False,
            "message": "No solution data received."
        }), 400

    try:

        # IMPORTANT:
        # database_service.py already has save_solution().
        # We import it with a different name so that it does
        # not conflict with this Flask route function.

        from services.database_service import (
            save_solution as save_solution_to_db
        )

        solution_id = save_solution_to_db(
            title=data.get(
                "title",
                "Untitled Solution"
            ),
            problem=data.get(
                "problem",
                ""
            ),
            problem_brief=data.get(
                "problem_brief",
                {}
            ),
            matches=data.get(
                "matches",
                []
            ),
            starter_kit=data.get(
                "starter_kit",
                {}
            )
        )

        return jsonify({
            "success": True,
            "solution_id": solution_id,
            "message": "Solution saved to the SolveNet Marketplace."
        })

    except Exception as error:

        print(
            "ERROR SAVING SOLUTION:",
            error
        )

        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


# ============================================================
# MARKETPLACE
# ============================================================

@app.route("/marketplace")
def marketplace():

    from services.database_service import (
        get_all_solutions
    )

    solutions = get_all_solutions()

    return render_template(
        "marketplace.html",
        solutions=solutions
    )


# ============================================================
# SOLUTION DETAILS
# ============================================================

@app.route(
    "/solution/<int:solution_id>"
)
def solution_detail(
    solution_id
):

    from services.database_service import (
        get_solution
    )

    solution = get_solution(
        solution_id
    )

    if not solution:

        return redirect(
            url_for("marketplace")
        )

    return render_template(
        "solution_detail.html",
        solution=solution
    )


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )