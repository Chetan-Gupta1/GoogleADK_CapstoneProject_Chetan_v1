import sys
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

BASE_DIR = Path(__file__).resolve().parent.parent
if __package__ in (None, ""):
    sys.path.insert(0, str(BASE_DIR))

from scripts.analysis import run_analysis
from content.slide_generator import SlideGenerator
from novaretail_agent.tools.build_presentation_tool import (build_presentation)

app = FastAPI()
app.mount(
    "/static",
    StaticFiles(directory="webapp/static"),
    name="static"
)

templates = Jinja2Templates(
    directory="webapp/templates"
)

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )

@app.post("/analyze")
def analyze():
    analysis = run_analysis()
    return {
        "status": "success",
        "kpis": analysis["kpis"],
        "growth_region": analysis["growth_region"],
        "risk_region": analysis["risk_region"]
    }

@app.post("/generate-content")
def generate_content():
    analysis = run_analysis()
    generator = SlideGenerator(analysis)
    content = generator.generate(use_ai=True)
    return {
        "status": "success",
        "content": content
    }

@app.post("/build-presentation")
def buildPresentation():
    result = build_presentation(use_ai=True)
    return result

@app.get("/download-ppt")
def download_ppt():
    return FileResponse(
        "output/presentation.pptx",
        media_type=
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename="NovaRetail_Executive_Review.pptx"
    )