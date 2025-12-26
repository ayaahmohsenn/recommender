from fastapi import FastAPI

app = FastAPI(title="Feed Recommender API")

@app.get("/health")
def health():
    return {"status": "ok", "service": "fastapi"}