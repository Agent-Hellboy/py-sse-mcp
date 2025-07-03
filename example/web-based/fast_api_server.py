import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()


@app.get("/hello")
async def hello():
    return JSONResponse({"message": "Hello from FastAPI!"})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5005)
