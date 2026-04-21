"""
MAS Sydney – Agent Scheduler
===============================
Background scheduler that runs agent workflows on a configurable schedule.

Schedule:
  ┌─────────────────────────────────────────────────────────────────────┐
  │ Phase          │ Frequency          │ Time (AEST)  │ Notes          │
  ├─────────────────────────────────────────────────────────────────────┤
  │ DCP Harvester  │ ONCE per council   │ Startup      │ run-once only  │
  │ Prospect+DA    │ Daily (Mon-Fri)    │ 06:00        │ ABS + trackers │
  │ Scout          │ Weekly (Monday)    │ 07:00        │ Domain scrape  │
  │ Survey         │ Weekly (Monday)    │ 08:00        │ GIS audit      │
  │ Full Cycle     │ On-demand only     │ API button   │ all phases     │
  └─────────────────────────────────────────────────────────────────────┘

The scheduler runs inside the FastAPI process via APScheduler.
"""

import asyncio
import logging
from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger("mas.scheduler")

_scheduler: AsyncIOScheduler | None = None


# ─── Scheduled Jobs ──────────────────────────────────────────

async def _startup_dcp_check():
    """Run DCP harvester for any councils not yet processed (run-once)."""
    logger.info("⏰ STARTUP DCP CHECK at %s", datetime.now().isoformat())
    try:
        from backend.workflows import run_dcp_phase
        result = await run_dcp_phase()
        logger.info("✅ DCP check: harvested=%s, skipped=%s",
                     result.get("harvested"), result.get("skipped"))
    except Exception as e:
        logger.error("❌ DCP check failed: %s", e, exc_info=True)


async def _daily_agent_run():
    """Runs prospect + DA scan phases daily at 06:00 AEST (Mon-Fri)."""
    logger.info("⏰ DAILY AGENT RUN at %s", datetime.now().isoformat())
    try:
        from backend.workflows import run_prospect_phase, run_da_scan_phase
        await run_prospect_phase()
        await run_da_scan_phase()
        logger.info("✅ Daily run completed")
    except Exception as e:
        logger.error("❌ Daily run failed: %s", e, exc_info=True)


async def _weekly_scout():
    """Runs property scout phase weekly on Monday at 07:00 AEST."""
    logger.info("⏰ WEEKLY SCOUT at %s", datetime.now().isoformat())
    try:
        from backend.workflows import run_scout_phase
        await run_scout_phase()
        logger.info("✅ Weekly scout completed")
    except Exception as e:
        logger.error("❌ Weekly scout failed: %s", e, exc_info=True)


async def _weekly_survey():
    """Runs geospatial survey phase weekly on Monday at 08:00 AEST (after scout)."""
    logger.info("⏰ WEEKLY SURVEY at %s", datetime.now().isoformat())
    try:
        from backend.workflows import run_survey_phase
        await run_survey_phase()
        logger.info("✅ Weekly survey completed")
    except Exception as e:
        logger.error("❌ Weekly survey failed: %s", e, exc_info=True)


# ─── Scheduler Lifecycle ─────────────────────────────────────

def start_scheduler():
    """Start the background scheduler with all scheduled jobs."""
    global _scheduler
    if _scheduler is not None:
        logger.info("Scheduler already running")
        return _scheduler

    _scheduler = AsyncIOScheduler(timezone="Australia/Sydney")

    # DCP: run once at startup (10 seconds after boot) — will skip already-harvested councils
    _scheduler.add_job(
        _startup_dcp_check,
        "date",
        run_date=datetime.now() + timedelta(seconds=30),
        id="startup_dcp_check",
        name="Startup DCP Check (run-once per council)",
        replace_existing=True,
    )

    # Daily: Prospect + DA Scan at 06:00 AEST (Mon-Fri)
    _scheduler.add_job(
        _daily_agent_run,
        CronTrigger(hour=6, minute=0, day_of_week="mon-fri", timezone="Australia/Sydney"),
        id="daily_prospect_da",
        name="Daily Prospect + DA Scan",
        replace_existing=True,
    )

    # Weekly: Scout on Monday at 07:00 AEST
    _scheduler.add_job(
        _weekly_scout,
        CronTrigger(hour=7, minute=0, day_of_week="mon", timezone="Australia/Sydney"),
        id="weekly_scout",
        name="Weekly Property Scout",
        replace_existing=True,
    )

    # Weekly: Survey on Monday at 08:00 AEST
    _scheduler.add_job(
        _weekly_survey,
        CronTrigger(hour=8, minute=0, day_of_week="mon", timezone="Australia/Sydney"),
        id="weekly_survey",
        name="Weekly Geospatial Survey",
        replace_existing=True,
    )

    _scheduler.start()
    logger.info(
        "📅 Scheduler started:\n"
        "  • DCP: at startup (run-once per council)\n"
        "  • Prospect + DA: daily 06:00 AEST Mon-Fri\n"
        "  • Scout: weekly Mon 07:00 AEST\n"
        "  • Survey: weekly Mon 08:00 AEST"
    )
    return _scheduler


def stop_scheduler():
    """Stop the background scheduler."""
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("Scheduler stopped")


def get_scheduler_status() -> dict:
    """Return current scheduler status and next run times."""
    if not _scheduler:
        return {"running": False, "jobs": []}

    jobs = []
    for job in _scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
            "trigger": str(job.trigger),
        })

    return {"running": _scheduler.running, "jobs": jobs}
