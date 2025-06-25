import pdfplumber
import re
from financials.models import ExtractedCashFlow

CASHFLOW_METRICS = {
    "Profit Before Tax": ["profit before tax", "profit before exceptional items and tax"],
    "Depreciation and Amortisation": ["depreciation and amortisation", "depreciation", "amortisation"],
    "Finance Cost": ["finance cost", "interest cost", "finance charges"],
    "Interest Income": ["interest income"],
    "Operating Profit before Working Capital Changes": ["operating profit before working capital changes"],
    "Cash Generated from Operations": ["cash generated from operations"],
    "Direct Taxes Paid": ["direct taxes paid"],
    "Net Cash from Operating Activities": ["net cash from operating activities", "net cash generated from operating activities"],
    "Purchase of Property, Plant and Equipment": ["purchase of property, plant and equipment"],
    "Proceeds from Disposal of PPE": ["proceeds from disposal of property, plant and equipment"],
    "Interest Received": ["interest received"],
    "Net Cash from Investing Activities": ["net cash from investing activities", "net cash (used in)/ cash flow from investing activities"],
    "Dividends Paid": ["dividends paid"],
    "Payment of Lease Liabilities": ["payment of lease liabilities"],
    "Net Cash from Financing Activities": ["net cash used in financing activities"],
    "Net Increase/Decrease in Cash": ["net increase", "net decrease in cash", "net increase/ (decrease) in cash"],
    "Cash and Cash Equivalents at Beginning": ["cash and cash equivalents at the beginning of the year"],
    "Cash and Cash Equivalents at End": ["cash and cash equivalents at the end of the year"]
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
        ExtractedCashFlow.objects.create(
            company=company,
            metric=metric,
            year=year,
            value=value if isinstance(value, float) else None
        )
    except Exception as e:
        print(f"⚠️ Error saving {metric} for {year}: {e}")

def parse_and_save_cash_flow(pdf_path, company):
    lines = extract_text_lines_from_pdf(pdf_path)
    years = find_column_years(lines)
    results = {metric: {year: "Not Found" for year in years} for metric in CASHFLOW_METRICS}

    for line in lines:
        line_lower = line.lower()
        for metric, keywords in CASHFLOW_METRICS.items():
            for keyword in keywords:
                if keyword in line_lower:
                    numbers = clean_and_extract_numbers(line, len(years))
                    if len(numbers) == len(years):
                        for i, year in enumerate(years):
                            try:
                                value = float(numbers[i].replace(",", ""))
                                results[metric][year] = value
                                save_to_db(company, metric, year, value)
                            except:
                                results[metric][year] = "Parse Error"

    return results, years
