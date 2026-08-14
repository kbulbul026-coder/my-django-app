from django.db import models
from django.utils import timezone

class Property(models.Model):
    property_name = models.CharField(max_length=100)
    address = models.TextField()
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.property_name


class Tenant(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    property_assigned = models.ForeignKey(Property, on_delete=models.CASCADE)
    move_in_date = models.DateField(default=timezone.now)
    move_out_date = models.DateField(null=True, blank=True)
    advance_security = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    
    # New field
    billing_day = models.PositiveSmallIntegerField(
        default=1,
        help_text="Day of the month when rent cycle starts (1-28)"
    )

    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        return f"{self.name} ({self.property_assigned.property_name}) - {status}"

    @property
    def latest_status(self):
        if not self.is_active:
            return "INACTIVE"
        if self.rentrecord_set.filter(status__in=['PENDING', 'PARTIAL']).exists():
            return 'PENDING'
        latest = self.rentrecord_set.order_by('-id').first()
        return latest.status if latest else "No Bill"






class RentRecord(models.Model):
    STATUS_CHOICES = [
        ('PAID', 'Paid'),
        ('PARTIAL', 'Partial'),
        ('PENDING', 'Pending'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('DIGITAL', 'Digital (UPI/Bank)'),
    ]
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    month_year = models.CharField(max_length=20)
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2)
    electricity_units = models.IntegerField(default=0)
    electricity_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_due = models.DecimalField(max_digits=10, decimal_places=2)
    
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, blank=True, null=True)
    payment_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tenant.name} - {self.month_year} - {self.status}"

    @property
    def remaining(self):
        return self.total_due - self.amount_paid

    def update_status(self):
        if self.amount_paid <= 0:
            self.status = 'PENDING'
        elif self.amount_paid >= self.total_due:
            self.status = 'PAID'
            self.amount_paid = self.total_due
        else:
            self.status = 'PARTIAL'
        self.save()


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('DIGITAL', 'Digital (UPI/Bank)'),
    ]

    rent_record = models.ForeignKey(RentRecord, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
    payment_date = models.DateField()
    note = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-payment_date', '-id']

    def __str__(self):
        return f"{self.rent_record.tenant.name} - ₹{self.amount} on {self.payment_date}"


class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('MAINTENANCE', 'Maintenance / मरम्मत'),
        ('WATER', 'Water Bill / पानी'),
        ('ELECTRICITY', 'Electricity (Common) / बिजली'),
        ('CLEANING', 'Cleaning / सफाई'),
        ('REPAIR', 'Repairs / मरम्मत'),
        ('TAX', 'Tax / Society'),
        ('OTHER', 'Other / अन्य'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('DIGITAL', 'Digital (UPI/Bank)'),
    ]

    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    property = models.ForeignKey(Property, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, default='CASH')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.date} - {self.get_category_display()} - ₹{self.amount}"


class TenantDocument(models.Model):
    DOCUMENT_TYPES = [
        ('AADHAAR', 'Aadhaar Card'),
        ('AGREEMENT', 'Rent Agreement'),
        ('PHOTO', 'Photo'),
        ('POLICE', 'Police Verification'),
        ('OTHER', 'Other'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=100, blank=True)
    file = models.FileField(upload_to='tenant_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tenant.name} - {self.get_document_type_display()}"
