
# Customer Contact Manager (CCM)

## 📝 Description
This Django-based web application was developed for managing customer contact records related to rejected payments within the Department for Work and Pensions (DWP). Originally created for coursework, it has been enhanced to align with modern **Software Engineering** and **DevOps** practices.

The app includes secure user authentication, record creation and editing, audit trail fields (e.g., `created_by`), and protections aligned with OWASP Top 10 vulnerabilities.

---

## ⚙️ Installation & Setup

### Requirements
- Python 3.8+
- Django 3.2+
- SQLite (default, for ease of setup)

### Setup Steps

```bash
# Clone the repository
git clone https://github.com/catiecord/assignment_ccm.git
cd assignment_ccm

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install requirements
pip install -r requirements.txt

# Migrate the database
python manage.py migrate

# Create a superuser for admin access
python manage.py createsuperuser

# Run the development server
python manage.py runserver
```

---

## 🔐 Security Enhancements

This application includes the following OWASP Top 10 protections:

- ✅ **CSRF Protection**: All forms use `{% csrf_token %}` to prevent CSRF attacks.
- ✅ **Input Validation**: Custom field-level validation on names, emails, etc.
- ✅ **XSS Protection**: All user output is escaped by default (no `|safe` used).
- ✅ **Access Control**: `@login_required` and `is_staff` used for admin views.

Test cases and validation messages confirm these protections are effective.

---

## 🧪 Testing

To run basic tests (if included):

```bash
python manage.py test
```

You may also see test coverage in `/htmlcov` if `coverage.py` was used.

---
