#!/usr/bin/env python3
# main.py  — Entry point
import os
import uvicorn
from dotenv import load_dotenv

load_dotenv()

if not os.getenv("GROQ_API_KEY"):
    raise SystemExit("❌  GROQ_API_KEY chưa được cấu hình. Thêm vào file .env")

from src.app import create_app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("ENV", "development") == "development",
        log_level="info",
    )
