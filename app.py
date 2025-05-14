from fastapi import FastAPI
from api.v2 import users_router_v2


mock_app = FastAPI()
mock_app.include_router(users_router_v2, prefix="/api")
