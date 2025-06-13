import asyncio
import os

from loguru import logger

from models import Payload, ReportBasic
from plugins.mongo.client import MongoClient
from plugins.mongo.models import AssetBase, CollectionAssets
from plugins.slack.publisher import SlackPublisher
from plugins.storage import StorageClient
from utilities import (
    append_to_csv_report,
    extract_blob_name_from_blob_id,
    extract_bucket_name_from_blob_id,
    gen_csv_report,
)

SCRIPT_NAME = os.path.basename(__file__).replace(".py", "")
storage_client = StorageClient()
mongo_client = MongoClient()


def initialize_report() -> tuple[ReportBasic, str]:
    """Initialize the report and generate the filename."""
    report = ReportBasic(
        report_name=f"{SCRIPT_NAME}_report",
        column_names=[
            "manufacturer_id",
            "manufacturer_status",
            "entity_type",
            "entity_id",
            "entity_status",
            "field_name",
            "asset_status",
            "asset_description",
            "blob_id",
            "removed_blob_id",
        ],
        data=[],
    )
    report_filename = gen_csv_report(report)
    return report, report_filename


def process_blob(
    blob_id: str,
    collection_id: int,
    collection_status: str,
    field_name: str,
    asset_status: str,
    asset_description: str,
    report: ReportBasic,
    dry_run: bool,
    manufacturer_id: int,
    manufacturer_status: str,
) -> None:
    """Check if a blob exists and handle if missing."""
    bucket_name = extract_bucket_name_from_blob_id(blob_id)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(extract_blob_name_from_blob_id(blob_id))
    logger.debug(f"Checking blob: {blob_id} - status: {asset_status}")
    removed_blob_id = ""
    if not blob.exists():
        logger.warning(f"Missing blob: {blob_id}")
        # Only set removed_blob_id when not in dry_run mode
        if not dry_run:
            removed_blob_id = blob_id
            # mongo_client.pull_asset_from_list(
            #     blob_id,
            #     collection_id,
            #     "collection_id",
            #     field_name,
            #     "collections",
            # )
            logger.warning(f"Removed blob: {removed_blob_id}")
        append_to_csv_report(
            report,
            [
                str(manufacturer_id),
                str(manufacturer_status),
                "collection",
                str(collection_id),
                str(collection_status),
                str(field_name),
                str(asset_status),
                str(asset_description),
                blob_id,
                removed_blob_id,
            ],
        )


def handle_null_blob(
    report: ReportBasic,
    collection_id: int,
    collection_status: str,
    field_name: str,
    asset_status: str,
    asset_description: str,
    manufacturer_id: int,
    manufacturer_status: str,
) -> None:
    """Handle case when blob_id is None by logging warning and appending to report."""
    logger.warning(
        f"Skipping {field_name} with None blob_id for collection_id: {collection_id}"
    )
    # Report null blob_id in CSV
    append_to_csv_report(
        report,
        [
            str(manufacturer_id),
            str(manufacturer_status),
            "collection",
            str(collection_id),
            str(collection_status),
            field_name,
            str(asset_status),
            str(asset_description),
            "",
            "",
        ],
    )


def process_single_asset(
    asset: AssetBase,
    field_name: str,
    collection_id: int,
    collection_status: str,
    report: ReportBasic,
    dry_run: bool,
    manufacturer_id: int,
    manufacturer_status: str,
) -> None:
    """Process a single asset and check if its blob exists in storage."""
    asset_description = asset.description or ""
    if asset.blob_id is None:
        handle_null_blob(
            report,
            collection_id,
            collection_status,
            field_name,
            asset.status,
            asset_description,
            manufacturer_id,
            manufacturer_status,
        )
    else:
        process_blob(
            blob_id=asset.blob_id,
            collection_id=collection_id,
            collection_status=collection_status,
            field_name=field_name,
            asset_status=asset.status,
            asset_description=asset_description,
            report=report,
            dry_run=dry_run,
            manufacturer_id=manufacturer_id,
            manufacturer_status=manufacturer_status,
        )


def process_collection_assets(
    collection_assets: CollectionAssets,
    report: ReportBasic,
    dry_run: bool,
    manufacturer_id: int,
    manufacturer_status: str,
) -> None:
    """Process each asset type in collection data."""
    collection_id = collection_assets.collection_id
    collection_status = collection_assets.status
    logger.info(
        f"Processing collection_id: {collection_id} - status: {collection_status}"
    )
    # Process image assets
    for image in collection_assets.images:
        process_single_asset(
            image,
            "images",
            collection_id,
            collection_status,
            report,
            dry_run,
            manufacturer_id,
            manufacturer_status,
        )


def process_manufacturer_collections(
    manufacturers_with_status: list[dict], report: ReportBasic, dry_run: bool
) -> None:
    """Process collections for the specified manufacturers."""
    for manufacturer in manufacturers_with_status:
        manufacturer_id = manufacturer["manufacturer_id"]
        manufacturer_status = manufacturer.get("status", "")
        logger.info(f"Started: {manufacturer_id} {SCRIPT_NAME}")
        collection_assets_list = mongo_client.get_blobs_from_collection_assets(
            manufacturer_id
        )
        for collection_assets in collection_assets_list:
            process_collection_assets(
                collection_assets,
                report,
                dry_run,
                manufacturer_id,
                manufacturer_status,
            )


def upload_report(report_filename: str, report: ReportBasic, dry_run: bool) -> None:
    """Upload report to storage and notify on Slack."""
    blob_id = storage_client.upload_file_to_reports_bucket(report_filename, SCRIPT_NAME)
    if blob_id:
        logger.info(f"Report uploaded to storage: {blob_id}")
        SlackPublisher.script_completed(
            script_name=SCRIPT_NAME,
            dry_run=dry_run,
            output_file_blob_id=blob_id,
            report=report,
        )


async def main(payload_dict: dict):
    try:
        payload = Payload.model_validate(payload_dict)
        SlackPublisher.script_started(script_name=SCRIPT_NAME, dry_run=payload.dry_run)
        report, report_filename = initialize_report()
        manufacturers_with_status = mongo_client.get_manufacturer_ids_with_status()
        process_manufacturer_collections(
            manufacturers_with_status, report, payload.dry_run
        )
        upload_report(report_filename, report, payload.dry_run)

        logger.info(f"Completed {SCRIPT_NAME}")
    except Exception as e:

        logger.error(f"Failed to complete {SCRIPT_NAME}: {e}")
        SlackPublisher.script_failed(
            script_name=SCRIPT_NAME, dry_run=payload.dry_run, error_message=str(e)
        )
        raise e


if __name__ == "__main__":
    asyncio.run(main({}))