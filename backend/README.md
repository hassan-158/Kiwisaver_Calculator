run api.py with the following:
    uv run uvicorn backend.api:app --reload

for deployment on render.com dashboard:
Build:
    uv sync --frozen && uv cache prune --ci
Deploy:
    uv run uvicorn api:app --host 0.0.0.0 --port $PORT