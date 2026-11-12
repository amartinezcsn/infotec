from __future__ import annotations

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import db, settings
from app.main import app


@pytest.fixture()
def client(tmp_path: Path):
    test_db = tmp_path / "test.db"
    upload_dir = tmp_path / "uploads"
    db.DB_PATH = test_db
    settings.DB_PATH = test_db
    settings.UPLOAD_DIR = upload_dir
    import app.services.payment as payment

    payment.UPLOAD_DIR = upload_dir
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def admin_headers():
    return {"X-Demo-Admin": "cupcake-demo-admin"}

