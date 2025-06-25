from django.db import models

class Company(models.Model):
    company_name = models.CharField(max_length=255)
    company_number = models.CharField(max_length=50)
    company_pan = models.CharField(max_length=20)
    line_of_business = models.TextField()
    website = models.URLField(blank=True, null=True)
    incorporated_on = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company_name


class FinancialDocument(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    balance_sheet = models.FileField(upload_to='financials/balance_sheets/')
    income_statement = models.FileField(upload_to='financials/income_statements/')
    cash_flow_statement = models.FileField(upload_to='financials/cash_flows/')
    uploaded_at = models.DateTimeField(auto_now_add=True)


class ExtractedBalanceSheet(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    metric = models.CharField(max_length=255)
    year = models.CharField(max_length=10)
    value = models.FloatField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.company} - {self.metric} - {self.year}"


class ExtractedIncomeStatement(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    metric = models.CharField(max_length=255)
    year = models.CharField(max_length=10)
    value = models.FloatField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.company} - {self.metric} - {self.year}"


class ExtractedCashFlow(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    metric = models.CharField(max_length=255)
    year = models.CharField(max_length=10)
    value = models.FloatField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.company} - {self.metric} - {self.year}"


class DerivedFinancialMetric(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    metric = models.CharField(max_length=255)
    year = models.CharField(max_length=10)
    value = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.company} - {self.metric} - {self.year}"


class CreditScore(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    year = models.CharField(max_length=10)
    score = models.FloatField()
    category = models.CharField(max_length=50)
    risk_bucket = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.company.company_name} - {self.year}: {self.risk_bucket}"
