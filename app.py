from flask import Flask, render_template, request, redirect, url_for, session
from models import (
    db,
    User,
    Subject,
    StudyPlan,
    Task,
    Note,
    Goal,
    Scripture,
    PrayerEntry,
    Reflection
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
from devotional_verses import load_kjv_verses
THEMES = {
    "anchor_classic": {
        "name": "Anchor Classic",
        "colors": ["#102a43", "#ffffff", "#c89b3c"]
    },
    "sage_garden": {
        "name": "Sage Garden",
        "colors": ["#647b64", "#f7f5ed", "#a3a66a"]
    },
    "lavender_haze": {
        "name": "Lavender Haze",
        "colors": ["#8275a8", "#ffffff", "#c7b8e8"]
    },
    "midnight": {
        "name": "Midnight",
        "colors": ["#171923", "#282c35", "#8d99ae"]
    },
    "rosewater": {
        "name": "Rosewater",
        "colors": ["#b76e79", "#fff8f5", "#e8b4b8"]
    },
    "terracotta": {
        "name": "Terracotta",
        "colors": ["#a44a35", "#fff4e8", "#d99b72"]
    },
    "ocean_breeze": {
        "name": "Ocean Breeze",
        "colors": ["#176b70", "#f4fbfa", "#8bcac3"]
    },
    "forest_canopy": {
        "name": "Forest Canopy",
        "colors": ["#285943", "#f6f5ed", "#a5b99a"]
    },
    "burgundy_luxe": {
        "name": "Burgundy Luxe",
        "colors": ["#702c3b", "#fff9f0", "#c6a15b"]
    },
    "skybound": {
        "name": "Skybound",
        "colors": ["#4386b5", "#f5faff", "#a9d5f2"]
    },
    "arctic_slate": {
        "name": "Arctic Slate",
        "colors": ["#475569", "#f8fafc", "#a5c4dc"]
    },
    "mocha_cream": {
        "name": "Mocha Cream",
        "colors": ["#604638", "#faf3e8", "#c49a6c"]
    }
}

app = Flask(__name__)

app.config["SECRET_KEY"] = "anchor-study-development-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///anchor.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


# Home page
@app.route("/")
def home():
    return render_template("index.html")


# User registration
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        university = request.form.get("university", "").strip()
        course = request.form.get("course", "").strip()
        year_of_study = request.form.get("year_of_study", "").strip()
        password = request.form.get("password", "")

        if not all([full_name, email, university, course, year_of_study, password]):
            return render_template(
                "signup.html",
                error="Please complete all required fields."
            )

        try:
            year_of_study = int(year_of_study)

            if year_of_study < 1:
                raise ValueError

        except ValueError:
            return render_template(
                "signup.html",
                error="Please enter a valid year of study."
            )

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return render_template(
                "signup.html",
                error="An account with this email already exists."
            )

        password_hash = generate_password_hash(password)

        new_user = User(
            full_name=full_name,
            email=email,
            university=university,
            course=course,
            year_of_study=year_of_study,
            password_hash=password_hash
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("signup.html")


# User login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            session.clear()
            session["user_id"] = user.id

            return redirect(url_for("dashboard"))

        return render_template(
            "login.html",
            error="Invalid email or password."
        )

    return render_template("login.html")


# Dashboard
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = db.session.get(User, session["user_id"])

    if not user:
        session.clear()
        return redirect(url_for("login"))

    return render_template("dashboard.html", user=user)


# Study planner
@app.route("/study", methods=["GET", "POST"])
def study():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = db.session.get(User, session["user_id"])

    if not user:
        session.clear()
        return redirect(url_for("login"))

    if request.method == "POST":
        action = request.form.get("action")

        if action == "add_subject":
            name = request.form.get("name", "").strip()
            code = request.form.get("code", "").strip()

            if name:
                new_subject = Subject(
                    name=name,
                    code=code,
                    user_id=user.id
                )

                db.session.add(new_subject)
                db.session.commit()

            return redirect(url_for("study"))

        if action == "add_plan":
            topic = request.form.get("topic", "").strip()
            subject_id = request.form.get("subject_id", "")
            study_date = request.form.get("study_date", "")
            duration = request.form.get("duration", "")

            subject = None

            if subject_id.isdigit():
                subject = Subject.query.filter_by(
                    id=int(subject_id),
                    user_id=user.id
                ).first()

            try:
                plan_date = datetime.strptime(
                    study_date,
                    "%Y-%m-%d"
                ).date()

                plan_duration = int(duration)

            except (ValueError, TypeError):
                return redirect(url_for("study"))

            if subject and topic and plan_duration > 0:
                new_plan = StudyPlan(
                    topic=topic,
                    subject_id=subject.id,
                    study_date=plan_date,
                    duration=plan_duration,
                    user_id=user.id
                )

                db.session.add(new_plan)
                db.session.commit()

            return redirect(url_for("study"))

    subjects = Subject.query.filter_by(
        user_id=user.id
    ).order_by(Subject.name.asc()).all()

    study_plans = StudyPlan.query.filter_by(
        user_id=user.id
    ).order_by(
        StudyPlan.study_date.asc(),
        StudyPlan.created_at.asc()
    ).all()

    today = date.today()

    total_plans = len(study_plans)

    completed_plans = sum(
        1 for plan in study_plans if plan.completed
    )

    progress = (
        round((completed_plans / total_plans) * 100)
        if total_plans > 0
        else 0
    )

    upcoming_plans = [
        plan for plan in study_plans
        if not plan.completed and plan.study_date >= today
    ]

    return render_template(
        "study.html",
        user=user,
        subjects=subjects,
        study_plans=study_plans,
        upcoming_plans=upcoming_plans,
        total_plans=total_plans,
        completed_plans=completed_plans,
        progress=progress,
        today=today
    )


# Mark a study plan as complete or incomplete
@app.route("/study/complete/<int:plan_id>", methods=["POST"])
def complete_study_plan(plan_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    plan = StudyPlan.query.filter_by(
        id=plan_id,
        user_id=session["user_id"]
    ).first()

    if plan:
        plan.completed = not plan.completed
        db.session.commit()

    return redirect(url_for("study"))


# Delete a subject
@app.route("/study/subject/delete/<int:subject_id>", methods=["POST"])
def delete_subject(subject_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    subject = Subject.query.filter_by(
        id=subject_id,
        user_id=session["user_id"]
    ).first()

    if subject:
        db.session.delete(subject)
        db.session.commit()

    return redirect(url_for("study"))


# Delete a study plan
@app.route("/study/delete/<int:plan_id>", methods=["POST"])
def delete_study_plan(plan_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    plan = StudyPlan.query.filter_by(
        id=plan_id,
        user_id=session["user_id"]
    ).first()

    if plan:
        db.session.delete(plan)
        db.session.commit()

    return redirect(url_for("study"))


# Focus timer
@app.route("/timer")
def timer():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = db.session.get(User, session["user_id"])

    if not user:
        session.clear()
        return redirect(url_for("login"))

    subjects = Subject.query.filter_by(
        user_id=user.id
    ).order_by(Subject.name.asc()).all()

    study_plans = StudyPlan.query.filter_by(
        user_id=user.id,
        completed=False
    ).order_by(
        StudyPlan.study_date.asc(),
        StudyPlan.created_at.asc()
    ).all()

    return render_template(
        "timer.html",
        user=user,
        subjects=subjects,
        study_plans=study_plans
    )


# Tasks
@app.route("/tasks", methods=["GET", "POST"])
def tasks():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = db.session.get(User, session["user_id"])

    if not user:
        session.clear()
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        due_date = request.form.get("due_date", "")
        priority = request.form.get("priority", "Medium")

        allowed_priorities = ["Low", "Medium", "High"]

        if priority not in allowed_priorities:
            priority = "Medium"

        if title:
            task_due_date = None

            if due_date:
                try:
                    task_due_date = datetime.strptime(
                        due_date,
                        "%Y-%m-%d"
                    ).date()
                except ValueError:
                    return redirect(url_for("tasks"))

            new_task = Task(
                title=title,
                description=description,
                due_date=task_due_date,
                priority=priority,
                user_id=user.id
            )

            db.session.add(new_task)
            db.session.commit()

        return redirect(url_for("tasks"))

    task_list = Task.query.filter_by(
        user_id=user.id
    ).order_by(
        Task.completed.asc(),
        Task.due_date.asc(),
        Task.created_at.desc()
    ).all()

    completed_tasks = sum(
        1 for task in task_list if task.completed
    )

    total_tasks = len(task_list)

    task_progress = (
        round((completed_tasks / total_tasks) * 100)
        if total_tasks > 0
        else 0
    )

    return render_template(
        "tasks.html",
        user=user,
        tasks=task_list,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        task_progress=task_progress
    )


# Toggle task completion
@app.route("/tasks/complete/<int:task_id>", methods=["POST"])
def complete_task(task_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    task = Task.query.filter_by(
        id=task_id,
        user_id=session["user_id"]
    ).first()

    if task:
        task.completed = not task.completed
        db.session.commit()

    return redirect(url_for("tasks"))


# Delete a task
@app.route("/tasks/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    task = Task.query.filter_by(
        id=task_id,
        user_id=session["user_id"]
    ).first()

    if task:
        db.session.delete(task)
        db.session.commit()

    return redirect(url_for("tasks"))


# Notes
@app.route("/notes", methods=["GET", "POST"])
def notes():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = db.session.get(User, session["user_id"])

    if not user:
        session.clear()
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        subject_id = request.form.get("subject_id", "")

        if title and content:
            selected_subject = None

            if subject_id.isdigit():
                selected_subject = Subject.query.filter_by(
                    id=int(subject_id),
                    user_id=user.id
                ).first()

            new_note = Note(
                title=title,
                content=content,
                subject_id=(
                    selected_subject.id
                    if selected_subject
                    else None
                ),
                user_id=user.id
            )

            db.session.add(new_note)
            db.session.commit()

        return redirect(url_for("notes"))

    subjects = Subject.query.filter_by(
        user_id=user.id
    ).order_by(Subject.name.asc()).all()

    note_list = Note.query.filter_by(
        user_id=user.id
    ).order_by(Note.created_at.desc()).all()

    return render_template(
        "notes.html",
        user=user,
        subjects=subjects,
        notes=note_list
    )


# Delete a note
@app.route("/notes/delete/<int:note_id>", methods=["POST"])
def delete_note(note_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    note = Note.query.filter_by(
        id=note_id,
        user_id=session["user_id"]
    ).first()

    if note:
        db.session.delete(note)
        db.session.commit()

    return redirect(url_for("notes"))


# Goals
@app.route("/goals", methods=["GET", "POST"])
def goals():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = db.session.get(User, session["user_id"])

    if not user:
        session.clear()
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        target_date = request.form.get("target_date", "")
        progress = request.form.get("progress", "0")

        if title:
            goal_date = None

            if target_date:
                try:
                    goal_date = datetime.strptime(
                        target_date,
                        "%Y-%m-%d"
                    ).date()
                except ValueError:
                    return redirect(url_for("goals"))

            try:
                goal_progress = int(progress)
            except (ValueError, TypeError):
                goal_progress = 0

            goal_progress = max(0, min(100, goal_progress))

            new_goal = Goal(
                title=title,
                description=description,
                target_date=goal_date,
                progress=goal_progress,
                completed=goal_progress == 100,
                user_id=user.id
            )

            db.session.add(new_goal)
            db.session.commit()

        return redirect(url_for("goals"))

    goal_list = Goal.query.filter_by(
        user_id=user.id
    ).order_by(
        Goal.completed.asc(),
        Goal.target_date.asc(),
        Goal.created_at.desc()
    ).all()

    return render_template(
        "goals.html",
        user=user,
        goals=goal_list
    )


# Update goal progress
@app.route("/goals/update/<int:goal_id>", methods=["POST"])
def update_goal(goal_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    goal = Goal.query.filter_by(
        id=goal_id,
        user_id=session["user_id"]
    ).first()

    if goal:
        progress = request.form.get("progress", "0")

        try:
            goal.progress = int(progress)
        except (ValueError, TypeError):
            goal.progress = 0

        goal.progress = max(0, min(100, goal.progress))
        goal.completed = goal.progress == 100

        db.session.commit()

    return redirect(url_for("goals"))


# Delete a goal
@app.route("/goals/delete/<int:goal_id>", methods=["POST"])
def delete_goal(goal_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    goal = Goal.query.filter_by(
        id=goal_id,
        user_id=session["user_id"]
    ).first()

    if goal:
        db.session.delete(goal)
        db.session.commit()

    return redirect(url_for("goals"))


# Scripture collection
@app.route("/scripture", methods=["GET", "POST"])
def scripture():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = db.session.get(User, session["user_id"])

    if not user:
        session.clear()
        return redirect(url_for("login"))

    if request.method == "POST":
        reference = request.form.get("reference", "").strip()
        verse_text = request.form.get("verse_text", "").strip()
        reflection = request.form.get("reflection", "").strip()

        if reference and verse_text:
            new_scripture = Scripture(
                reference=reference,
                verse_text=verse_text,
                reflection=reflection,
                user_id=user.id
            )

            db.session.add(new_scripture)
            db.session.commit()

        return redirect(url_for("scripture"))

    scriptures = Scripture.query.filter_by(
        user_id=user.id
    ).order_by(
        Scripture.favorite.desc(),
        Scripture.created_at.desc()
    ).all()

    return render_template(
        "scripture.html",
        user=user,
        scriptures=scriptures
    )


# Toggle a saved scripture as a favorite
@app.route("/scripture/favorite/<int:scripture_id>", methods=["POST"])
def favorite_scripture(scripture_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    scripture_entry = Scripture.query.filter_by(
        id=scripture_id,
        user_id=session["user_id"]
    ).first()

    if scripture_entry:
        scripture_entry.favorite = not scripture_entry.favorite
        db.session.commit()

    return redirect(url_for("scripture"))


# Delete a saved scripture
@app.route("/scripture/delete/<int:scripture_id>", methods=["POST"])
def delete_scripture(scripture_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    scripture_entry = Scripture.query.filter_by(
        id=scripture_id,
        user_id=session["user_id"]
    ).first()

    if scripture_entry:
        db.session.delete(scripture_entry)
        db.session.commit()

    return redirect(url_for("scripture"))


# Prayer journal
@app.route("/prayer-journal", methods=["GET", "POST"])
def prayer_journal():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = db.session.get(User, session["user_id"])

    if not user:
        session.clear()
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        category = request.form.get("category", "Personal")

        if title and content:
            new_prayer = PrayerEntry(
                title=title,
                content=content,
                category=category,
                user_id=user.id
            )

            db.session.add(new_prayer)
            db.session.commit()

        return redirect(url_for("prayer_journal"))

    prayer_list = PrayerEntry.query.filter_by(
        user_id=user.id
    ).order_by(
        PrayerEntry.answered.asc(),
        PrayerEntry.created_at.desc()
    ).all()

    total_prayers = len(prayer_list)

    answered_prayers = sum(
        1 for prayer in prayer_list if prayer.answered
    )

    return render_template(
        "prayer_journal.html",
        user=user,
        prayers=prayer_list,
        total_prayers=total_prayers,
        answered_prayers=answered_prayers
    )


# Mark a prayer as answered or unanswered
@app.route("/prayer-journal/answered/<int:prayer_id>", methods=["POST"])
def mark_prayer_answered(prayer_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    prayer = PrayerEntry.query.filter_by(
        id=prayer_id,
        user_id=session["user_id"]
    ).first()

    if prayer:
        prayer.answered = not prayer.answered
        db.session.commit()

    return redirect(url_for("prayer_journal"))


# Delete a prayer entry
@app.route("/prayer-journal/delete/<int:prayer_id>", methods=["POST"])
def delete_prayer(prayer_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    prayer = PrayerEntry.query.filter_by(
        id=prayer_id,
        user_id=session["user_id"]
    ).first()

    if prayer:
        db.session.delete(prayer)
        db.session.commit()

    return redirect(url_for("prayer_journal"))


# Devotionals
@app.route("/devotionals")
def devotionals():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = db.session.get(User, session["user_id"])

    if not user:
        session.clear()
        return redirect(url_for("login"))

    all_verses = load_kjv_verses()

    topics = {
        "Faith": "faith",
        "Hope": "hope",
        "Peace": "peace",
        "Wisdom": "wisdom",
        "Strength": "strength",
        "Prayer": "pray",
        "Love": "love",
        "Guidance": "guide"
    }

    today = date.today()

    verse_of_day = None

    if all_verses:
        daily_index = today.toordinal() % len(all_verses)
        verse_of_day = all_verses[daily_index].copy()

        verse_of_day["reflection"] = (
            "Take a moment to consider what this verse reveals about God "
            "and how you can apply its message to your life today."
        )

        verse_of_day["prayer"] = (
            "Heavenly Father, help me understand Your Word and live out "
            "its truth today. Guide my thoughts, words and actions. Amen."
        )

    search_term = request.args.get("q", "").strip()
    selected_topic = request.args.get("topic", "All")

    if selected_topic not in topics:
        selected_topic = "All"

    filtered_verses = all_verses

    if selected_topic != "All":
        keyword = topics[selected_topic].lower()

        filtered_verses = [
            verse for verse in filtered_verses
            if keyword in verse["text"].lower()
        ]

    if search_term:
        search_lower = search_term.lower()

        filtered_verses = [
            verse for verse in filtered_verses
            if search_lower in verse["text"].lower()
            or search_lower in verse["reference"].lower()
        ]

    total_results = len(filtered_verses)
    displayed_verses = filtered_verses[:100]

    return render_template(
        "devotionals.html",
        user=user,
        verse_of_day=verse_of_day,
        verses=displayed_verses,
        topics=list(topics.keys()),
        selected_topic=selected_topic,
        search_term=search_term,
        total_results=total_results,
        today=today
    )


# Save a verse from the devotional page to My Scriptures
@app.route("/devotionals/save", methods=["POST"])
def save_devotional_verse():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = db.session.get(User, session["user_id"])

    if not user:
        session.clear()
        return redirect(url_for("login"))

    reference = request.form.get("reference", "").strip()
    verse_text = request.form.get("verse_text", "").strip()

    if not reference or not verse_text:
        return redirect(url_for("devotionals"))

    existing_verse = Scripture.query.filter_by(
        user_id=user.id,
        reference=reference
    ).first()

    if not existing_verse:
        new_scripture = Scripture(
            reference=reference,
            verse_text=verse_text,
            reflection="",
            user_id=user.id
        )

        db.session.add(new_scripture)
        db.session.commit()

    return redirect(url_for("scripture"))


# Reflections page
@app.route("/reflections", methods=["GET"])
def reflections():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = db.session.get(User, session["user_id"])

    if not user:
        session.clear()
        return redirect(url_for("login"))

    reflection_entries = Reflection.query.filter_by(
        user_id=user.id
    ).order_by(
        Reflection.created_at.desc()
    ).all()

    prompts = [
        {
            "category": "Personal growth",
            "question": "What have I learned about myself recently?"
        },
        {
            "category": "Student life",
            "question": "What challenged me in my studies, and how did I respond?"
        },
        {
            "category": "Gratitude",
            "question": "What is one thing I am grateful for today?"
        },
        {
            "category": "Looking forward",
            "question": "What is one thing I want to do differently tomorrow?"
        },
        {
            "category": "Faith",
            "question": "What do I feel God is teaching me in this season?"
        }
    ]

    return render_template(
        "reflections.html",
        user=user,
        reflections=reflection_entries,
        prompts=prompts
    )


# Save a reflection
@app.route("/reflections/save", methods=["POST"])
def save_reflection():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = db.session.get(User, session["user_id"])

    if not user:
        session.clear()
        return redirect(url_for("login"))

    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()
    prompt = request.form.get("prompt", "").strip()

    if not title or not content:
        return redirect(url_for("reflections"))

    entry = Reflection(
        title=title,
        content=content,
        prompt=prompt or None,
        user_id=user.id
    )

    db.session.add(entry)
    db.session.commit()

    return redirect(url_for("reflections"))


# Edit a reflection
@app.route("/reflections/edit/<int:reflection_id>", methods=["POST"])
def edit_reflection(reflection_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = db.session.get(User, session["user_id"])

    if not user:
        session.clear()
        return redirect(url_for("login"))

    entry = Reflection.query.filter_by(
        id=reflection_id,
        user_id=user.id
    ).first_or_404()

    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()
    prompt = request.form.get("prompt", "").strip()

    if not title or not content:
        return redirect(url_for("reflections"))

    entry.title = title
    entry.content = content
    entry.prompt = prompt or None

    db.session.commit()

    return redirect(url_for("reflections"))


# Delete a reflection
@app.route("/reflections/delete/<int:reflection_id>", methods=["POST"])
def delete_reflection(reflection_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = db.session.get(User, session["user_id"])

    if not user:
        session.clear()
        return redirect(url_for("login"))

    entry = Reflection.query.filter_by(
        id=reflection_id,
        user_id=user.id
    ).first_or_404()

    db.session.delete(entry)
    db.session.commit()

    return redirect(url_for("reflections"))


# Profile
@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = db.session.get(User, session["user_id"])

    if not user:
        session.clear()
        return redirect(url_for("login"))

    return render_template("profile.html", user=user)


# Settings
@app.route("/settings", methods=["GET", "POST"])
def settings():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = db.session.get(User, session["user_id"])

    if not user:
        session.clear()
        return redirect(url_for("login"))

    if request.method == "POST":
        selected_theme = request.form.get(
            "theme",
            user.theme or "anchor_classic"
        )

        selected_doodle_style = request.form.get(
            "doodle_style",
            user.doodle_style or "off"
        )

        if selected_theme not in THEMES:
            selected_theme = user.theme or "anchor_classic"

        if selected_doodle_style not in ["off", "subtle", "playful"]:
            selected_doodle_style = user.doodle_style or "off"

        user.theme = selected_theme
        user.doodle_style = selected_doodle_style

        db.session.commit()

        return redirect(url_for("settings"))

    return render_template(
        "settings.html",
        user=user,
        themes=THEMES
    )
# Log out
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# Create database tables and run the application
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)