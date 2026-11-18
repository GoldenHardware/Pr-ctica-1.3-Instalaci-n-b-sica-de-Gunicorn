from fastapi import FastAPI

app = FastAPI(title="API practica 1.3", version="1.0.0")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/version")
def version():
    return {"app": "API practica 1.3", "version": app.version}


@app.get("/ping")
def ping():
    return {"message": "pong"}
