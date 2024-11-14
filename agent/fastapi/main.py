from fastapi import FastAPI
from routers import router  # Import the router for endpoint routes

app = FastAPI()

# Include the router from routers.py
app.include_router(router)

# Root endpoint for the app
@app.get("/")
async def read_root():
    return {"message": "Welcome to the Document Selection API!"}
