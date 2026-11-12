from __future__ import annotations

import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = Path(os.getenv("CUPCAKE_DATA_DIR", ROOT / "data"))
DB_PATH = Path(os.getenv("CUPCAKE_DB_PATH", DATA_DIR / "app.db"))
UPLOAD_DIR = Path(os.getenv("CUPCAKE_UPLOAD_DIR", DATA_DIR / "uploads"))
POLICY_DIR = Path(os.getenv("CUPCAKE_POLICY_DIR", DATA_DIR / "delivery-policies"))
FOUNDRY_ENDPOINT = os.getenv("FOUNDRY_PROJECT_ENDPOINT", "").strip()
DEMO_ADMIN_TOKEN = os.getenv("DEMO_ADMIN_TOKEN", "cupcake-demo-admin")
ALLOWED_CATEGORIES = {
    "pasteles-personalizados",
    "cupcakes",
    "galletas-decoradas",
}


def ensure_runtime_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

