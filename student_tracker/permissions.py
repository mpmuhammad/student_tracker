"""Row-level permissions: a Mentor only sees the students assigned to them
(Student.mentor) and the activity records of those students."""

import frappe

MENTOR_ROLE = "Mentor"


def is_restricted_mentor(user: str | None = None) -> bool:
	"""True for users who have the Mentor role but no admin role."""
	user = user or frappe.session.user
	if user == "Administrator":
		return False
	roles = frappe.get_roles(user)
	return MENTOR_ROLE in roles and "System Manager" not in roles


def student_query_conditions(user: str | None = None) -> str:
	user = user or frappe.session.user
	if not is_restricted_mentor(user):
		return ""
	return f"`tabStudent`.`mentor` = {frappe.db.escape(user)}"


def activity_record_query_conditions(user: str | None = None) -> str:
	user = user or frappe.session.user
	if not is_restricted_mentor(user):
		return ""
	return (
		"`tabActivity Record`.`student` in "
		f"(select `name` from `tabStudent` where `mentor` = {frappe.db.escape(user)})"
	)


def has_student_permission(doc, ptype=None, user=None) -> bool | None:
	user = user or frappe.session.user
	if not is_restricted_mentor(user):
		return None
	return doc.mentor == user


def has_activity_record_permission(doc, ptype=None, user=None) -> bool | None:
	user = user or frappe.session.user
	if not is_restricted_mentor(user):
		return None
	if not doc.student:
		# new, not yet linked record; the student check runs on save
		return ptype == "create"
	return frappe.db.get_value("Student", doc.student, "mentor") == user
