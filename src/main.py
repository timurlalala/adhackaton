import logging
from fastapi import FastAPI
import uvicorn
from app.router import router

logging.basicConfig(level=logging.DEBUG)

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "App healthy"}

app.include_router(router)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=False, host="0.0.0.0", log_level="info")