from fastapi import FastAPI 
from prometheus_fastapi_instrumentator import Instrumentator 
from app.api import routes_auth, routes_predict 
from app.middleware import LoggingMiddleware 
from app.core.exceptions import register_exception_handlers 

app = FastAPI(title = 'Car price prediction API')  

app.add_middleware(LoggingMiddleware) 

app.inclue_router(routes_auth.router, tags = ['Auth']) 
app.include_router(router_predict.router, tags = ['Prediction']) 

Instrumentator().instrument(app).expose(app) 

