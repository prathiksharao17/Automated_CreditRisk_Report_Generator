from ..models import (
    ExtractedBalanceSheet,
    ExtractedIncomeStatement,
    ExtractedCashFlow,
    DerivedFinancialMetric
)

def fetch_data(model, company):
    data = {}
    records = model.objects.filter(company=company)
    for record in records:
        data.setdefault(record.metric, {})[record.year] = record.value
    return data

def parse_and_save_derived_metrics(company):
    balance_data = fetch_data(ExtractedBalanceSheet, company)
    income_data = fetch_data(ExtractedIncomeStatement, company)
    cash_data = fetch_data(ExtractedCashFlow, company)

    # Choose years based on common overlap
    years = sorted(set(balance_data.get("Total Assets", {}).keys()), reverse=True)
    derived_metrics = {}

    def val(d, key, year): 
        return d.get(key, {}).get(year, 0) if isinstance(d.get(key, {}).get(year, 0), (int, float)) else 0

    for year in years:
        derived_metrics[year] = {}
        try:
            total_assets = val(balance_data, "Total Assets", year)
            total_liabilities = val(balance_data, "Total Liabilities", year)
            equity = val(balance_data, "Equity Share Capital", year) + val(balance_data, "Other Equity", year)
            pbt = val(income_data, "PBT (Profit Before Tax)", year)
            pat = val(income_data, "PAT (Profit After Tax)", year)
            total_income = val(income_data, "Total Income", year)
            total_revenue = val(income_data, "Revenue from Operations", year)
            depreciation = val(income_data, "Depreciation and Amortisation", year)
            finance_cost = val(income_data, "Finance Costs", year)
            net_cash_ops = val(cash_data, "Net Cash from Operating Activities", year)
            trade_receivables = val(balance_data, "Trade Receivables", year)
            fixed_assets = val(balance_data, "Property, Plant and Equipment", year) + val(balance_data, "Capital Work-in-Progress", year)

            # Derived metrics
            derived_metrics[year]["Current Ratio (approx)"] = round(total_assets / total_liabilities, 2) if total_liabilities else None
            derived_metrics[year]["Debt-to-Equity"] = round(total_liabilities / equity, 2) if equity else None
            derived_metrics[year]["Net Profit Margin (%)"] = round((pat / total_income) * 100, 2) if total_income else None
            derived_metrics[year]["EBIT"] = round(pbt + finance_cost, 2)
            derived_metrics[year]["EBITDA"] = round(pbt + finance_cost + depreciation, 2)
            derived_metrics[year]["Interest Coverage Ratio"] = round((pbt + finance_cost) / finance_cost, 2) if finance_cost else None
            derived_metrics[year]["Operating Cash Flow to Total Liabilities"] = round(net_cash_ops / total_liabilities, 2) if total_liabilities else None
            derived_metrics[year]["Return on Assets (ROA) %"] = round((pat / total_assets) * 100, 2) if total_assets else None
            derived_metrics[year]["Return on Equity (ROE) %"] = round((pat / equity) * 100, 2) if equity else None
            derived_metrics[year]["Debt-to-Assets Ratio"] = round(total_liabilities / total_assets, 2) if total_assets else None
            derived_metrics[year]["Equity Ratio"] = round(equity / total_assets, 2) if total_assets else None
            derived_metrics[year]["Asset Turnover Ratio"] = round(total_revenue / total_assets, 2) if total_assets else None
            derived_metrics[year]["Receivables Turnover Ratio"] = round(total_revenue / trade_receivables, 2) if trade_receivables else None
            derived_metrics[year]["Fixed Asset Turnover Ratio"] = round(total_revenue / fixed_assets, 2) if fixed_assets else None

        except Exception as e:
            print(f"⚠️ Error computing metrics for {year}: {e}")

    # Save all derived metrics to DB
    for year, metrics in derived_metrics.items():
        for metric_name, value in metrics.items():
            try:
                DerivedFinancialMetric.objects.create(
                    company=company,
                    metric=metric_name,
                    year=year,
                    value=value
                )
            except Exception as e:
                print(f"⚠️ Failed to save derived metric {metric_name} for {year}: {e}")

    return derived_metrics, years
