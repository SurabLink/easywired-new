from fastapi import FastAPI

app = FastAPI(title="easyWIRED static site")


@app.get("/api/")
async def health() -> dict:
    return {"status": "ok", "service": "easywired-static"}
