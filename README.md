# Práctica 1.3: instalación básica de Gunicorn

Despliegue de aplicaciones web, 2º DAW. Javier Doñoro Garcia.

Backend sencillo en FastAPI servido con Gunicorn y el worker de Uvicorn en 127.0.0.1:8000, con los endpoints /health, /version y /ping.

La documentación completa, con los pasos y las capturas, está en [docs/gunicorn.md](gunicorn.md).

Para arrancarlo:

```bash
python3.13 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
gunicorn app.main:app --worker-class uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000
```
