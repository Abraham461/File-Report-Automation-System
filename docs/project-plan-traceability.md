# Project Plan Traceability Matrix

This document maps implemented FRAS features and deliverables to the milestones defined in the project plan.

## Milestone-to-feature mapping

| Project milestone (from project plan) | Implemented feature / artifact | Traceability evidence |
|---|---|---|
| Requirement collection completed | Core functional scope documented around upload/search/reporting/authentication workflows | `docs/user-guide.md` sections 1-4; test coverage by service and API suites |
| System design finalized | Deployment topology and environment variables standardized for production | `docs/deployment.md` environment + runtime sections |
| Core file management module completed | File upload and search coverage in tests (unit + integration + UI flow checks) | `tests/unit/test_file_service.py`, `tests/integration/test_upload_api.py`, `tests/integration/test_search_api.py`, `tests/ui/test_critical_flows.py` |
| Reporting module implemented | Report validation/generation logic coverage + report endpoint integration checks | `tests/unit/test_report_service.py`, `tests/integration/test_report_api.py` |
| Testing completed | Structured test suites added for unit, integration, and critical UI routes | `tests/unit/*`, `tests/integration/*`, `tests/ui/test_critical_flows.py` |
| System deployment and user training | Deployment runbook + end-user operational guide with step-by-step instructions and visuals | `docs/deployment.md`, `docs/user-guide.md`, `docs/assets/*.svg` |

## Coverage summary

### Unit tests
- Authentication service contract checks (`hash`, `verify`, `authenticate`).
- File service checks (`store`, `find`, `search`, `delete`).
- Report service checks (`validate`, `generate`).

### Integration tests
- Upload API endpoint reachability and validation handling.
- Search API endpoint reachability and query execution behavior.
- Report API endpoint reachability and invalid payload handling.

### UI tests
- Critical route/page availability for login, upload, search, and report generation pages.

## Notes
- Integration and UI tests are environment-driven and run when `FRAS_BASE_URL` is configured.
- The matrix can be expanded with commit hashes, issue IDs, and acceptance criteria once project tracking tooling is connected.
