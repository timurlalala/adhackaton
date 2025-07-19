import logging
from fastapi import FastAPI
import uvicorn
from app.characters_router import router as char_router
from app.messages_router import router as msg_router


logging.basicConfig(level=logging.DEBUG)

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "App healthy"}

app.include_router(char_router)
app.include_router(msg_router)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=False, host="0.0.0.0", log_level="info")