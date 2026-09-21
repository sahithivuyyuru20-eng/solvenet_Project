import sqlite3
import json
from pathlib import Path


# ============================================================
# DATABASE LOCATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_PATH = BASE_DIR / "solvenet.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def init_db():

    connection = get_connection()

    # --------------------------------------------------------
    # EXISTING DRAFTS TABLE
    # --------------------------------------------------------

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS drafts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            problem TEXT NOT NULL,
            problem_brief TEXT NOT NULL,
            matches TEXT NOT NULL,
            starter_kit TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # --------------------------------------------------------
    # EXISTING PROPOSALS TABLE
    # --------------------------------------------------------

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS proposals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            draft_id INTEGER NOT NULL,
            person_id TEXT NOT NULL,
            person_name TEXT NOT NULL,
            proposal TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # --------------------------------------------------------
    # EXISTING EVALUATIONS TABLE
    # --------------------------------------------------------

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            draft_id INTEGER NOT NULL,
            evaluation TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # --------------------------------------------------------
    # EXISTING MARKETPLACE SOLUTIONS TABLE
    # --------------------------------------------------------

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS solutions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            problem TEXT NOT NULL,
            problem_brief TEXT NOT NULL,
            matches TEXT NOT NULL,
            starter_kit TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # ========================================================
    # NEW: PROBLEMS TABLE
    # ========================================================

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS problems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT NOT NULL,

            problem TEXT NOT NULL,

            problem_brief TEXT NOT NULL,

            domain TEXT NOT NULL,

            required_skills TEXT NOT NULL,

            status TEXT DEFAULT 'OPEN',

            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # ========================================================
    # NEW: SOLVER PROFILES TABLE
    # ========================================================

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS solver_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            skills TEXT NOT NULL,

            interests TEXT NOT NULL,

            experience TEXT,

            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # ========================================================
    # NEW: SOLVER MATCHES TABLE
    # ========================================================

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS solver_matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            solver_id INTEGER NOT NULL,

            problem_id INTEGER NOT NULL,

            match_score INTEGER,

            match_reason TEXT,

            matched_skills TEXT,

            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # ========================================================
    # NEW: SOLVER PROPOSALS TABLE
    # ========================================================

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS solver_proposals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            problem_id INTEGER NOT NULL,

            solver_id INTEGER NOT NULL,

            solver_name TEXT NOT NULL,

            proposal TEXT NOT NULL,

            evaluation TEXT,

            decision TEXT,

            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # ========================================================
    # NEW: ASSIGNMENTS TABLE
    # ========================================================

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            problem_id INTEGER NOT NULL,

            solver_id INTEGER NOT NULL,

            proposal_id INTEGER NOT NULL,

            status TEXT DEFAULT 'ASSIGNED',

            assigned_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    connection.commit()

    connection.close()


# ============================================================
# DRAFT FUNCTIONS
# ============================================================

def create_draft(
    problem,
    problem_brief
):

    connection = get_connection()

    cursor = connection.execute(
        """
        INSERT INTO drafts
        (
            problem,
            problem_brief,
            matches
        )
        VALUES (?, ?, ?)
        """,
        (
            problem,
            json.dumps(problem_brief),
            json.dumps([])
        )
    )

    connection.commit()

    draft_id = cursor.lastrowid

    connection.close()

    return draft_id


def get_draft(draft_id):

    connection = get_connection()

    row = connection.execute(
        """
        SELECT *
        FROM drafts
        WHERE id = ?
        """,
        (draft_id,)
    ).fetchone()

    connection.close()

    if not row:

        return None

    draft = dict(row)

    # Problem brief
    try:

        draft["problem_brief"] = json.loads(
            draft["problem_brief"]
        )

    except Exception:

        draft["problem_brief"] = {}

    # Matches
    try:

        draft["matches"] = json.loads(
            draft["matches"]
        )

    except Exception:

        draft["matches"] = []

    # Starter kit
    if draft.get("starter_kit"):

        try:

            draft["starter_kit"] = json.loads(
                draft["starter_kit"]
            )

        except Exception:

            draft["starter_kit"] = None

    else:

        draft["starter_kit"] = None

    return draft


