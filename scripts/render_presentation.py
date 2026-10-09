import argparse
import json

from novaretail_agent.tools.build_presentation_tool import build_presentation


def main():
    parser = argparse.ArgumentParser(description="Build the NovaRetail executive review.")
    parser.add_argument("--offline", action="store_true", help="Build a labelled, non-AI preview without API calls.")
    arguments = parser.parse_args()
    result = build_presentation(use_ai=not arguments.offline)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())