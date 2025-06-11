
# Customer Contact Manager (CCM)

## 📝 Description

This Django-based web application was created by me for as part of the coursework for the 'Software Engineering and DevOps' module. It was developed in Django and SQLite and utilises several libraries such as Bootstrap and Django Rest Framework.

It is designed to be a simple contact manager for the rejected payments team at the Department of Work and Pensions. This team handles any payments that have been rejected by the bank and need to be manually processed by contacting citizens to request updated contact details or give further instructions on how to proceed. 
The team needs to be able to keep track of the contacts they have made with customers and the outcome of those contacts.

The app includes secure user authentication, record creation and editing, audit trail fields (e.g., `created_by`), and protections aligned with OWASP Top 10 vulnerabilities.

---
Source code :
    [https://github.com/catiecord/assigment_ccm_devops](https://github.com/catiecord/assigment_ccm_devops)

Working demonstration:
    [https://ccm-devops-app-dee10a9354b1.herokuapp.com/](https://ccm-devops-app-dee10a9354b1.herokuapp.com/)

---

## ⚙️ Installation & Setup

### Requirements
- Python 3.8+
- Django 3.2+
- SQLite 

### Setup Steps

```bash
# Clone the repository
git clone https://github.com/catiecord/assigment_ccm_devops
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
## 🚀 Usage

The application is simple and intuitive. Users can navigate using the top navigation bar to manage contacts.

### Regular Users Can:
- Add a new record
- View all records
- View a single record
- Update a record
- Search for a record

### Admin Users Can:
- Add a new record
- View all records
- View a single record
- Update a record
- Delete a record
- Search for a record
- View all users
- Activate and deactivate user accounts
- Access audit logs for each record:
  - Date and time of creation or update
  - User who created or updated the record

---
## 🗂 Models

The application uses a single model, `Record`, with the following fields:

- `created_at`
- `created_by`
- `payment_reference`
- `first_name`
- `last_name`
- `contact_method`
- `contact_date`
- `contact_status`
- `notes`
- `updated_by`
- `updated_at`

These fields help store contact details and track changes made by users.

---

## 🔐 Security 

This application includes the following OWASP Top 10 protections:

- ✅ **CSRF Protection**: All forms use `{% csrf_token %}` to prevent CSRF attacks.
- ✅ **Input Validation**: Custom field-level validation on names, emails, etc.
- ✅ **XSS Protection**: All user output is escaped by default (no `|safe` used).
- ✅ **Access Control**: `@login_required_message` and `is_staff` used for admin views.

Test cases and validation messages confirm these protections are effective.

---

## 🧪 Testing

The application has been tested using Django’s built-in test framework.

**Tests include:**
- Form validation
- Model creation and updates
- URL routing
- View access control

### To run tests:
```bash
python manage.py test