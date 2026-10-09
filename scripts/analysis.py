from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
METRICS = {
    "Regional_Performance": [
        "Revenue_USD_M", "Units_Sold_K", "Returns_Rate_pct", "Marketing_Spend_USD_M"
    ],
    "Customer_Experience": [
        "NPS", "CSAT_pct", "Avg_Delivery_Days", "Support_Tickets_K"
    ],
    "Operational_Risk": [
        "Stockout_Rate_pct", "Return_Processing_Days",
        "Warehouse_Capacity_Util_pct", "Fraud_Incidents"
    ],
}


def run_analysis(data_path=None):
    tables = pd.read_excel(
        data_path or BASE_DIR / "data" / "novaretail_dataset.xlsx",
        sheet_name=list(METRICS),
    )
    expected_keys = None
    for sheet, metrics in METRICS.items():
        table = tables[sheet]
        required = ["Quarter", "Region", *metrics]
        missing = set(required) - set(table.columns)
        if missing:
            raise ValueError(f"{sheet}: missing columns {sorted(missing)}")
        if table[required].isna().any().any():
            raise ValueError(f"{sheet}: missing values")
        if table.duplicated(["Quarter", "Region"]).any():
            raise ValueError(f"{sheet}: duplicate region-quarter rows")
        if not table["Quarter"].str.fullmatch(r"\d{4}-Q[1-4]").all():
            raise ValueError(f"{sheet}: quarters must use YYYY-QN")
        for metric in metrics:
            table[metric] = pd.to_numeric(table[metric], errors="raise")
            if table[metric].isin([float("inf"), float("-inf")]).any():
                raise ValueError(f"{sheet}: non-finite {metric}")
        keys = set(zip(table["Quarter"], table["Region"]))
        if expected_keys is not None and keys != expected_keys:
            raise ValueError("All sheets must contain the same region-quarter pairs")
        expected_keys = keys
        quarters = sorted(table["Quarter"].unique())
        regions = sorted(table["Region"].unique())
        if len(quarters) != 4 or len(regions) != 4 or len(keys) != 16:
            raise ValueError(f"{sheet}: expected a complete 4-region x 4-quarter grid")
        tables[sheet] = table.sort_values(["Quarter", "Region"])

    quarters = sorted(tables["Regional_Performance"]["Quarter"].unique())
    first_quarter, latest_quarter = quarters[0], quarters[-1]
    previous_quarter = quarters[-2]
    regional = tables["Regional_Performance"]
    first = regional[regional["Quarter"] == first_quarter].set_index("Region")
    latest = regional[regional["Quarter"] == latest_quarter].set_index("Region")
    previous = regional[regional["Quarter"] == previous_quarter].set_index("Region")
    if (regional["Revenue_USD_M"] <= 0).any():
        raise ValueError("Revenue must be positive to calculate growth")

    facts = {region: {} for region in latest.index}
    for sheet, metrics in METRICS.items():
        table = tables[sheet]
        baseline = table[table["Quarter"] == first_quarter].set_index("Region")
        current = table[table["Quarter"] == latest_quarter].set_index("Region")
        for region in facts:
            for metric in metrics:
                facts[region][metric] = {
                    "first": float(baseline.loc[region, metric]),
                    "latest": float(current.loc[region, metric]),
                    "change": float(current.loc[region, metric] - baseline.loc[region, metric]),
                }
            facts[region]["revenue_growth_pct"] = float(
                (latest.loc[region, "Revenue_USD_M"] / first.loc[region, "Revenue_USD_M"] - 1) * 100
            )

    latest_customer = tables["Customer_Experience"].query("Quarter == @latest_quarter")
    latest_risk = tables["Operational_Risk"].query("Quarter == @latest_quarter")
    total_revenue = float(latest["Revenue_USD_M"].sum())
    previous_revenue = float(previous["Revenue_USD_M"].sum())
    charts = {}
    for name, sheet, metric, title in [
        ("performance", "Regional_Performance", "Revenue_USD_M", "Revenue by region (USD M)"),
        ("customer", "Customer_Experience", "NPS", "Customer NPS by region (points)"),
        ("risk", "Operational_Risk", "Stockout_Rate_pct", "Stockout rate by region (%)"),
    ]:
        pivot = tables[sheet].pivot(index="Quarter", columns="Region", values=metric).sort_index()
        charts[name] = {
            "title": title,
            "type": "line",
            "categories": pivot.index.tolist(),
            "series": {region: pivot[region].astype(float).tolist() for region in pivot.columns},
        }
    return {
        "first_quarter": first_quarter,
        "latest_quarter": latest_quarter,
        "previous_quarter": previous_quarter,
        "top_region": str(latest["Revenue_USD_M"].idxmax()),
        "growth_region": max(facts, key=lambda region: facts[region]["revenue_growth_pct"]),
        "risk_region": str(latest_risk.loc[latest_risk["Stockout_Rate_pct"].idxmax(), "Region"]),
        "customer_leader": str(latest_customer.loc[latest_customer["NPS"].idxmax(), "Region"]),
        "capacity_region": str(latest_risk.loc[latest_risk["Warehouse_Capacity_Util_pct"].idxmax(), "Region"]),
        "kpis": {
            "total_revenue_usd_m": total_revenue,
            "revenue_qoq_growth_pct": (total_revenue / previous_revenue - 1) * 100,
            "unweighted_regional_nps": float(latest_customer["NPS"].mean()),
        },
        "regions": facts,
        "charts": charts,
    }


if __name__ == "__main__":
    import json

    print(json.dumps(run_analysis(), indent=2))