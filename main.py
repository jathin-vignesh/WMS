from fastapi import FastAPI
from db import Base, engine
from app import route

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sales & Order Management Service")

app.include_router(route.router)

@app.get('/')
def greet():
    return "welcome to WMS!"