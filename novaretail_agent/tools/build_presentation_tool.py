from novaretail_agent.tools.analysis_tool import analyze_dataset
from novaretail_agent.tools.content_tool import generate_content
from novaretail_agent.tools.render_tool import render_presentation
from pathlib import Path
import json
import os
import re

from google.genai.errors import APIError


def build_presentation(use_ai: bool = True) -> dict:
    """Build a NovaRetail review matching the provided template's slides and named shapes.

    Args:
        use_ai: Generate Gemini-written copy. False is only for an explicitly requested offline preview.

    Returns:
        Build status, actual slide count, saved file paths, content provenance and computed business findings.
    """
    stage = "analysis"
    try:
        analysis = analyze_dataset()
        stage = "content"
        content = generate_content(analysis, use_ai=use_ai)
        stage = "render"
        output_dir = Path(__file__).resolve().parents[2] / "output"
        stem = "presentation" if use_ai else "offline_preview"
        output_file = render_presentation(
            content, analysis, output_dir / f"{stem}.pptx", offline=not use_ai
        )
        stage = "audit"
        audit_path = output_dir / f"{stem}_evidence.json"
        audit_path.write_text(json.dumps({
            "content_source": "gemini" if use_ai else "offline_draft",
            "slide_count": len(content),
            "analysis": analysis,
            "content": content,
        }, indent=2, allow_nan=False), encoding="utf-8")
    except Exception as error:
        result = {
            "status": "error",
            "stage": stage,
            "error_type": type(error).__name__,
            "next_step": (
                "Check local assets and workbook schema for analysis failures; "
                "check template shape names, API key, model access, quota and content schema for content failures; "
                "close the output deck in PowerPoint and check shape names/output permissions for render or audit failures."
            ),
        }
        if isinstance(error, APIError):
            message = error.message or "Gemini API request failed."
            for name in ("GOOGLE_API_KEY", "GEMINI_API_KEY"):
                secret = os.getenv(name)
                if secret:
                    message = message.replace(secret, "[REDACTED]")
            message = re.sub(r"AIza[0-9A-Za-z_-]+", "[REDACTED]", message)
            result["http_status"] = error.code
            result["message"] = message[:2000]
            result["next_step"] = {
                400: "Check Gemini request parameters and JSON Schema compatibility.",
                401: "Check the API key privately in .env and restart ADK after changing it.",
                403: "Check API key permissions and access to the configured Gemini model.",
                404: "Check GEMINI_MODEL and confirm the model is available to your account.",
                429: "Check Gemini quota and billing, then retry after the rate limit clears.",
            }.get(error.code, "Check Gemini service availability and retry the request.")
        return result

    return {
        "status": "success",
        "file": output_file,
        "evidence_file": str(audit_path),
        "content_source": "gemini" if use_ai else "offline_draft",
        "slide_count": len(content),
        "quarter": analysis["latest_quarter"],
        "kpis": analysis["kpis"],
        "growth_region": analysis["growth_region"],
        "risk_region": analysis["risk_region"],
    }