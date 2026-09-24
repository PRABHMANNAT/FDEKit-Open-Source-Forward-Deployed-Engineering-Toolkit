# FastAPI inspection example

This is a small source/configuration example for `fdekit scan examples/fastapi-service`.
The scanner does not install or run this service. SERVICE_API_KEY is a synthetic
configuration contract; replace it only in your local untracked environment.

To run separately, create an isolated environment, install requirements.txt, and run
`uvicorn app:app --host 127.0.0.1 --port 8000`. GET /health returns a static status;
it does not verify upstream connectivity. Dependency constraints are illustrative and
should be reviewed before deploying. The Dockerfile runs as a non-root user.

Missing CI is intentional so the report provides a useful actionable finding.
