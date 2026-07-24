from __future__ import annotations

import argparse
import csv
import mimetypes
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse

import requests
from PIL import Image, UnidentifiedImageError

try:
    from .common import build_report, issue, resource_path, sha256_file, validate_json, write_report
except ImportError:
    from common import build_report, issue, resource_path, sha256_file, validate_json, write_report

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".gif", ".webp"}
REQUIRED_COLUMNS = {
    "filename",
    "case_name",
    "ppt_page",
    "figure_title",
    "source_type",
    "source_organization",
    "source_title",
    "publication_year",
    "source_url",
    "license_or_usage_note",
    "verification_status",
}
DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$", re.IGNORECASE)


def _safe_asset_path(asset_root: Path, filename: str) -> Path | None:
    try:
        candidate = (asset_root / filename).resolve()
        candidate.relative_to(asset_root.resolve())
        return candidate
    except (OSError, ValueError):
        return None


def _valid_http_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _check_url(session: requests.Session, url: str, timeout: float) -> tuple[int | None, str, str]:
    try:
        response = session.head(url, allow_redirects=True, timeout=timeout)
        if response.status_code in {403, 405} or response.status_code >= 500:
            response = session.get(url, allow_redirects=True, timeout=timeout, stream=True)
        return response.status_code, response.headers.get("content-type", ""), str(response.url)
    except requests.RequestException as exc:
        return None, "", str(exc)


