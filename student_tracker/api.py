"""Whitelisted endpoints used by the Mentor portal (frontend/, served at /mentor)."""

import html

import frappe
from frappe import _
from frappe.query_builder.functions import Count, Max
from frappe.utils import getdate, today

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
