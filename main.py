# Root main.py forwarding to app.main:app for backward compatibility
from app.main import app

__all__ = ["app"]
