import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class Goal(Document):
    def before_insert(self):
        self.created_on = now_datetime()

    def validate(self):
        self.task_description = (self.task_description or "").strip()

        if not self.task_description:
            frappe.throw(_("Task description is required"))

        # Default older records or missing values to Short Term.
        if not self.goal_term:
            self.goal_term = "Short Term"

        if self.goal_term not in ("Short Term", "Long Term"):
            frappe.throw(_("Please select a valid goal term"))

        percentage = self.actual_percentage or 0

        if not 0 <= percentage <= 100:
            frappe.throw(_("Progress must be between 0 and 100"))

        if percentage == 0:
            self.status = "Started"
        elif percentage < 100:
            self.status = "Ongoing"
        else:
            self.status = "Complete"

        # Allow only one unfinished goal per student.
        existing = frappe.db.exists(
            "Goal",
            {
                "student": self.student,
                "is_closed": 0,
                "name": ["!=", self.name or ""],
            },
        )

        if existing:
            frappe.throw(
                _("This student already has an active goal.")
            )