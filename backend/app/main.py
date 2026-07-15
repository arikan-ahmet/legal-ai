from fastapi import FastAPI

app = FastAPI(
    title="Legal AI API",
    description="Backend API for the Legal AI platform.",
    version="0.1.0",
)


@app.get("/")
def root():
    return {"message": "Legal AI API is running!"}