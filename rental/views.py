from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.utils import timezone
from decimal import Decimal
from datetime import datetime
import urllib.parse

from .models import Tenant, Property, RentRecord, Expense


def dashboard(request):
    tenants = Tenant.objects.select_related('property_assigned').all()
    total_tenants = tenants.count()

    total_collected = RentRecord.objects.aggregate(
        total=Sum('amount_paid')
    )['total'] or 0

    # Calculate remaining pending
    all_records = RentRecord.objects.all()
    total_pending = sum((r.total_due - r.amount_paid) for r in all_records)

    total_expense = Expense.objects.aggregate(total=Sum('amount'))['total'] or 0
    net_profit = total_collected - total_expense

    context = {
        'tenants': tenants,
        'total_tenants': total_tenants,
        'total_collected': total_collected,
        'total_pending': total_pending,
        'total_expense': total_expense,
        'net_profit': net_profit,
    }
    return render(request, 'dashboard.html', context)


def add_tenant(request):
    properties = Property.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        property_id = request.POST.get('property')
        advance_security = request.POST.get('advance_security') or 0

        selected_property = get_object_or_404(Property, id=property_id)

        Tenant.objects.create(
            name=name,
            phone=phone,
            property_assigned=selected_property,
            advance_security=advance_security,
            move_in_date=timezone.now().date()
        )
        return redirect('dashboard')

    return render(request, 'add_tenant.html', {'properties': properties})


def generate_bill(request, tenant_id):
    tenant = get_object_or_404(Tenant, id=tenant_id)

    if request.method == 'POST':
        month_year = request.POST.get('month_year')
        units = int(request.POST.get('units') or 0)
        rate_per_unit = Decimal(str(request.POST.get('rate') or 8))

        rent = tenant.property_assigned.monthly_rent
        elec_charge = Decimal(units) * rate_per_unit
        total_due = rent + elec_charge

        RentRecord.objects.create(
            tenant=tenant,
            month_year=month_year,
            rent_amount=rent,
            electricity_units=units,
            electricity_charge=elec_charge,
            total_due=total_due,
            amount_paid=0,
            status='PENDING'
        )
        return redirect('dashboard')

    return render(request, 'generate_bill.html', {'tenant': tenant})


def tenant_bills(request, tenant_id):
    tenant = get_object_or_404(Tenant, id=tenant_id)
    records = list(RentRecord.objects.filter(tenant=tenant))

    def parse_month_year(record):
        try:
            return datetime.strptime(record.month_year, "%B %Y")
        except:
            return datetime.min

    records = sorted(records, key=parse_month_year, reverse=True)

    total_paid = sum(r.amount_paid for r in records)
    total_pending = sum(r.remaining for r in records)
    total_bills = len(records)

    context = {
        'tenant': tenant,
        'records': records,
        'total_paid': total_paid,
        'total_pending': total_pending,
        'total_bills': total_bills,
    }
    return render(request, 'tenant_bills.html', context)


def record_payment(request, record_id):
    record = get_object_or_404(RentRecord, id=record_id)

    if request.method == 'POST':
        amount = Decimal(str(request.POST.get('amount') or 0))
        method = request.POST.get('payment_method')
        date_str = request.POST.get('payment_date')

        if amount > 0:
            record.amount_paid += amount
            record.payment_method = method

            if date_str:
                record.payment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            else:
                record.payment_date = timezone.now().date()

            record.update_status()

        return redirect('tenant_bills', tenant_id=record.tenant.id)

    return render(request, 'record_payment.html', {
        'record': record,
        'today': timezone.now().date().isoformat(),
        'remaining': record.remaining
    })


def mark_as_paid(request, record_id):
    # Keep old function for compatibility (optional)
    record = get_object_or_404(RentRecord, id=record_id)
    return redirect('record_payment', record_id=record.id)


def edit_payment(request, record_id):
    record = get_object_or_404(RentRecord, id=record_id)

    if request.method == 'POST':
        status = request.POST.get('status')
        method = request.POST.get('payment_method')
        date_str = request.POST.get('payment_date')
        amount_paid = Decimal(str(request.POST.get('amount_paid') or 0))

        record.amount_paid = amount_paid
        record.payment_method = method

        if date_str:
            record.payment_date = datetime.strptime(date_str, '%Y-%m-%d').date()

        record.update_status()
        return redirect('tenant_bills', tenant_id=record.tenant.id)

    return render(request, 'edit_payment.html', {
        'record': record,
        'today': timezone.now().date().isoformat()
    })


def send_whatsapp_bill(request, record_id):
    record = get_object_or_404(RentRecord, id=record_id)

    message = (
        f"नमस्ते {record.tenant.name} जी,\n\n"
        f"आपका {record.month_year} का किराया बिल:\n"
        f"• कमरा किराया: ₹{record.rent_amount}\n"
        f"• बिजली बिल ({record.electricity_units} units): ₹{record.electricity_charge}\n"
        f"-----------------------------\n"
        f"कुल बिल: ₹{record.total_due}\n"
        f"भुगतान हो चुका: ₹{record.amount_paid}\n"
        f"बाकी बकाया: ₹{record.remaining}\n\n"
        f"कृपया समय पर भुगतान करें।\nधन्यवाद!"
    )

    encoded_message = urllib.parse.quote(message)
    phone = record.tenant.phone.strip().replace('+', '').replace(' ', '').replace('-', '')

    if not phone.startswith('91') and len(phone) == 10:
        phone = '91' + phone

    whatsapp_url = f"https://wa.me/{phone}?text={encoded_message}"
    return redirect(whatsapp_url)


def expense_list(request):
    expenses = Expense.objects.select_related('property').order_by('-date', '-id')
    total_expense = expenses.aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'expenses': expenses,
        'total_expense': total_expense,
    }
    return render(request, 'expense_list.html', context)


def add_expense(request):
    properties = Property.objects.all()

    if request.method == 'POST':
        date = request.POST.get('date')
        amount = request.POST.get('amount')
        category = request.POST.get('category')
        property_id = request.POST.get('property') or None
        description = request.POST.get('description', '')
        payment_method = request.POST.get('payment_method')

        property_obj = None
        if property_id:
            property_obj = get_object_or_404(Property, id=property_id)

        Expense.objects.create(
            date=date,
            amount=amount,
            category=category,
            property=property_obj,
            description=description,
            payment_method=payment_method
        )
        return redirect('expense_list')

    return render(request, 'add_expense.html', {
        'properties': properties,
        'today': timezone.now().date().isoformat()
    })