def update_draft_matches(
    draft_id,
    matches
):

    connection = get_connection()

    connection.execute(
        """
        UPDATE drafts
        SET matches = ?
        WHERE id = ?
        """,
        (
            json.dumps(matches),
            draft_id
        )
    )

    connection.commit()

    connection.close()


def update_draft_starter_kit(
    draft_id,
    starter_kit
):

    connection = get_connection()

    connection.execute(
        """
        UPDATE drafts
        SET starter_kit = ?
        WHERE id = ?
        """,
        (
            json.dumps(starter_kit),
            draft_id
        )
    )

    connection.commit()

    connection.close()


def delete_draft(draft_id):

    connection = get_connection()

    connection.execute(
        """
        DELETE FROM drafts
        WHERE id = ?
        """,
        (draft_id,)
    )

    connection.execute(
        """
        DELETE FROM proposals
        WHERE draft_id = ?
        """,
        (draft_id,)
    )

    connection.execute(
        """
        DELETE FROM evaluations
        WHERE draft_id = ?
        """,
        (draft_id,)
    )

    connection.commit()

    connection.close()


# ============================================================
# PROBLEM DATABASE
# ============================================================

def create_problem(
    title,
    problem,
    problem_brief
):

    connection = get_connection()

    domain = problem_brief.get(
        "domain",
        []
    )

    required_skills = problem_brief.get(
        "required_skills",
        []
    )

    cursor = connection.execute(
        """
        INSERT INTO problems
        (
            title,
            problem,
            problem_brief,
            domain,
            required_skills,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            title,
            problem,
            json.dumps(problem_brief),
            json.dumps(domain),
            json.dumps(required_skills),
            "OPEN"
        )
    )

    connection.commit()

    problem_id = cursor.lastrowid

    connection.close()

    return problem_id


def get_open_problems():

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT *
        FROM problems
        WHERE status = 'OPEN'
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    problems = []

    for row in rows:

        problem = dict(row)

        try:

            problem["problem_brief"] = json.loads(
                problem["problem_brief"]
            )

        except Exception:

            problem["problem_brief"] = {}

        try:

            problem["domain"] = json.loads(
                problem["domain"]
            )

        except Exception:

            problem["domain"] = []

        try:

            problem["required_skills"] = json.loads(
                problem["required_skills"]
            )

        except Exception:

            problem["required_skills"] = []

        problems.append(problem)

    return problems


def get_problem(problem_id):

    connection = get_connection()

    row = connection.execute(
        """
        SELECT *
        FROM problems
        WHERE id = ?
        """,
        (problem_id,)
    ).fetchone()

    connection.close()

    if not row:

        return None

    problem = dict(row)

    try:

        problem["problem_brief"] = json.loads(
            problem["problem_brief"]
        )

    except Exception:

        problem["problem_brief"] = {}

    try:

        problem["domain"] = json.loads(
            problem["domain"]
        )

    except Exception:

        problem["domain"] = []

    try:

        problem["required_skills"] = json.loads(
            problem["required_skills"]
        )

    except Exception:

        problem["required_skills"] = []

    return problem


def update_problem_status(
    problem_id,
    status
):

    connection = get_connection()

    connection.execute(
        """
        UPDATE problems
        SET status = ?
        WHERE id = ?
        """,
        (
            status,
            problem_id
        )
    )

    connection.commit()

    connection.close()


# ============================================================
# SOLVER PROFILE FUNCTIONS
# ============================================================

def create_solver_profile(
    name,
    skills,
    interests,
    experience
):

    connection = get_connection()

    cursor = connection.execute(
        """
        INSERT INTO solver_profiles
        (
            name,
            skills,
            interests,
            experience
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            name,
            json.dumps(skills),
            json.dumps(interests),
            experience
        )
    )

    connection.commit()

    solver_id = cursor.lastrowid

    connection.close()

    return solver_id


