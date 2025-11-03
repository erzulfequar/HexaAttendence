"""
ASGI config for hexaattendanceportal project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
import sys

# Add the fastapi_api directory to Python path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fastapi_api'))

from django.core.asgi import get_asgi_application
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hexaattendanceportal.settings')

# Import the FastAPI app from fastapi_api/main.py
from fastapi_app.main import app as fastapi_app

@fastapi_app.get("/api/health")
def health_check():
    return {"status": "ok"}

# Mount Django under FastAPI
fastapi_app.mount("/", WSGIMiddleware(get_asgi_application()))

# Entry point for uvicorn
application = fastapi_app
