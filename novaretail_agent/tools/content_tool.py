import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(BASE_DIR))

from content.slide_generator import (SlideGenerator)

def generate_content(analysis_result, use_ai=True):

    generator = SlideGenerator(analysis_result)
    return generator.generate(use_ai=use_ai)