# Security Policy

## Supported versions

Security fixes are applied to the latest released minor version. Older versions may receive documentation-only notices.

## Reporting a vulnerability

Do not open a public issue for a vulnerability that could expose local files, credentials, unpublished research, or private presentation content. Contact the repository maintainers through the private security-reporting channel configured on the hosting platform.

Include the affected version, operating system, command, minimal reproduction and potential impact. Remove real credentials and confidential documents from the report.

## Threat model

This toolkit reads PPTX, CSV, JSON and image files and can optionally access URLs. Treat files and URLs from unknown sources as untrusted.

- Run the tools with normal user privileges;
- do not place secrets in metadata CSV files;
- review URLs before using `--check-urls`;
- use a disposable environment when processing untrusted Office files;
- keep Microsoft Office and Python dependencies patched;
- never enable macros merely to render a deck;
- inspect generated reports before publishing them because absolute local paths are included for auditability.

The PowerPoint renderer opens the input as read-only and does not intentionally run slide-show actions. It is not a malware scanner.
