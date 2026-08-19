import argparse
import csv
import hashlib
import os
import sys
from pathlib import Path
from typing import Dict, List
from urllib.parse import urlparse, urlunparse

import requests
import psycopg2

CURRENT_DIR = os.path.dirname(__file__)
SCRIPTS_DIR = os.path.dirname(CURRENT_DIR)
BACKEND_DIR = os.path.dirname(SCRIPTS_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.core.database import get_connection


ENTITY_ORDER = [
    "candidates",
    "jobs",
    "applications",
    "stage_events",
    "interviews",
    "offers",
    "onboarding",
]

PIPELINE_TABLES = [
    "core.validation_errors",
    "core.load_errors",
    "raw.raw_records",
    "staging.candidates",
    "staging.jobs",
    "staging.applications",
    "staging.stage_events",
    "staging.interviews",
    "staging.offers",
    "staging.onboarding",
    "core.stage_events",
    "core.interviews",
    "core.offers",
    "core.onboarding",
    "core.applications",
    "core.jobs",
    "core.candidates",
    "core.ingestion_batches",
    "core.possible_duplicates",
]


def resolve_database_url(raw_url: str) -> str:
    parsed = urlparse(raw_url)
    if parsed.hostname == "db":
        netloc = parsed.netloc.replace("db", "localhost", 1)
        parsed = parsed._replace(netloc=netloc)
    return urlunparse(parsed)


def get_database_url(override: str | None) -> str:
    default_url = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/recruitflow",
    )
    return resolve_database_url(override or default_url)


def truncate_pipeline_tables(database_url: str) -> None:
    with psycopg2.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"TRUNCATE TABLE {', '.join(PIPELINE_TABLES)} RESTART IDENTITY CASCADE"
            )
        conn.commit()


def count_csv_rows(file_path: Path) -> int:
    with file_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        next(reader, None)
        return sum(1 for _ in reader)


def read_manifest(dataset_dir: Path) -> Dict:
    manifest_path = dataset_dir / "expected_results.json"
    if manifest_path.exists():
        import json

        return json.loads(manifest_path.read_text(encoding="utf-8"))
    return {}


def upload_file(api_url: str, file_path: Path) -> Dict:
    timeout_seconds = int(os.getenv("MVP_UPLOAD_TIMEOUT", "1800"))
    with file_path.open("rb") as handle:
        response = requests.post(
            api_url,
            files={"file": (file_path.name, handle, "text/csv")},
            timeout=timeout_seconds,
        )
    response.raise_for_status()
    return response.json()


