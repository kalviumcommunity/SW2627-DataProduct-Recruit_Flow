import argparse
import subprocess
import sys
from datetime import datetime
from secrets import token_hex
from pathlib import Path


CURRENT_DIR = Path(__file__).resolve().parent
GENERATOR = CURRENT_DIR / "generate_mvp_scale_data.py"
LOADER = CURRENT_DIR / "load_mvp_scale_dataset.py"


def make_run_id() -> str:
    return f"demo-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{token_hex(3)}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Fresh seed command for the MVP demo dataset.")
    parser.add_argument("--dataset", choices=["clean", "messy"], default="clean")
    parser.add_argument("--transport", choices=["direct", "http"], default="direct")
    parser.add_argument("--run-id", default=None, help="Optional namespace for this seed run.")
    parser.add_argument("--skip-reset", action="store_true", help="Skip the database reset before load.")
    parser.add_argument("--generate-only", action="store_true", help="Only generate files, do not load them.")
    args = parser.parse_args()

    run_id = args.run_id or make_run_id()
    print(f"Using run_id={run_id}")

    subprocess.run(
        [sys.executable, str(GENERATOR), "--run-id", run_id],
        check=True,
    )

    if args.generate_only:
        return

    load_cmd = [
        sys.executable,
        str(LOADER),
        "--dataset",
        args.dataset,
        "--transport",
        args.transport,
        "--run-id",
        run_id,
    ]
    if args.skip_reset:
        load_cmd.append("--skip-reset")

    subprocess.run(load_cmd, check=True)


if __name__ == "__main__":
    main()
