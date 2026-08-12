from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def read_root():
    return { "name": "Task API", "version": "1.0", "endpoints": ["/tasks"] }

@app.get("/health")
async def read_health():
    return { "status": "ok" }