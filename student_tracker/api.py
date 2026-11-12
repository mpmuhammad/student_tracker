
"""Whitelisted endpoints used by the Mentor portal (frontend/, served at /mentor)."""

import html

import frappe
from frappe import _
from frappe.query_builder.functions import Count, Max
from frappe.utils import getdate, today, now_datetime , format_datetime

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
        frappe.throw(
            _("Only users with the Mentor role can use this page"),
            frappe.PermissionError,
        )


def _get_assigned_student(student: str) -> dict:
    """Return the student if it is assigned to the current mentor, else raise."""
    filters = {"name": student}

    if is_restricted_mentor():
        filters["mentor"] = frappe.session.user

    row = frappe.db.get_value(
        "Student",
        filters,
        STUDENT_FIELDS,
        as_dict=True,
    )

    if not row:
        frappe.throw(
            _("Student {0} is not assigned to you").format(student),
            frappe.PermissionError,
        )

    return row


@frappe.whitelist()
def get_session_info() -> dict:
    """Logged-in user and whether they may use the mentor portal."""
    user = frappe.session.user

    if user == "Guest":
        return {"user": "Guest", "is_mentor": False}

    roles = frappe.get_roles(user)
    full_name, user_image = frappe.db.get_value(
        "User",
        user,
        ["full_name", "user_image"],
    )

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

    filters = (
        {"mentor": frappe.session.user}
        if is_restricted_mentor()
        else {}
    )

    students = frappe.get_all(
        "Student",
        filters=filters,
        fields=STUDENT_FIELDS,
        order_by="creation desc",
    )

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
        .where(
            ActivityRecord.student.isin([s.name for s in students])
        )
        .groupby(ActivityRecord.student)
        .run(as_dict=True)
    )

    by_student = {r.student: r for r in stats}

    for s in students:
        r = by_student.get(s.name)
        s.activity_count = r["count"] if r else 0
        s.last_activity_date = r["last_date"] if r else None

    # Fetch the latest goal for each student, including completed goals.
    goals = frappe.get_all(
        "Goal",
        filters={
            "student": ["in", [s.name for s in students]],
        },
        fields=[
            "name",
            "student",
            "task_description",
            "goal_term",
            "status",
            "actual_percentage",
            "created_on",
            "closed_on",
            "is_closed",
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
        fields=[
            "name",
            "activity_date",
            "activity_note",
            "owner",
            "creation",
        ],
        order_by="activity_date desc, creation desc",
    )


@frappe.whitelist(methods=["POST"])
def add_activity(
    student: str,
    activity_note: str,
    activity_date: str | None = None,
) -> dict:
    """Create an Activity Record for one of the mentor's students."""
    _ensure_mentor()
    _get_assigned_student(student)

    activity_note = (activity_note or "").strip()

    if not activity_note:
        frappe.throw(_("Activity note is required"))

    activity_date = activity_date or today()

    if getdate(activity_date) > getdate(today()):
        frappe.throw(_("Activity date cannot be in the future"))

    # Plain text from the portal -> simple HTML for the Text Editor field.
    paragraphs = [
        p.strip()
        for p in activity_note.split("\n\n")
        if p.strip()
    ]

    note_html = "".join(
        f"<p>{html.escape(p).replace(chr(10), '<br>')}</p>"
        for p in paragraphs
    )

    doc = frappe.get_doc({
        "doctype": "Activity Record",
        "student": student,
        "activity_date": activity_date,
        "activity_note": note_html,
    }).insert()

    return doc.as_dict()



@frappe.whitelist(methods=["POST"])
def create_student(
    name1: str,
    house_name: str = "",
    phone_number: str = "",
    parent_name: str = "",
    parent_contact_number: str = "",
    school_name: str = "",
    school_class: str = "",
    madrassa_name: str = "",
    madrassa_class: str = "",
    photo: str = "",
) -> dict:
    """Create a student assigned automatically to the logged-in mentor."""

    _ensure_mentor()

    name1 = (name1 or "").strip()
    photo = (photo or "").strip()

    if not name1:
        frappe.throw(_("Student name is required"))

    # Verify that the supplied photo belongs to an uploaded File record.
    if photo and not frappe.db.exists("File", {"file_url": photo}):
        frappe.throw(_("Invalid student photo"))

    doc = frappe.get_doc({
        "doctype": "Student",
        "name1": name1,
        "house_name": (house_name or "").strip(),
        "phone_number": (phone_number or "").strip(),
        "parent_name": (parent_name or "").strip(),
        "parent_contact_number": (parent_contact_number or "").strip(),
        "school_name": (school_name or "").strip(),
        "school_class": (school_class or "").strip(),
        "madrassa_name": (madrassa_name or "").strip(),
        "madrassa_class": (madrassa_class or "").strip(),
        "photo": photo,

        # Always assign the currently logged-in mentor.
        "mentor": frappe.session.user,
    })

    # Mentor users have read-only DocType permissions.
    # Ownership is enforced above, so insertion is performed
    # through this restricted, validated endpoint.
    doc.insert(ignore_permissions=True)

    return doc.as_dict()



@frappe.whitelist()
def get_goal(student: str) -> dict | None:
    """Return the latest goal for one of the mentor's students, including completed goals."""
    _ensure_mentor()
    _get_assigned_student(student)

    goals = frappe.get_all(
        "Goal",
        filters={"student": student},
        fields=[
            "name",
            "student",
            "task_description",
            "goal_term",
            "status",
            "actual_percentage",
            "created_on",
            "closed_on",
            "is_closed",
        ],
        order_by="creation desc",
        limit=1,
    )

    return goals[0] if goals else None


@frappe.whitelist()
def get_goal_history(student: str) -> list[dict]:
    """Return the complete goal history for an assigned student."""
    _ensure_mentor()
    _get_assigned_student(student)

    # Collect every field defined in the Goal DocType.
    meta = frappe.get_meta("Goal")

    excluded_fieldtypes = {
        "Section Break",
        "Column Break",
        "Tab Break",
        "Table",
        "Table MultiSelect",
        "HTML",
        "Button",
        "Fold",
    }

    fields = ["name"]

    for df in meta.fields:
        if (
            df.fieldname
            and df.fieldname != "name"
            and df.fieldtype not in excluded_fieldtypes
        ):
            fields.append(df.fieldname)

    # Include standard Frappe record metadata.
    fields.extend([
        "owner",
        "creation",
        "modified",
        "modified_by",
    ])

    # Remove duplicate field names.
    fields = list(dict.fromkeys(fields))


    goals = frappe.get_all(
        "Goal",
        filters={"student": student},
        fields=fields,
        order_by="creation desc",
    )

    for goal in goals:
        if goal.get("created_on"):
            goal["created_on"] = format_datetime(
                goal["created_on"], "dd MMM yyyy, hh:mm a"
            )

        if goal.get("closed_on"):
            goal["closed_on"] = format_datetime(
                goal["closed_on"], "dd MMM yyyy, hh:mm a"
            )

    return goals


@frappe.whitelist(methods=["POST"])
def create_goal(
    student: str,
    task_description: str,
    goal_term: str = "Short Term",
) -> dict:
    """Create a goal without adding an Activity Record."""
    _ensure_mentor()
    _get_assigned_student(student)

    task_description = (task_description or "").strip()

    if not task_description:
        frappe.throw(_("Task description is required"))

    if goal_term not in ("Short Term", "Long Term"):
        frappe.throw(_("Please select a valid goal term"))

    doc = frappe.get_doc({
        "doctype": "Goal",
        "student": student,
        "task_description": task_description,
        "goal_term": goal_term,
        "actual_percentage": 0,
        "is_closed": 0,
    }).insert()

    return doc.as_dict()


@frappe.whitelist(methods=["POST"])
def update_goal_progress(
    goal: str,
    actual_percentage: int,
) -> dict:
    """
    Update goal progress.

    Automatically close the goal when progress reaches 100%.
    Record the completion date in the Goal DocType.
    """
    _ensure_mentor()

    doc = frappe.get_doc("Goal", goal)
    _get_assigned_student(doc.student)

    try:
        percentage = int(actual_percentage)
    except (TypeError, ValueError):
        frappe.throw(_("Progress must be a number between 0 and 100"))

    if not 0 <= percentage <= 100:
        frappe.throw(_("Progress must be between 0 and 100"))

    # Do not allow an already closed goal to be modified.
    if doc.is_closed:
        return doc.as_dict()

    # Update the progress.
    doc.actual_percentage = percentage

    # Automatically close the goal at 100%.
    if percentage == 100:
        completed_at = now_datetime()

        doc.is_closed = 1
        doc.closed_on = completed_at

    # Save once. Goal.validate() will also set status to Complete.
    doc.save()

    return doc.as_dict()


@frappe.whitelist(methods=["POST"])
def close_goal(goal: str) -> dict:
    """
    Retained for compatibility with older frontend versions.

    New frontend code does not need to call this endpoint because
    update_goal_progress() closes the goal automatically at 100%.
    """
    _ensure_mentor()

    doc = frappe.get_doc("Goal", goal)
    _get_assigned_student(doc.student)

    if doc.is_closed:
        return doc.as_dict()

    if (doc.actual_percentage or 0) < 100:
        frappe.throw(
            _("A goal can only be closed after reaching 100%.")
        )

    completed_at = now_datetime()

    doc.is_closed = 1
    doc.closed_on = completed_at
    doc.save()

    return doc.as_dict()