def validate_sources(
    csv_path: Path,
    asset_root: Path,
    *,
    check_urls: bool = False,
    strict_network: bool = False,
    timeout: float = 15.0,
) -> dict:
    issues: list[dict] = []
    csv_path = csv_path.resolve()
    asset_root = asset_root.resolve()
    if not csv_path.is_file():
        return build_report("validate_sources", csv_path, [issue("error", "CSV_NOT_FOUND", f"Metadata CSV not found: {csv_path}")])
    if not asset_root.is_dir():
        return build_report("validate_sources", csv_path, [issue("error", "ASSET_ROOT_NOT_FOUND", f"Asset root not found: {asset_root}")])

    try:
        with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            fieldnames = reader.fieldnames or []
            rows = list(reader)
    except (OSError, UnicodeError, csv.Error) as exc:
        return build_report("validate_sources", csv_path, [issue("error", "CSV_READ_ERROR", str(exc))])

    missing_columns = sorted(REQUIRED_COLUMNS - set(fieldnames))
    if missing_columns:
        issues.append(issue("error", "MISSING_COLUMNS", f"Missing required columns: {', '.join(missing_columns)}"))

    schema_path = resource_path("schemas/source_metadata.schema.json")
    seen_filenames: dict[str, int] = {}
    seen_asset_ids: dict[str, int] = {}
    content_hash_rows: defaultdict[str, list[int]] = defaultdict(list)
    file_hashes: dict[str, str] = {}
    image_dimensions: dict[str, list[int]] = {}
    url_cache: dict[str, tuple[int | None, str, str]] = {}
    url_contexts: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    session = requests.Session()
    session.headers.update({"User-Agent": "Evidence-First-PPT-Workflow/1.0 source-audit"})

    for row_number, raw_row in enumerate(rows, start=2):
        row = {key: (value or "").strip() for key, value in raw_row.items() if key is not None}
        for message in validate_json(row, schema_path):
            issues.append(issue("error", "SCHEMA_VIOLATION", f"Row {row_number}: {message}", details={"row": row_number}))

        filename = row.get("filename", "")
        if filename:
            normalized = filename.replace("\\", "/").casefold()
            if normalized in seen_filenames:
                issues.append(issue("error", "DUPLICATE_FILENAME", f"Rows {seen_filenames[normalized]} and {row_number} use the same filename: {filename}"))
            else:
                seen_filenames[normalized] = row_number

        asset_id = row.get("asset_id", "")
        if asset_id:
            normalized_id = asset_id.casefold()
            if normalized_id in seen_asset_ids:
                issues.append(issue("error", "DUPLICATE_ASSET_ID", f"Rows {seen_asset_ids[normalized_id]} and {row_number} use the same asset_id: {asset_id}"))
            else:
                seen_asset_ids[normalized_id] = row_number

        path = _safe_asset_path(asset_root, filename) if filename else None
        if path is None:
            issues.append(issue("error", "UNSAFE_ASSET_PATH", f"Row {row_number} leaves the asset root: {filename}"))
        elif not path.is_file():
            issues.append(issue("error", "ASSET_NOT_FOUND", f"Row {row_number} file not found: {filename}"))
        else:
            digest = sha256_file(path)
            file_hashes[filename] = digest
            content_hash_rows[digest].append(row_number)
            declared_hash = row.get("file_sha256", "")
            if declared_hash and digest.casefold() != declared_hash.casefold():
                issues.append(issue("error", "HASH_MISMATCH", f"Row {row_number} SHA-256 does not match file: {filename}"))
            if path.suffix.lower() in IMAGE_SUFFIXES:
                try:
                    with Image.open(path) as image:
                        width, height = image.size
                    image_dimensions[filename] = [width, height]
                    if max(width, height) < 700:
                        issues.append(issue("warning", "LOW_RESOLUTION", f"Row {row_number} image long edge is below 700 px: {filename} ({width}×{height})"))
                except (UnidentifiedImageError, OSError) as exc:
                    issues.append(issue("error", "IMAGE_READ_ERROR", f"Row {row_number} image cannot be decoded: {filename}: {exc}"))

        doi = row.get("doi", "")
        if doi:
            doi = doi.removeprefix("https://doi.org/").removeprefix("http://doi.org/")
            if not DOI_RE.match(doi):
                issues.append(issue("error", "INVALID_DOI", f"Row {row_number} DOI is not valid: {row.get('doi')}"))

        for column in ("source_url", "download_url"):
            url = row.get(column, "")
            if url and not _valid_http_url(url):
                issues.append(issue("error", "INVALID_URL", f"Row {row_number} {column} is not an HTTP(S) URL: {url}"))
            elif url and check_urls:
                url_contexts[url].append({"row": row_number, "column": column})
                if url not in url_cache:
                    url_cache[url] = _check_url(session, url, timeout)

        verification = row.get("verification_status", "").casefold()
        if "未核验" in verification or "不建议" in verification or "unverified" in verification:
            issues.append(issue("error", "UNVERIFIED_ASSET", f"Row {row_number} is not verified for formal use: {row.get('verification_status')}"))
        elif not any(token in verification for token in ("已核验", "verified", "可用", "需补充")):
            issues.append(issue("warning", "UNKNOWN_VERIFICATION_STATUS", f"Row {row_number} uses an unrecognized verification status: {row.get('verification_status')}"))

    for digest, row_numbers in content_hash_rows.items():
        if len(row_numbers) > 1:
            issues.append(issue("error", "DUPLICATE_FILE_CONTENT", f"Rows {row_numbers} contain identical asset bytes.", details={"sha256": digest, "rows": row_numbers}))

    url_results: dict[str, dict[str, object]] = {}
    for url, (status, content_type, final_value) in url_cache.items():
        contexts = url_contexts[url]
        rows_for_url = sorted({int(context["row"]) for context in contexts})
        columns_for_url = sorted({str(context["column"]) for context in contexts})
        url_results[url] = {
            "status": status,
            "content_type": content_type,
            "final_url_or_error": final_value,
            "rows": rows_for_url,
            "columns": columns_for_url,
        }
        if status is None or status >= 400:
            severity = "error" if strict_network else "warning"
            issues.append(issue(severity, "URL_UNREACHABLE", f"URL used by rows {rows_for_url} could not be verified: {url}", details=url_results[url]))
        elif "download_url" in columns_for_url and content_type and not any(token in content_type.casefold() for token in ("image", "pdf", "octet-stream")):
            issues.append(issue("warning", "DOWNLOAD_MIME_SUSPECT", f"download_url used by rows {rows_for_url} returned {content_type}: {url}", details=url_results[url]))

    metrics = {
        "row_count": len(rows),
        "column_count": len(fieldnames),
        "files_found": len(file_hashes),
        "unique_file_hashes": len(content_hash_rows),
        "unique_urls_checked": len(url_cache),
        "url_results": url_results,
        "file_sha256": file_hashes,
        "image_dimensions": image_dimensions,
        "issue_codes": dict(Counter(item["code"] for item in issues)),
    }
    return build_report("validate_sources", csv_path, issues, metrics)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate evidence metadata, files, hashes, DOI/URL fields and verification status.")
    parser.add_argument("metadata_csv", type=Path)
    parser.add_argument("--asset-root", type=Path, required=True)
    parser.add_argument("--check-urls", action="store_true")
    parser.add_argument("--strict-network", action="store_true", help="Treat unreachable URLs as errors instead of warnings.")
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args(argv)
    report = validate_sources(
        args.metadata_csv,
        args.asset_root,
        check_urls=args.check_urls,
        strict_network=args.strict_network,
        timeout=args.timeout,
    )
    write_report(report, args.report)
    return 1 if report["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
