Here’s the updated **README.md** with clear **Termux installation steps**.

You can copy the complete file below and replace your current `README.md` on GitHub.

---

```markdown
# Tenant & Rent Management System

A simple and practical **Tenant / Rent Management** web application built with Django.  
Designed especially for small landlords and property owners who manage rooms/houses.

---

## Features

### Tenant Management
- Add / View tenants
- Assign property/room to tenant
- Track advance security money
- Latest payment status on dashboard

### Billing
- Generate monthly rent + electricity bill
- Partial payment support
- Payment method (Cash / Digital)
- Payment date tracking
- Edit payment details anytime
- WhatsApp bill sharing

### Expense Tracking
- Add daily/monthly expenses
- Categories (Maintenance, Water, Electricity, Cleaning, etc.)
- Link expense to specific property
- Total expense & Net Profit on dashboard

### Dashboard
- Total Tenants
- Total Collected (Paid)
- Total Pending
- Total Expense
- Net Profit

---

## Tech Stack

- **Backend**: Django 5 / 6
- **Database**: SQLite (default)
- **Frontend**: Bootstrap 5 + HTML
- **Language**: Python 3.10+

---

## Installation on Termux (Android)

### 1. Update Termux & Install required packages
```bash
pkg update && pkg upgrade
pkg install python git
```

### 2. Clone the repository
```bash
git clone https://github.com/kbulbul026-coder/my-django-app.git
cd my-django-app
```

### 3. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate
```

### 4. Install Django
```bash
pip install django
```

### 5. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create superuser (optional)
```bash
python manage.py createsuperuser
```

### 7. Start the server
```bash
python manage.py runserver
```

### 8. Open in browser
Open this link in your mobile browser:

```
http://127.0.0.1:8000
```

> **Note**: Keep the Termux session running while using the app.

---

## Installation on Linux / Mac / Windows

```bash
git clone https://github.com/kbulbul026-coder/my-django-app.git
cd my-django-app
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install django
python manage.py migrate
python manage.py runserver
```

---

## How to Use

1. Go to **Admin Panel** → `/admin/` and add Properties first
2. Add Tenants from the Dashboard
3. Generate monthly bills
4. Record full or partial payments
5. Add expenses from “खर्च देखें”
6. Share bills directly on WhatsApp

---

## Project Structure

```
my-django-app/
├── config/
├── rental/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── templates/
├── manage.py
└── db.sqlite3
```

---

## Important Notes for Termux

- Use `TIME_ZONE = 'UTC'` in `settings.py` (Asia/Kolkata may cause issues)
- Keep Termux awake while server is running
- For better experience, use a browser like Chrome or Firefox

---

## Future Improvements

- Delete bill / expense
- Multiple payment history
- PDF receipt
- Monthly reports
- Search functionality

---

**Made for practical daily use by small property owners.**
```

---

Would you like me to also give you the command to update the README directly on GitHub?- Link expense to specific property
- Total expense & Net Profit on dashboard

### Dashboard
- Total Tenants
- Total Collected (Paid)
- Total Pending
- Total Expense
- Net Profit

---

## Tech Stack

- **Backend**: Django 5 / 6
- **Database**: SQLite (default)
- **Frontend**: Bootstrap 5 + HTML
- **Language**: Python 3.10+

---

## Installation on Termux (Android)

### 1. Update Termux & Install required packages
```bash
pkg update && pkg upgrade
pkg install python git
