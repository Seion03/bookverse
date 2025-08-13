from fastapi import FastAPI

app =FastAPI()

@app.get("/")
async def health():
    return {"status": "ok", "server": "running"}

@app.get("/user/sample")
async def sample_user():
    return [{"id":1, "name":"seion"}]

