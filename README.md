### Student Tracker

Frappe app for track student activity information

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch version-16
bench install-app student_tracker
```

### Mentor portal

A Vue 3 + [frappe-ui](https://ui.frappe.io) app for users with the **Mentor** role, served at `/mentor`.

- **Login** at `/mentor/login` (Mentors are also sent to `/mentor` after logging in through `/login`).
- **My students** – every Student whose `Mentor` field is the logged-in user, with photo, contact, school and madrassa details, number of activities and the last activity date. Searchable.
- **Add activity** – record an Activity Record (date + note) for any of those students.
- **View notes** – a student's profile and the timeline of their previous activity notes.

Mentors can only see and add records for students assigned to them (enforced by permission hooks in `student_tracker/permissions.py` and the checks in `student_tracker/api.py`).

#### Setup

1. `bench --site <site> migrate` – creates the **Mentor** role (fixture) and the new `Mentor` fields on Student / Activity Record.
2. Create a user, give them the **Mentor** role.
3. Open each Student and set **Mentor** to that user (upload a photo with the image field in the form header).
4. Build the frontend: `bench build --app student_tracker` (or `cd apps/student_tracker/frontend && npm install && npm run build`).

#### Development

```bash
cd apps/student_tracker/frontend
npm install
npm run dev
```

The Vite dev server proxies `/api`, `/files`, … to the bench web server. Open the URL it prints and go to `/mentor`.

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/student_tracker
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### License

mit
