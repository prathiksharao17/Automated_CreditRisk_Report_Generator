# financials/utils/bse2.py

import pdfplumber
import re
from financials.models import ExtractedBalanceSheet

METRICS = {
    "Total Assets": ["total assets"],
    "Total Equity and Liabilities": ["total equity and liabilities"],
    "Total Liabilities": ["total liabilities"],
    "Equity Share Capital": ["equity share capital"],
    "Other Equity": ["other equity"],
    "Cash and Cash Equivalents": ["cash and cash equivalents", "cash equivalents"],
    "Deferred Tax Liabilities (Net)": [
        "deferred tax liabilities (net)", "net deferred tax liabilities", "deferred tax liability (net)"
    ],
    "Deferred Tax Assets (Net)": ["deferred tax assets (net)", "net deferred tax assets", "dta"],
    "Current Tax Liabilities (Net)": ["current tax liabilities (net)", "income tax payable", "provision for tax"],
    "Current Tax Assets (Net)": ["current tax assets (net)", "advance income tax", "tax refund receivable"],
    "Property, Plant and Equipment": ["property, plant and equipment", "property plant and equipment"],
    "Capital Work-in-Progress": ["capital work-in-progress", "capital work in progress", "cwip"],
    "Trade Receivables": ["trade receivables", "trades receivable"]
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
        ExtractedBalanceSheet.objects.create(
            company=company,
            metric=metric,
            year=year,
            value=value if isinstance(value, float) else None
        )
    except Exception as e:
        print(f"⚠️ Could not save {metric} for {year}: {e}")

def parse_and_save_balance_sheet(pdf_path, company):
    lines = extract_text_lines_from_pdf(pdf_path)
    years = find_column_years(lines)
    results = {metric: {year: "Not Found" for year in years} for metric in METRICS}
    results["Long-Term Debt"] = {year: "Not Found" for year in years}
    results["Total Current Assets"] = {year: "Not Found" for year in years}
    results["Total Current Liabilities"] = {year: "Not Found" for year in years}

    in_non_current_liabilities = False

    for i, line in enumerate(lines):
        line_lower = line.lower()

        if "non-current liabilities" in line_lower:
            in_non_current_liabilities = True
        elif any(term in line_lower for term in ["current liabilities", "equity", "assets", "total equity and liabilities"]):
            in_non_current_liabilities = False

        if in_non_current_liabilities and "borrowings" in line_lower:
            numbers = clean_and_extract_numbers(line, len(years))
            if len(numbers) == len(years):
                for j, year in enumerate(years):
                    try:
                        results["Long-Term Debt"][year] = float(numbers[j].replace(",", ""))
                    except:
                        results["Long-Term Debt"][year] = "Parse Error"

        for metric, keywords in METRICS.items():
            for keyword in keywords:
                if keyword in line_lower:
                    numbers = clean_and_extract_numbers(line, len(years))
                    if len(numbers) == len(years):
                        for j, year in enumerate(years):
                            try:
                                results[metric][year] = float(numbers[j].replace(",", ""))
                            except:
                                results[metric][year] = "Parse Error"

        if "total assets" in line_lower and i > 0:
            prev_line = lines[i - 1]
            numbers = clean_and_extract_numbers(prev_line, len(years))
            if len(numbers) == len(years):
                for j, year in enumerate(years):
                    try:
                        results["Total Current Assets"][year] = float(numbers[j].replace(",", ""))
                    except:
                        results["Total Current Assets"][year] = "Parse Error"

        if "total liabilities" in line_lower and i > 0:
            prev_line = lines[i - 1]
            numbers = clean_and_extract_numbers(prev_line, len(years))
            if len(numbers) == len(years):
                for j, year in enumerate(years):
                    try:
                        results["Total Current Liabilities"][year] = float(numbers[j].replace(",", ""))
                    except:
                        results["Total Current Liabilities"][year] = "Parse Error"

    # Fill Total Liabilities if needed
    for year in years:
        try:
            teql = results["Total Equity and Liabilities"][year]
            esc = results["Equity Share Capital"][year]
            oe = results["Other Equity"][year]
            tl = results["Total Liabilities"][year]
            if tl == "Not Found" and all(isinstance(x, float) for x in [teql, esc, oe]):
                results["Total Liabilities"][year] = round(teql - (esc + oe), 2)
        except:
            continue

    # Save all to DB
    for metric, year_values in results.items():
        for year, value in year_values.items():
            save_to_db(company, metric, year, value)

    return results, years