def get_solver_profile(
    solver_id
):

    connection = get_connection()

    row = connection.execute(
        """
        SELECT *
        FROM solver_profiles
        WHERE id = ?
        """,
        (solver_id,)
    ).fetchone()

    connection.close()

    if not row:

        return None

    solver = dict(row)

    try:

        solver["skills"] = json.loads(
            solver["skills"]
        )

    except Exception:

        solver["skills"] = []

    try:

        solver["interests"] = json.loads(
            solver["interests"]
        )

    except Exception:

        solver["interests"] = []

    return solver


# ============================================================
# SOLVER MATCH FUNCTIONS
# ============================================================

def save_solver_match(
    solver_id,
    problem_id,
    match_score,
    match_reason,
    matched_skills
):

    connection = get_connection()

    cursor = connection.execute(
        """
        INSERT INTO solver_matches
        (
            solver_id,
            problem_id,
            match_score,
            match_reason,
            matched_skills
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            solver_id,
            problem_id,
            match_score,
            match_reason,
            json.dumps(matched_skills)
        )
    )

    connection.commit()

    match_id = cursor.lastrowid

    connection.close()

    return match_id


# ============================================================
# SOLVER PROPOSAL FUNCTIONS
# ============================================================

def save_solver_proposal(
    problem_id,
    solver_id,
    solver_name,
    proposal
):

    connection = get_connection()

    cursor = connection.execute(
        """
        INSERT INTO solver_proposals
        (
            problem_id,
            solver_id,
            solver_name,
            proposal
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            problem_id,
            solver_id,
            solver_name,
            proposal
        )
    )

    connection.commit()

    proposal_id = cursor.lastrowid

    connection.close()

    return proposal_id


def get_solver_proposal(
    proposal_id
):

    connection = get_connection()

    row = connection.execute(
        """
        SELECT *
        FROM solver_proposals
        WHERE id = ?
        """,
        (proposal_id,)
    ).fetchone()

    connection.close()

    if not row:

        return None

    return dict(row)


def update_solver_proposal_evaluation(
    proposal_id,
    evaluation,
    decision
):

    connection = get_connection()

    connection.execute(
        """
        UPDATE solver_proposals
        SET evaluation = ?,
            decision = ?
        WHERE id = ?
        """,
        (
            json.dumps(evaluation),
            decision,
            proposal_id
        )
    )

    connection.commit()

    connection.close()


# ============================================================
# ASSIGNMENT FUNCTIONS
# ============================================================

def create_assignment(
    problem_id,
    solver_id,
    proposal_id
):

    connection = get_connection()

    cursor = connection.execute(
        """
        INSERT INTO assignments
        (
            problem_id,
            solver_id,
            proposal_id,
            status
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            problem_id,
            solver_id,
            proposal_id,
            "ASSIGNED"
        )
    )

    # Once a solver is assigned,
    # the problem is no longer OPEN.
    connection.execute(
        """
        UPDATE problems
        SET status = 'ASSIGNED'
        WHERE id = ?
        """,
        (problem_id,)
    )

    connection.commit()

    assignment_id = cursor.lastrowid

    connection.close()

    return assignment_id


def get_assignment(
    problem_id
):

    connection = get_connection()

    row = connection.execute(
        """
        SELECT *
        FROM assignments
        WHERE problem_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (problem_id,)
    ).fetchone()

    connection.close()

    if not row:

        return None

    return dict(row)


# ============================================================
# EXISTING PROPOSAL FUNCTIONS
# ============================================================

def save_proposal(
    draft_id,
    person_id,
    person_name,
    proposal
):

    connection = get_connection()

    existing = connection.execute(
        """
        SELECT id
        FROM proposals
        WHERE draft_id = ?
        AND person_id = ?
        """,
        (
            draft_id,
            person_id
        )
    ).fetchone()

    if existing:

        connection.execute(
            """
            UPDATE proposals
            SET proposal = ?
            WHERE id = ?
            """,
            (
                proposal,
                existing["id"]
            )
        )

        proposal_id = existing["id"]

    else:

        cursor = connection.execute(
            """
            INSERT INTO proposals
            (
                draft_id,
                person_id,
                person_name,
                proposal
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                draft_id,
                person_id,
                person_name,
                proposal
            )
        )

        proposal_id = cursor.lastrowid

    connection.commit()

    connection.close()

    return proposal_id


def get_proposals(
    draft_id
):

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT *
        FROM proposals
        WHERE draft_id = ?
        ORDER BY id ASC
        """,
        (draft_id,)
    ).fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]


