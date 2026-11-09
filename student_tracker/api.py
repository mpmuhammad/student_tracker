"""Whitelisted endpoints used by the Mentor portal (frontend/, served at /mentor)."""

import html

import frappe
from frappe import _
from frappe.query_builder.functions import Count, Max
from frappe.utils import getdate, today, now_datetime, format_datetime
from student_tracker.permissions import MENTOR_ROLE, is_restricted_mentor

STUDENT_FIELDS = [
	"name",
	"name1",
	"photo",
	"house_name",
	"phone_number",
	"parent_name",
	"parent_contact_number",
	"school_name",
	"school_class",
	"madrassa_name",
	"madrassa_class",
	"mentor",
]


def _ensure_mentor():
	if frappe.session.user == "Guest":
		raise frappe.AuthenticationError(_("Please log in"))
	roles = frappe.get_roles()
	if MENTOR_ROLE not in roles:
		frappe.throw(_("Only users with the Mentor role can use this page"), frappe.PermissionError)


def _get_assigned_student(student: str) -> dict:
	"""Return the student if it is assigned to the current mentor, else raise."""
	filters = {"name": student}
	if is_restricted_mentor():
		filters["mentor"] = frappe.session.user
	row = frappe.db.get_value("Student", filters, STUDENT_FIELDS, as_dict=True)
	if not row:
		frappe.throw(_("Student {0} is not assigned to you").format(student), frappe.PermissionError)
	return row


@frappe.whitelist()
def get_session_info() -> dict:
	"""Logged-in user and whether they may use the mentor portal."""
	user = frappe.session.user
	if user == "Guest":
		return {"user": "Guest", "is_mentor": False}
	roles = frappe.get_roles(user)
	full_name, user_image = frappe.db.get_value("User", user, ["full_name", "user_image"])
	return {
		"user": user,
		"full_name": full_name or user,
		"user_image": user_image,
		"is_mentor": MENTOR_ROLE in roles,
	}


@frappe.whitelist()
def get_my_students() -> list[dict]:
	"""Students assigned to the logged-in mentor, with their latest activity date."""
	_ensure_mentor()
	filters = {"mentor": frappe.session.user} if is_restricted_mentor() else {}
	students = frappe.get_all("Student", filters=filters, fields=STUDENT_FIELDS, order_by="name1 asc")
	if not students:
		return students

	ActivityRecord = frappe.qb.DocType("Activity Record")
	stats = (
		frappe.qb.from_(ActivityRecord)
		.select(
			ActivityRecord.student,
			Count(ActivityRecord.name).as_("count"),
			Max(ActivityRecord.activity_date).as_("last_date"),
		)
		.where(ActivityRecord.student.isin([s.name for s in students]))
		.groupby(ActivityRecord.student)
		.run(as_dict=True)
	)
	by_student = {r.student: r for r in stats}
	for s in students:
		r = by_student.get(s.name)
		s.activity_count = r["count"] if r else 0
		s.last_activity_date = r["last_date"] if r else None

	# Fetch the latest goal for each student.
	goals = frappe.get_all(
		"Goal",
		filters={"student": ["in", [s.name for s in students]],"is_closed": 0,},
		fields=[
				"name",
				"student",
				"task_description",
				"status",
				"actual_percentage",
				"created_on",
				"creation",
			],
		order_by="creation desc",
		)

	latest_goals = {}
	for goal in goals:
		if goal.student not in latest_goals:
				latest_goals[goal.student] = goal

	for s in students:
		s.goal = latest_goals.get(s.name)

	return students


@frappe.whitelist()
def get_student(student: str) -> dict:
	_ensure_mentor()
	return _get_assigned_student(student)


@frappe.whitelist()
def get_activities(student: str) -> list[dict]:
	"""Previous activity notes of a student, newest first."""
	_ensure_mentor()
	_get_assigned_student(student)
	return frappe.get_all(
		"Activity Record",
		filters={"student": student},
		fields=["name", "activity_date", "activity_note", "owner", "creation"],
		order_by="activity_date desc, creation desc",
	)


