from ..models import DerivedFinancialMetric, CreditScore

# Define weights
metric_weights = {
    "Current Ratio (approx)": 0.08,
    "Debt-to-Equity": 0.1,
    "Net Profit Margin (%)": 0.1,
    "EBIT": 0.05,
    "EBITDA": 0.05,
    "Interest Coverage Ratio": 0.1,
    "Operating Cash Flow to Total Liabilities": 0.1,
    "Return on Assets (ROA) %": 0.1,
    "Return on Equity (ROE) %": 0.1,
    "Debt-to-Assets Ratio": 0.07,
    "Equity Ratio": 0.05,
    "Asset Turnover Ratio": 0.04,
    "Receivables Turnover Ratio": 0.03,
    "Fixed Asset Turnover Ratio": 0.03
}

# Scoring logic
def score_metric(metric, value):
    if value in [None, "N/A", 0]:
        return 0
    if metric == "Current Ratio (approx)":
        return min((value / 2.0) * 100, 100)
    elif metric == "Debt-to-Equity":
        return max(100 - (value / 2.0) * 100, 0)
    elif metric == "Net Profit Margin (%)":
        return min(value, 100)
    elif metric in ["EBIT", "EBITDA"]:
        return min(value / 1000, 100)
    elif metric == "Interest Coverage Ratio":
        return min(value / 5.0 * 10, 100)
    elif metric == "Operating Cash Flow to Total Liabilities":
        return min(value * 100, 100)
    elif metric in ["Return on Assets (ROA) %", "Return on Equity (ROE) %"]:
        return min(value, 100)
    elif metric == "Debt-to-Assets Ratio":
        return max(100 - (value * 100), 0)
    elif metric == "Equity Ratio":
        return min(value * 100, 100)
    elif metric == "Asset Turnover Ratio":
        return min(value * 30, 100)
    elif metric == "Receivables Turnover Ratio":
        return min(value * 2, 100)
    elif metric == "Fixed Asset Turnover Ratio":
        return min(value * 10, 100)
    return 0

def get_category(score):
    if score >= 85:
        return "Low Risk (Excellent)"
    elif score >= 70:
        return "Moderate Risk (Good)"
    elif score >= 50:
        return "High Risk (Caution)"
    return "Very High Risk (Poor)"

def get_bucket(score):
    if score >= 80:
        return "A (Low Risk)"
    elif score >= 60:
        return "B (Moderate Risk)"
    return "C (High Risk)"

# 🔽 This is Step 3
def calculate_credit_scores(company):
    derived_metrics_qs = DerivedFinancialMetric.objects.filter(company=company)
    years = sorted(set(derived_metrics_qs.values_list("year", flat=True)))

    final_scores = {}

    for year in years:
        year_metrics = {
            obj.metric: obj.value
            for obj in derived_metrics_qs.filter(year=year)
        }

        total_score = 0
        for metric, weight in metric_weights.items():
            value = year_metrics.get(metric, "N/A")
            score = score_metric(metric, value)
            weighted_score = round(score * weight, 2)
            total_score += weighted_score

        total_score = round(total_score, 2)
        category = get_category(total_score)
        bucket = get_bucket(total_score)

        # Save to DB
        CreditScore.objects.create(
            company=company,
            year=year,
            score=total_score,
            category=category,
            risk_bucket=bucket
        )

        final_scores[year] = {
            "score": total_score,
            "category": category,
            "bucket": bucket
        }

    return final_scores