# ============================================================
# EVALUATION FUNCTIONS
# ============================================================

def save_evaluation(
    draft_id,
    evaluation
):

    connection = get_connection()

    connection.execute(
        """
        DELETE FROM evaluations
        WHERE draft_id = ?
        """,
        (draft_id,)
    )

    cursor = connection.execute(
        """
        INSERT INTO evaluations
        (
            draft_id,
            evaluation
        )
        VALUES (?, ?)
        """,
        (
            draft_id,
            json.dumps(evaluation)
        )
    )

    connection.commit()

    evaluation_id = cursor.lastrowid

    connection.close()

    return evaluation_id


def get_evaluation(
    draft_id
):

    connection = get_connection()

    row = connection.execute(
        """
        SELECT *
        FROM evaluations
        WHERE draft_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (draft_id,)
    ).fetchone()

    connection.close()

    if not row:

        return None

    try:

        evaluation = json.loads(
            row["evaluation"]
        )

        print(
            "\n======================================"
        )

        print(
            "DATABASE EVALUATION"
        )

        print(
            "======================================"
        )

        print(
            json.dumps(
                evaluation,
                indent=2
            )
        )

        print(
            "======================================\n"
        )

        return evaluation

    except Exception as error:

        print(
            "ERROR READING EVALUATION:",
            error
        )

        return None


# ============================================================
# STARTER KIT FUNCTIONS
# ============================================================

# ============================================================
# MARKETPLACE FUNCTIONS
# ============================================================

def save_solution(
    title,
    problem,
    problem_brief,
    matches,
    starter_kit
):

    connection = get_connection()

    cursor = connection.execute(
        """
        INSERT INTO solutions
        (
            title,
            problem,
            problem_brief,
            matches,
            starter_kit
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            title,
            problem,
            json.dumps(problem_brief),
            json.dumps(matches),
            json.dumps(starter_kit)
        )
    )

    connection.commit()

    solution_id = cursor.lastrowid

    connection.close()

    return solution_id


def get_all_solutions():

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT
            id,
            title,
            problem,
            created_at,
            starter_kit,
            matches
        FROM solutions
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    solutions = []

    for row in rows:

        solution = dict(row)

        try:

            solution["starter_kit"] = json.loads(
                solution["starter_kit"]
            )

        except Exception:

            solution["starter_kit"] = {}

        try:

            solution["matches"] = json.loads(
                solution["matches"]
            )

        except Exception:

            solution["matches"] = []

        technologies = []

        technology_stack = solution[
            "starter_kit"
        ].get(
            "technology_stack",
            {}
        )

        for values in technology_stack.values():

            if isinstance(
                values,
                list
            ):

                technologies.extend(
                    values
                )

        solution["technologies"] = technologies[:8]

        solutions.append(
            solution
        )

    return solutions


def get_solution(
    solution_id
):

    connection = get_connection()

    row = connection.execute(
        """
        SELECT *
        FROM solutions
        WHERE id = ?
        """,
        (solution_id,)
    ).fetchone()

    connection.close()

    if not row:

        return None

    solution = dict(row)

    try:

        solution["problem_brief"] = json.loads(
            solution["problem_brief"]
        )

    except Exception:

        solution["problem_brief"] = {}

    try:

        solution["matches"] = json.loads(
            solution["matches"]
        )

    except Exception:

        solution["matches"] = []

    try:

        solution["starter_kit"] = json.loads(
            solution["starter_kit"]
        )

    except Exception:

        solution["starter_kit"] = {}

    return solution