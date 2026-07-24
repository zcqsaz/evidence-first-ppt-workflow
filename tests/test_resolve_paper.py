import pytest

from scripts.resolve_paper import normalize_doi, resolve_paper


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code
        self.ok = status_code < 400
        self.text = "mock response"

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self):
        self.headers = {}

    def get(self, url, timeout):
        if "api.crossref.org" in url:
            return FakeResponse(
                {
                    "message": {
                        "title": ["Publisher article"],
                        "publisher": "Elsevier BV",
                        "container-title": ["Remote Sensing of Environment"],
                        "URL": "https://doi.org/10.1016/j.rse.2024.114000",
                        "link": [{"URL": "https://publisher.example/article.pdf", "content-type": "application/pdf"}],
                    }
                }
            )
        if "api.openalex.org" in url:
            return FakeResponse(
                {
                    "locations": [
                        {
                            "is_oa": True,
                            "version": "publishedVersion",
                            "pdf_url": "https://repository.example/article.pdf",
                            "landing_page_url": "https://repository.example/article",
                            "source": {"type": "repository"},
                        }
                    ]
                }
            )
        if "api.unpaywall.org" in url:
            return FakeResponse(
                {
                    "best_oa_location": {
                        "host_type": "repository",
                        "version": "acceptedVersion",
                        "license": "cc-by",
                        "url_for_pdf": "https://repository.example/article.pdf",
                        "url_for_landing_page": "https://repository.example/article",
                    },
                    "oa_locations": [],
                }
            )
        raise AssertionError(f"Unexpected URL: {url}")


def test_resolver_returns_metadata_and_candidates_without_downloads():
    report = resolve_paper("https://doi.org/10.1016/j.rse.2024.114000", email="researcher@example.edu", session=FakeSession())
    assert report["doi"] == "10.1016/j.rse.2024.114000"
    assert report["publisher_metadata"]["publisher"] == "Elsevier BV"
    assert any(item["kind"] == "publisher_landing_page" for item in report["candidate_access_locations"])
    assert any(item["kind"] == "open_access_pdf" for item in report["candidate_access_locations"])
    assert report["queries"][2]["source"] == "unpaywall"
    assert all(item.get("requires_access_check") for item in report["candidate_access_locations"])


def test_resolver_skips_unpaywall_without_email_and_rejects_invalid_doi():
    report = resolve_paper("10.1016/j.rse.2024.114000", session=FakeSession())
    assert report["queries"][2]["skipped"] is True
    with pytest.raises(ValueError):
        normalize_doi("not-a-doi")
