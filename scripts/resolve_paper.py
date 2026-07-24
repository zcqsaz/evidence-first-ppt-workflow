"""Resolve a DOI to publisher metadata and lawful open-access candidates.

This module deliberately performs metadata discovery only. It does not download
articles, manage publisher logins, or circumvent access controls.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests

try:
    from .common import TOOL_VERSION
except ImportError:
    from common import TOOL_VERSION

DOI_PATTERN = re.compile(r"^10\.\d{4,9}/\S+$", re.IGNORECASE)


def normalize_doi(value: str) -> str:
    doi = value.strip()
    doi = re.sub(r"^doi:\s*", "", doi, flags=re.IGNORECASE)
    doi = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", doi, flags=re.IGNORECASE)
    doi = doi.rstrip(". ,;)")
    if not DOI_PATTERN.match(doi):
        raise ValueError(f"Invalid DOI: {value}")
    return doi


def _query_json(session: requests.Session, source: str, url: str, timeout: float) -> dict[str, Any]:
    try:
        response = session.get(url, timeout=timeout)
        result: dict[str, Any] = {
            "source": source,
            "url": url,
            "status": response.status_code,
            "ok": response.ok,
        }
        if response.ok:
            result["data"] = response.json()
        else:
            result["error"] = response.text[:500]
        return result
    except (requests.RequestException, ValueError) as exc:
        return {"source": source, "url": url, "status": None, "ok": False, "error": str(exc)}


def _clean_text(value: Any) -> str | None:
    if isinstance(value, list):
        return " ".join(str(item) for item in value if item)
    return str(value) if value else None


def _append_candidate(candidates: list[dict[str, Any]], candidate: dict[str, Any]) -> None:
    url = candidate.get("url")
    if not url or not isinstance(url, str):
        return
    fingerprint = (url, candidate.get("kind"), candidate.get("version"))
    if fingerprint not in {(item.get("url"), item.get("kind"), item.get("version")) for item in candidates}:
        candidates.append(candidate)


def resolve_paper(doi: str, *, email: str | None = None, timeout: float = 20.0, session: requests.Session | None = None) -> dict[str, Any]:
    """Return metadata and lawful OA candidates for a DOI without downloading files."""
    normalized_doi = normalize_doi(doi)
    session = session or requests.Session()
    session.headers.setdefault(
        "User-Agent",
        f"Evidence-First-PPT-Workflow/{TOOL_VERSION} metadata-resolver" + (f" mailto:{email}" if email else ""),
    )
    encoded_doi = quote(normalized_doi, safe="")
    crossref = _query_json(session, "crossref", f"https://api.crossref.org/works/{encoded_doi}", timeout)
    openalex = _query_json(session, "openalex", f"https://api.openalex.org/works/https://doi.org/{encoded_doi}", timeout)
    unpaywall = (
        _query_json(session, "unpaywall", f"https://api.unpaywall.org/v2/{encoded_doi}?email={quote(email, safe='')}", timeout)
        if email
        else {"source": "unpaywall", "skipped": True, "reason": "--email is required by the Unpaywall API"}
    )

    publisher_metadata: dict[str, Any] = {}
    candidates: list[dict[str, Any]] = []
    if crossref.get("ok"):
        record = crossref["data"].get("message", {})
        publisher_metadata = {
            "title": _clean_text(record.get("title")),
            "publisher": record.get("publisher"),
            "journal": _clean_text(record.get("container-title")),
            "published": record.get("published-print") or record.get("published-online") or record.get("issued"),
            "article_type": record.get("type"),
            "publisher_landing_page": record.get("URL"),
        }
        _append_candidate(candidates, {"kind": "publisher_landing_page", "url": record.get("URL"), "source": "crossref", "requires_access_check": True})
        for link in record.get("link", []) or []:
            _append_candidate(
                candidates,
                {
                    "kind": "publisher_link",
                    "url": link.get("URL"),
                    "content_type": link.get("content-type"),
                    "intended_application": link.get("intended-application"),
                    "source": "crossref",
                    "requires_access_check": True,
                },
            )

    if unpaywall.get("ok"):
        record = unpaywall["data"]
        for location in [record.get("best_oa_location"), *(record.get("oa_locations") or [])]:
            if not location:
                continue
            common = {
                "source": "unpaywall",
                "host_type": location.get("host_type"),
                "version": location.get("version"),
                "license": location.get("license"),
                "requires_access_check": True,
            }
            _append_candidate(candidates, {**common, "kind": "open_access_pdf", "url": location.get("url_for_pdf")})
            _append_candidate(candidates, {**common, "kind": "open_access_landing_page", "url": location.get("url_for_landing_page")})

    if openalex.get("ok"):
        record = openalex["data"]
        for location in record.get("locations") or []:
            common = {
                "source": "openalex",
                "version": location.get("version"),
                "is_oa": location.get("is_oa"),
                "host_type": (location.get("source") or {}).get("type"),
                "requires_access_check": True,
            }
            _append_candidate(candidates, {**common, "kind": "openalex_pdf", "url": location.get("pdf_url")})
            _append_candidate(candidates, {**common, "kind": "openalex_landing_page", "url": location.get("landing_page_url")})

    return {
        "tool": "resolve_paper",
        "tool_version": TOOL_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "doi": normalized_doi,
        "doi_url": f"https://doi.org/{normalized_doi}",
        "publisher_metadata": publisher_metadata,
        "candidate_access_locations": candidates,
        "queries": [crossref, openalex, unpaywall],
        "limitations": [
            "Candidate locations are leads, not verified download permissions.",
            "Open each candidate in a normal browser and verify title, version, figure number and rights before use.",
            "This tool does not download full text, log in to publishers, solve CAPTCHAs or bypass access controls.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Resolve a DOI to publisher metadata and lawful open-access candidates without downloading articles.")
    parser.add_argument("doi")
    parser.add_argument("--email", help="Research contact email required by the Unpaywall API; never stored in output except as an API request parameter.")
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        report = resolve_paper(args.doi, email=args.email, timeout=args.timeout)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(args.output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
