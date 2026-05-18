import logging

import uvicorn
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI

from app.api import router
from app.config import settings
from app.config.logging import setup_logging
from app.scheduler import run_increment

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="Power RAG")
app.include_router(router)

scheduler = BackgroundScheduler()


@app.on_event("startup")
def on_startup():
    # 启动时执行一次增量扫描
    run_increment()
    # 定时任务
    scheduler.add_job(run_increment, "interval", minutes=settings.SCAN_INTERVAL_MINUTES)
    scheduler.start()
    logger.info(f"Scheduler started, interval={settings.SCAN_INTERVAL_MINUTES}min")


@app.on_event("shutdown")
def on_shutdown():
    scheduler.shutdown()


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
