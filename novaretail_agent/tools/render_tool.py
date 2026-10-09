import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(BASE_DIR))

from renderer.ppt_renderer import (
    PptRenderer
)
from content.slide_generator import content_schema
from renderer.ppt_utils import DEFAULT_TEMPLATE, inspect_template
from scripts.analysis import run_analysis
from datetime import date


def render_presentation(content, analysis=None, output_path=None, offline=False, template_path=None):
    template_path = template_path or DEFAULT_TEMPLATE
    specifications = inspect_template(template_path)
    content = content_schema(specifications).model_validate(content).model_dump()
    analysis = analysis if analysis is not None else run_analysis()
    renderer = PptRenderer(template_path)
    kpis = analysis["kpis"]
    callouts = {
        1: {"value": f"${kpis['total_revenue_usd_m']:,.0f}M", "label": "Latest-quarter revenue (USD M)"},
        2: {"value": f"{kpis['revenue_qoq_growth_pct']:+.2f}%", "label": f"Revenue growth vs {analysis['previous_quarter']}"},
        3: {"value": f"{kpis['unweighted_regional_nps']:.2f}", "label": "Mean regional NPS (unweighted)"},
    }
    for specification in specifications:
        slide_no = specification["slide_no"]
        slide_content = content[f"slide_{slide_no}"]
        for field, names in specification["fields"].items():
            for name in names:
                renderer.replace_text(slide_no, name, slide_content[field], bold_lead=field == "recommendations")
        for name in specification["subtitles"]:
            renderer.replace_text(slide_no, name, f"{analysis['latest_quarter']} | Board Review | Prepared {date.today().isoformat()}")
        for name, callout in specification["kpis"].items():
            renderer.replace_text(slide_no, name, callouts[callout["number"]][callout["kind"]])
        for name, theme in specification["charts"].items():
            renderer.replace_chart(slide_no, name, analysis["charts"][theme])
        for name in specification["icons"]:
            renderer.replace_icon(slide_no, name, BASE_DIR / "icons" / slide_content["icon"])
        footer = f"NovaRetail | Source: novaretail_dataset.xlsx | {analysis['first_quarter']} to {analysis['latest_quarter']}"
        if offline:
            footer = "OFFLINE PREVIEW - NOT AI GENERATED | " + footer
        for name in specification["footers"]:
            renderer.replace_text(slide_no, name, footer)
        for name in specification["page_numbers"]:
            renderer.replace_text(slide_no, name, str(slide_no))
    renderer.validate()
    output_path = Path(output_path) if output_path else BASE_DIR / "output" / "presentation.pptx"
    renderer.save(output_path)
    return str(output_path)


if __name__ == "__main__":
    from novaretail_agent.tools.analysis_tool import analyze_dataset
    from novaretail_agent.tools.content_tool import generate_content

    content = generate_content(analyze_dataset())
    print(render_presentation(content))