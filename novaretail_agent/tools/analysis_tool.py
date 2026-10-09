import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(BASE_DIR))

from scripts.analysis import run_analysis



def analyze_dataset():

    """
    Analyze NovaRetail dataset and
    return business metrics.
    """

    return run_analysis()


if __name__ == "__main__":
    print(analyze_dataset())