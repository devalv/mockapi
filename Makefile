dev:
	poetry run uvicorn "app:mock_app" --lifespan on --port 8000 --host 0.0.0.0  --workers 1  --reload  --log-config "log_cfg_debug.yaml"