@frappe.whitelist(methods=["POST"])
def add_activity(student: str, activity_note: str, activity_date: str | None = None) -> dict:
	"""Create an Activity Record for one of the mentor's students."""
	_ensure_mentor()
	_get_assigned_student(student)

	activity_note = (activity_note or "").strip()
	if not activity_note:
		frappe.throw(_("Activity note is required"))
	activity_date = activity_date or today()
	if getdate(activity_date) > getdate(today()):
		frappe.throw(_("Activity date cannot be in the future"))

	# Plain text from the portal -> simple HTML for the Text Editor field
	paragraphs = [p.strip() for p in activity_note.split("\n\n") if p.strip()]
	note_html = "".join(f"<p>{html.escape(p).replace(chr(10), '<br>')}</p>" for p in paragraphs)

	doc = frappe.get_doc(
		{
			"doctype": "Activity Record",
			"student": student,
			"activity_date": activity_date,
			"activity_note": note_html,
		}
	).insert()
	return doc.as_dict()

@frappe.whitelist()
def get_goal(student: str) -> dict | None:
    """Return the latest goal for one of the mentor's students."""
    _ensure_mentor()
    _get_assigned_student(student)

    goals = frappe.get_all(
        "Goal",
        filters={"student": student,"is_closed": 0,},
        fields=[
            "name",
            "student",
            "task_description",
            "status",
            "actual_percentage",
            "created_on",
            "closed_on", 
        ],
        order_by="creation desc",
        limit=1,
    )

    return goals[0] if goals else None

def _add_goal_activity(student: str, message: str) -> None:
    """Add an automatically generated goal event to Activity Notes."""
    note_html = f"<p>{html.escape(message)}</p>"

    frappe.get_doc({
        "doctype": "Activity Record",
        "student": student,
        "activity_date": today(),
        "activity_note": note_html,
    }).insert()


@frappe.whitelist(methods=["POST"])
def create_goal(student: str, task_description: str) -> dict:
    """Create a goal and record its start in the activity history."""
    _ensure_mentor()
    _get_assigned_student(student)

    task_description = (task_description or "").strip()

    if not task_description:
        frappe.throw(_("Task description is required"))

    doc = frappe.get_doc({
        "doctype": "Goal",
        "student": student,
        "task_description": task_description,
        "actual_percentage": 0,
        "is_closed": 0,
    }).insert()

    # Automatically add a goal-start message to Activity Notes.
    _add_goal_activity(
        student,
        f"Goal started: {task_description}.",
    )

    return doc.as_dict()


@frappe.whitelist(methods=["POST"])
def update_goal_progress(goal: str, actual_percentage: int) -> dict:
    """Update progress for a goal belonging to an assigned student."""
    _ensure_mentor()

    doc = frappe.get_doc("Goal", goal)
    _get_assigned_student(doc.student)

    try:
        percentage = int(actual_percentage)
    except (TypeError, ValueError):
        frappe.throw(_("Progress must be a number between 0 and 100"))

    if not 0 <= percentage <= 100:
        frappe.throw(_("Progress must be between 0 and 100"))

    doc.actual_percentage = percentage
    doc.save()

    return doc.as_dict()

@frappe.whitelist(methods=["POST"])
def close_goal(goal: str) -> dict:
    """Close a completed goal without deleting its record."""
    _ensure_mentor()

    doc = frappe.get_doc("Goal", goal)
    _get_assigned_student(doc.student)

    if (doc.actual_percentage or 0) < 100:
        frappe.throw(_("A goal can only be closed after reaching 100%."))

    if doc.is_closed:
        return doc.as_dict()

    completed_at = now_datetime()

    doc.is_closed = 1
    doc.closed_on = completed_at
    doc.save()

    completion_message = (
        f"Goal '{doc.task_description}' is completed on "
        f"{format_datetime(completed_at)}."
    )

    _add_goal_activity(doc.student, completion_message)

    return doc.as_dict()