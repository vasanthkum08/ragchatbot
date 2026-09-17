import uvicorn
import config

if __name__ == "__main__":
    print(f"🚀 Starting FastAPI Backend Server on http://{config.FASTAPI_HOST}:{config.FASTAPI_PORT}")
    uvicorn.run("backend.main:app", host=config.FASTAPI_HOST, port=config.FASTAPI_PORT, reload=True)
