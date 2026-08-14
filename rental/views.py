from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.utils import timezone
from decimal import Decimal
from datetime import datetime
import urllib.parse


from .models import Tenant, Property, RentRecord, Expense, Payment, TenantDocument






def dashboard(request):
    # Show only active tenants by default
    tenants = Tenant.objects.filter(is_active=True).select_related('property_assigned')
    total_tenants = tenants.count()

    total_collected = RentRecord.objects.aggregate(
        total=Sum('amount_paid')
    )['total'] or 0

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
        billing_day = int(request.POST.get('billing_day') or 1)

        selected_property = get_object_or_404(Property, id=property_id)

        Tenant.objects.create(
            name=name,
            phone=phone,
            property_assigned=selected_property,
            advance_security=advance_security,
            move_in_date=timezone.now().date(),
            is_active=True,
            billing_day=billing_day
        )
        return redirect('dashboard')

    return render(request, 'add_tenant.html', {'properties': properties})


















def generate_bill(request, tenant_id):
    tenant = get_object_or_404(Tenant, id=tenant_id)

    if request.method == 'POST':
        month_year = request.POST.get('month_year')
        rent_amount = Decimal(str(request.POST.get('rent_amount') or tenant.property_assigned.monthly_rent))
        units = int(request.POST.get('units') or 0)
        rate_per_unit = Decimal(str(request.POST.get('rate') or 8))

        elec_charge = Decimal(units) * rate_per_unit
        total_due = rent_amount + elec_charge

        RentRecord.objects.create(
            tenant=tenant,
            month_year=month_year,
            rent_amount=rent_amount,
            electricity_units=units,
            electricity_charge=elec_charge,
            total_due=total_due,
            amount_paid=0,
            status='PENDING'
        )
        return redirect('tenant_bills', tenant_id=tenant.id)

    return render(request, 'generate_bill.html', {
        'tenant': tenant,
        'default_rent': tenant.property_assigned.monthly_rent
    })





















def tenant_bills(request, tenant_id):
    tenant = get_object_or_404(Tenant, id=tenant_id)
    records = list(RentRecord.objects.filter(tenant=tenant).prefetch_related('payments'))

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
        note = request.POST.get('note', '')

        if amount > 0:
            payment_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else timezone.now().date()

            Payment.objects.create(
                rent_record=record,
                amount=amount,
                payment_method=method,
                payment_date=payment_date,
                note=note
            )

            record.amount_paid += amount
            record.payment_method = method
            record.payment_date = payment_date
            record.update_status()

        return redirect('tenant_bills', tenant_id=record.tenant.id)

    return render(request, 'record_payment.html', {
        'record': record,
        'today': timezone.now().date().isoformat(),
        'remaining': record.remaining
    })


def edit_payment(request, record_id):
    record = get_object_or_404(RentRecord, id=record_id)

    if request.method == 'POST':
        amount_paid = Decimal(str(request.POST.get('amount_paid') or 0))
        method = request.POST.get('payment_method')
        date_str = request.POST.get('payment_date')

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


def edit_single_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    record = payment.rent_record

    if request.method == 'POST':
        old_amount = payment.amount
        new_amount = Decimal(str(request.POST.get('amount') or 0))
        method = request.POST.get('payment_method')
        date_str = request.POST.get('payment_date')
        note = request.POST.get('note', '')

        payment.amount = new_amount
        payment.payment_method = method
        payment.note = note
        if date_str:
            payment.payment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        payment.save()

        record.amount_paid = record.amount_paid - old_amount + new_amount
        record.update_status()

        return redirect('tenant_bills', tenant_id=record.tenant.id)

    return render(request, 'edit_single_payment.html', {
        'payment': payment,
        'record': record,
        'today': timezone.now().date().isoformat()
    })


def delete_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    record = payment.rent_record

    record.amount_paid -= payment.amount
    if record.amount_paid < 0:
        record.amount_paid = 0

    payment.delete()
    record.update_status()

    return redirect('tenant_bills', tenant_id=record.tenant.id)


def move_out_tenant(request, tenant_id):
    tenant = get_object_or_404(Tenant, id=tenant_id)

    if request.method == 'POST':
        move_out_date = request.POST.get('move_out_date')
        tenant.is_active = False
        if move_out_date:
            tenant.move_out_date = datetime.strptime(move_out_date, '%Y-%m-%d').date()
        else:
            tenant.move_out_date = timezone.now().date()
        tenant.save()
        return redirect('dashboard')

    return render(request, 'move_out.html', {
        'tenant': tenant,
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

def inactive_tenants(request):
    tenants = Tenant.objects.filter(is_active=False).select_related('property_assigned').order_by('-move_out_date')
    
    context = {
        'tenants': tenants,
    }
    return render(request, 'inactive_tenants.html', context)






def tenant_documents(request, tenant_id):
    tenant = get_object_or_404(Tenant, id=tenant_id)
    documents = tenant.documents.all().order_by('-uploaded_at')

    if request.method == 'POST':
        document_type = request.POST.get('document_type')
        title = request.POST.get('title', '')
        file = request.FILES.get('file')

        if file:
            TenantDocument.objects.create(
                tenant=tenant,
                document_type=document_type,
                title=title,
                file=file
            )
        return redirect('tenant_documents', tenant_id=tenant.id)

    return render(request, 'tenant_documents.html', {
        'tenant': tenant,
        'documents': documents
    })


def delete_document(request, document_id):
    document = get_object_or_404(TenantDocument, id=document_id)
    tenant_id = document.tenant.id
    document.file.delete()  # delete actual file
    document.delete()
    return redirect('tenant_documents', tenant_id=tenant_id)
