"""Production Health Checks, Probes, and Telemetry Endpoints."""

import time
import os
import resource
from typing import Dict, Any, List
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from backend.app.db.session import get_db, check_db_connection
from backend.app.core.platform_adapters import PlatformRegistry
from backend.app.ai.registry.model_registry import ModelRegistryManager

router = APIRouter(prefix="/health", tags=["Production Health & Diagnostics"])

START_TIME = time.time()


@router.get("/liveness")
async def liveness_probe():
    """Kubernetes liveness probe indicating process is alive."""
    return {
        "status": "alive",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime_seconds": int(time.time() - START_TIME),
    }


@router.get("/readiness")
async def readiness_probe(db: AsyncSession = Depends(get_db)):
    """Kubernetes readiness probe verifying DB connectivity, Platform Registry, and Model Registry."""
    db_ok = False
    try:
        await db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    platforms = PlatformRegistry.list_platforms()
    models_count = len(ModelRegistryManager.DEFAULT_CATALOG)

    is_ready = db_ok and len(platforms) >= 5 and models_count >= 6

    res = {
        "status": "ready" if is_ready else "not_ready",
        "database": "connected" if db_ok else "unreachable",
        "registered_platforms_count": len(platforms),
        "registered_models_count": models_count,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    if not is_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=res,
        )

    return res


@router.get("/telemetry")
async def system_telemetry():
    """Comprehensive production system telemetry (memory, CPU, platform, model stats)."""
    # Use standard library resource usage
    usage = resource.getrusage(resource.RUSAGE_SELF)
    max_rss_mb = round(usage.ru_maxrss / 1024.0, 2)  # Linux ru_maxrss is in KB

    return {
        "service": "AISMM Universal Backend",
        "version": "1.0.0",
        "uptime_seconds": int(time.time() - START_TIME),
        "process": {
            "pid": os.getpid(),
            "max_rss_memory_mb": max_rss_mb,
            "user_cpu_time_s": round(usage.ru_utime, 2),
            "system_cpu_time_s": round(usage.ru_stime, 2),
        },
        "platforms": {
            "count": len(PlatformRegistry.list_platforms()),
            "list": PlatformRegistry.list_platforms(),
        },
        "models": {
            "count": len(ModelRegistryManager.DEFAULT_CATALOG),
            "active": [m["model_name"] for m in ModelRegistryManager.DEFAULT_CATALOG],
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
