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
