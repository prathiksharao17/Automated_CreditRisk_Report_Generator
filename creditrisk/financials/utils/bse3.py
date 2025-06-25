import pdfplumber
import re
from financials.models import ExtractedIncomeStatement

INCOME_METRICS = {
    "Revenue from Operations": ["revenue from operations"],
    "Other Income": ["other income"],
    "Total Income": ["total income"],
    "Cost of Materials Consumed": ["cost of materials consumed"],
    "Excise Duty": ["excise duty"],
    "Purchases of Stock-in-Trade": ["purchases of stock-in-trade"],
    "Changes in Inventories": ["changes in inventories"],
    "Employee Benefits Expense": ["employee benefits expense"],
    "Finance Costs": ["finance costs"],
    "Depreciation and Amortisation": ["depreciation", "amortisation", "impairment"],
    "Other Expenses": ["other expenses"],
    "PBT (Profit Before Tax)": ["profit before tax", "profit / (loss) before tax"],
    "PAT (Profit After Tax)": ["profit for the year", "profit / (loss) for the year"],
    "Current Tax": ["current tax"],
    "Deferred Tax": ["deferred tax"],
    "Total Comprehensive Income": ["total comprehensive income"],
    "EPS (Basic)": ["earnings per equity share", "basic"],
    "EPS (Diluted)": ["diluted"]
}

def extract_text_lines_from_pdf(path):
    lines = []
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    lines.extend(text.splitlines())
    except Exception as e:
        print(f"❌ Error reading PDF: {e}")
    return lines

def find_column_years(lines):
    for line in lines:
        years = re.findall(r"20\d{2}", line)
        if len(years) >= 2:
            return sorted(years, reverse=True)
    return []

def clean_and_extract_numbers(line, num_years):
    numbers = re.findall(r"[0-9,.\-]+", line)
    if len(numbers) > num_years:
        numbers = numbers[-num_years:]
    return numbers

def save_to_db(company, metric, year, value):
    try:
        ExtractedIncomeStatement.objects.create(
            company=company,
            metric=metric,
            year=year,
            value=value if isinstance(value, float) else None
        )
    except Exception as e:
        print(f"⚠️ Error saving {metric} for {year}: {e}")

def parse_and_save_income_statement(pdf_path, company):
    lines = extract_text_lines_from_pdf(pdf_path)
    years = find_column_years(lines)
    results = {metric: {year: "Not Found" for year in years} for metric in INCOME_METRICS}

    for line in lines:
        line_lower = line.lower()

        for metric, keywords in INCOME_METRICS.items():
            for keyword in keywords:
                if keyword in line_lower:
                    numbers = clean_and_extract_numbers(line, len(years))
                    if len(numbers) == len(years):
                        for i, year in enumerate(years):
                            try:
                                results[metric][year] = float(numbers[i].replace(",", ""))
                            except:
                                results[metric][year] = "Parse Error"

    # Save to DB
    for metric, values in results.items():
        for year, value in values.items():
            save_to_db(company, metric, year, value)

    return results, years
