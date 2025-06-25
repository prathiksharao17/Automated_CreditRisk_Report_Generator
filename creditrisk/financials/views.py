from django.shortcuts import render, redirect, get_object_or_404
from .forms import CompanyForm, FinancialDocumentForm
from .models import Company, CreditScore
from .utils.bse2 import parse_and_save_balance_sheet
from .utils.bse3 import parse_and_save_income_statement
from .utils.bse4 import parse_and_save_cash_flow
from .utils.bse5 import parse_and_save_derived_metrics
from .utils.bse6 import calculate_credit_scores
from .utils.generate_report import generate_company_report, generate_word_report
from django.http import HttpResponse

def company_info(request):
    if request.method == 'POST':
        company_form = CompanyForm(request.POST)
        if company_form.is_valid():
            company = company_form.save()
            request.session['company_id'] = company.id  # Save for next step
            return redirect('document_upload')
    else:
        company_form = CompanyForm()
    return render(request, 'financials/upload_form.html', {'company_form': company_form})

def document_upload(request):
    company_id = request.session.get('company_id')
    if not company_id:
        return redirect('company_info')
    company = get_object_or_404(Company, id=company_id)
    error = None

    if request.method == 'POST':
        document_form = FinancialDocumentForm(request.POST, request.FILES)
        if document_form.is_valid():
            document = document_form.save(commit=False)
            document.company = company
            document.save()
            try:
                parse_and_save_balance_sheet(document.balance_sheet.path, company)
                parse_and_save_income_statement(document.income_statement.path, company)
                parse_and_save_cash_flow(document.cash_flow_statement.path, company)
                parse_and_save_derived_metrics(company)
                calculate_credit_scores(company)
                return redirect('upload_success')
            except Exception as e:
                error = f"Processing failed: {e}"
    else:
        document_form = FinancialDocumentForm()
    return render(request, 'financials/document_upload.html', {
        'company': company,
        'document_form': document_form,
        'error': error,
    })

def download_report(request):
    company_id = request.session.get('company_id')
    if not company_id:
        return redirect('company_info')
    document = generate_word_report(company_id)
    response = HttpResponse(
        document,
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
    response['Content-Disposition'] = f'attachment; filename=credit_report_{company_id}.docx'
    return response

def upload_success(request):
    company_id = request.session.get('company_id')
    if not company_id:
        return redirect('company_info')
    company = get_object_or_404(Company, id=company_id)
    derived_data, years = parse_and_save_derived_metrics(company)
    credit_scores = CreditScore.objects.filter(company=company).order_by('-year')
    full_report = generate_company_report(company.id)
    
    # FIX: Use the first year in the list
    financials = derived_data[years[0]] if years else {}

    return render(request, 'financials/upload_success.html', {
        'company': company,
        'derived': derived_data,
        'credit_scores': credit_scores,
        'report': full_report,
        'financials': financials,
    })