def load_dataset(api_url: str, dataset_dir: Path, transport: str, database_url: str) -> List[Dict]:
    results = []
    if transport == "direct":
        os.environ["DATABASE_URL"] = database_url
        from app.core.config import settings as app_settings

        app_settings.DATABASE_URL = database_url
        from app.services.ingestion.file_handler import (
            create_ingestion_batch,
        )
        from app.services.ingestion.parser import parse_file_to_raw_records, store_raw_records
        from app.services.ingestion.staging_service import process_batch_to_staging
        from app.services.ingestion.cleaner import clean_batch
        from app.services.ingestion.deduplicator import deduplicate_batch
        from app.services.ingestion.journey_builder import (
            derive_missing_applied_stage,
            derive_supporting_journey_events,
        )

        combined_parsed_data: Dict[str, List[Dict]] = {}
        file_hashes: List[str] = []

        for entity in ENTITY_ORDER:
            file_path = dataset_dir / f"{entity}.csv"
            if not file_path.exists():
                raise FileNotFoundError(f"Missing dataset file: {file_path}")

            expected_rows = count_csv_rows(file_path)
            file_bytes = file_path.read_bytes()
            file_hash = hashlib.sha256(file_bytes).hexdigest()
            file_hashes.append(f"{entity}:{file_hash}")
            parsed_data = parse_file_to_raw_records(str(file_path), "csv")
            combined_parsed_data.update(parsed_data)
            results.append(
                {
                    "entity": entity,
                    "file": file_path.name,
                    "expected_rows": expected_rows,
                }
            )

        bundle_hash = hashlib.sha256("|".join(file_hashes).encode("utf-8")).hexdigest()
        bundle_name = f"{dataset_dir.name}_bundle"
        batch_id = create_ingestion_batch(bundle_name, bundle_hash, "bundle")
        store_raw_records(batch_id, combined_parsed_data, bundle_name)
        with get_connection() as conn:
            with conn.cursor() as cur:
                total_rows = sum(item["expected_rows"] for item in results)
                cur.execute(
                    """
                    UPDATE core.ingestion_batches
                    SET total_rows = %s
                    WHERE id = %s
                    """,
                    (total_rows, batch_id),
                )
                conn.commit()

        accepted_rows, rejected_rows = process_batch_to_staging(batch_id)
        clean_counts = clean_batch(batch_id)
        core_counts = deduplicate_batch(batch_id)
        derived_stages = derive_missing_applied_stage(batch_id)
        derived_stages += derive_supporting_journey_events(batch_id)

        for item in results:
            item.update(
                {
                    "batch_id": batch_id,
                    "status": "journey_reconstructed",
                    "accepted_rows": accepted_rows,
                    "rejected_rows": rejected_rows,
                    "cleaned_rows": clean_counts,
                    "core_loaded": core_counts,
                    "derived_stages": derived_stages,
                }
            )
            print(
                f"{item['entity']}: expected={item['expected_rows']}, accepted={accepted_rows}, "
                f"rejected={rejected_rows}, status=journey_reconstructed"
            )
        return results

    for entity in ENTITY_ORDER:
        file_path = dataset_dir / f"{entity}.csv"
        if not file_path.exists():
            raise FileNotFoundError(f"Missing dataset file: {file_path}")

        expected_rows = count_csv_rows(file_path)
        response = upload_file(api_url, file_path)
        results.append(
            {
                "entity": entity,
                "file": file_path.name,
                "expected_rows": expected_rows,
                "batch_id": response.get("batch_id"),
                "status": response.get("status"),
                "total_rows": response.get("total_rows"),
                "accepted_rows": response.get("accepted_rows"),
                "rejected_rows": response.get("rejected_rows"),
                "cleaned_rows": response.get("cleaned_rows"),
                "core_loaded": response.get("core_loaded"),
                "derived_stages": response.get("derived_stages"),
            }
        )
        print(
            f"{entity}: expected={expected_rows}, accepted={response.get('accepted_rows')}, "
            f"rejected={response.get('rejected_rows')}, status={response.get('status')}"
        )
    return results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Reset the ingestion pipeline and load the large MVP dataset."
    )
    parser.add_argument(
        "--dataset",
        choices=["clean", "messy"],
        default="clean",
        help="Which generated dataset to load.",
    )
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000/uploads/",
        help="Upload endpoint used by the running backend.",
    )
    parser.add_argument(
        "--database-url",
        default=None,
        help="Database URL for the reset step. Defaults to DATABASE_URL or localhost fallback.",
    )
    parser.add_argument(
        "--skip-reset",
        action="store_true",
        help="Skip the database reset step.",
    )
    parser.add_argument(
        "--request-timeout",
        type=int,
        default=1800,
        help="Per-file HTTP timeout in seconds.",
    )
    parser.add_argument(
        "--transport",
        choices=["direct", "http"],
        default="direct",
        help="How to run the load. Direct is faster; http exercises the upload endpoint.",
    )
    parser.add_argument(
        "--run-id",
        default=None,
        help="Optional namespace label for log output.",
    )
    args = parser.parse_args()

    os.environ["MVP_UPLOAD_TIMEOUT"] = str(args.request_timeout)

    dataset_dir = Path(CURRENT_DIR) / "outputs" / args.dataset
    if not dataset_dir.exists():
        raise FileNotFoundError(f"Dataset directory not found: {dataset_dir}")

    if args.run_id:
        print(f"Seed run namespace: {args.run_id}")

    manifest = read_manifest(dataset_dir)
    database_url = get_database_url(args.database_url)

    if not args.skip_reset:
        print("Resetting pipeline tables...")
        truncate_pipeline_tables(database_url)

    print(f"Loading dataset from: {dataset_dir}")
    results = load_dataset(args.api_url, dataset_dir, args.transport, database_url)

    print("\nLoad summary:")
    for item in results:
        print(
            f"- {item['entity']}: batch={item['batch_id']} "
            f"accepted={item['accepted_rows']} rejected={item['rejected_rows']} "
            f"status={item['status']}"
        )

    if manifest:
        print("\nExpected funnel summary from manifest:")
        if args.dataset == "clean":
            summary = manifest.get("summary", {})
        else:
            summary = manifest.get("expected_results", {})
        for key, value in summary.items():
            if key in {"stage_counts", "supported_entities"}:
                print(f"- {key}: present")
            else:
                print(f"- {key}: {value}")


if __name__ == "__main__":
    main()
