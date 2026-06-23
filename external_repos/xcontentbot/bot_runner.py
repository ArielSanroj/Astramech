"""Bot runner with scheduling and main loop."""
import asyncio
import time
import logging
from datetime import datetime
from typing import Dict, List, Tuple

import httpx
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from client_config import (
    QUERIES, LIMIT, MAX_POSTS_TO_PROCESS, AUTO,
    ENABLE_SCHEDULER, RUN_ON_STARTUP, SCHEDULE_TZ, SCHEDULE_CRON,
    POST_PROCESSING_SEMAPHORE
)
from bot_state import bot_state
from api_client import fetch_posts, get_post, draft_comment, submit_comment, refine_with_ai

logger = logging.getLogger("x-mcp-client")


async def process_post(client: httpx.AsyncClient, post: Dict, auto: bool) -> Tuple[str, str]:
    """Process a single post with concurrency control and duplicate prevention."""
    pid = post.get("id", "")

    if bot_state.is_post_processed(pid):
        logger.debug("Skipping already processed post: %s", pid)
        return ("skipped", f"{pid}: already processed")

    async with POST_PROCESSING_SEMAPHORE:
        try:
            logger.debug("Processing post: %s", pid)
            full_post = await get_post(client, pid)
            if not full_post.get("text"):
                bot_state.mark_post_processed(pid, posted=False)
                return ("skipped", f"{pid}: no text")

            draft = await draft_comment(client, pid)
            comment = (draft or {}).get("comment", "").strip()
            if not comment:
                bot_state.mark_post_processed(pid, posted=False)
                return ("skipped", f"{pid}: no draft")

            refined = await refine_with_ai(comment)
            res = await submit_comment(client, pid, refined, auto=auto)

            posted = res.get("status") == "posted"
            bot_state.mark_post_processed(pid, posted=posted)

            if posted:
                logger.info("Successfully posted to %s: %s", pid, res)
            else:
                logger.info("Processed %s (status: %s): %s", pid, res.get("status", "unknown"), res)

            return (res.get("status", "error"), f"{pid}: {res}")
        except Exception as e:
            logger.exception("process_post(%s) failed", pid)
            bot_state.mark_post_processed(pid, posted=False)
            return ("error", f"{pid}: {e}")


async def process_keyword(client: httpx.AsyncClient, query: str, limit: int, max_posts: int, auto: bool) -> Dict:
    """Process posts for a keyword with improved concurrency control and logging."""
    start_time = time.time()
    logger.info("Processing query: %s (limit: %d, max_posts: %d, auto: %s)", query, limit, max_posts, auto)

    posts = await fetch_posts(client, query, limit)
    if not posts:
        logger.warning("No posts fetched for '%s'. Check MCP server logs.", query)
        return {"query": query, "posted": 0, "preview": 0, "skipped": 0, "errors": 0, "duration": 0}

    new_posts = [p for p in posts if not bot_state.is_post_processed(p.get("id", ""))]
    if not new_posts:
        logger.info("All posts for '%s' have already been processed", query)
        return {"query": query, "posted": 0, "preview": 0, "skipped": 0, "errors": 0, "duration": 0}

    to_process = new_posts[:max_posts]
    logger.info("Processing %d new posts for '%s' (filtered from %d total)", len(to_process), query, len(posts))

    tasks = [process_post(client, p, auto) for p in to_process]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    summary = {"query": query, "posted": 0, "preview": 0, "skipped": 0, "errors": 0}
    for result in results:
        if isinstance(result, Exception):
            summary["errors"] += 1
            logger.error("Task failed for %s: %s", query, result)
        else:
            status, detail = result
            if status == "posted":
                summary["posted"] += 1
            elif status == "preview":
                summary["preview"] += 1
            elif status == "skipped":
                summary["skipped"] += 1
            else:
                summary["errors"] += 1
            logger.info("[%s] %s", query, detail)

    duration = time.time() - start_time
    summary["duration"] = round(duration, 2)

    logger.info("[%s] Summary - posted=%d, preview=%d, skipped=%d, errors=%d, duration=%.2fs",
                query, summary["posted"], summary["preview"], summary["skipped"], summary["errors"], duration)
    return summary


async def run_once() -> List[Dict]:
    """Run the bot once for all configured queries."""
    run_start_time = time.time()
    logger.info("Starting bot run (queries: %s, auto: %s)", QUERIES, AUTO)

    bot_state.last_run_time = datetime.now()
    bot_state.save_state()

    summaries = []
    total_posts_before = bot_state.total_posts_processed
    total_posted_before = bot_state.total_posts_posted

    async with httpx.AsyncClient() as client:
        for i, q in enumerate(QUERIES, 1):
            try:
                logger.info("Processing query %d/%d: %s", i, len(QUERIES), q)
                s = await process_keyword(client, q, LIMIT, MAX_POSTS_TO_PROCESS, AUTO)
                summaries.append(s)
            except Exception as e:
                logger.exception("Keyword loop crashed for '%s'", q)
                summaries.append({
                    "query": q, "posted": 0, "preview": 0, "skipped": 0, "errors": 1,
                    "duration": 0, "detail": str(e)
                })

    run_duration = time.time() - run_start_time
    total_posts_this_run = bot_state.total_posts_processed - total_posts_before
    total_posted_this_run = bot_state.total_posts_posted - total_posted_before

    logger.info("Bot run completed in %.2fs", run_duration)
    logger.info("Run statistics: %d posts processed, %d posted (total: %d processed, %d posted)",
                total_posts_this_run, total_posted_this_run, bot_state.total_posts_processed, bot_state.total_posts_posted)

    for summary in summaries:
        if "duration" in summary:
            logger.info("  %s: %d posted, %d preview, %d skipped, %d errors (%.2fs)",
                        summary["query"], summary["posted"], summary["preview"],
                        summary["skipped"], summary["errors"], summary["duration"])

    return summaries


def schedule_client():
    """Set up the scheduler with comprehensive logging and next run tracking."""
    tz = pytz.timezone(SCHEDULE_TZ)
    scheduler = AsyncIOScheduler(timezone=tz)

    try:
        minute, hour, dom, mon, dow = SCHEDULE_CRON.split()
        trigger = CronTrigger(minute=minute, hour=hour, day=dom, month=mon, day_of_week=dow, timezone=tz)
    except ValueError:
        logger.warning("Invalid CRON format '%s', falling back to 08:00 daily", SCHEDULE_CRON)
        trigger = CronTrigger(minute=0, hour=8, timezone=tz)

    def scheduled_job():
        """Wrapper for the scheduled job with enhanced logging."""
        job_start = time.time()
        logger.info("Scheduled job started")

        asyncio.create_task(run_once())

        next_run = trigger.get_next_fire_time(None, datetime.now(tz))
        if next_run:
            bot_state.next_run_time = next_run.replace(tzinfo=None)
            bot_state.save_state()
            logger.info("Next scheduled run: %s", next_run.strftime("%Y-%m-%d %H:%M:%S %Z"))

        job_duration = time.time() - job_start
        logger.info("Scheduled job completed in %.2fs", job_duration)

    scheduler.add_job(scheduled_job, trigger=trigger, id="x_bot_job")
    scheduler.start()

    next_run = trigger.get_next_fire_time(None, datetime.now(tz))
    if next_run:
        bot_state.next_run_time = next_run.replace(tzinfo=None)
        bot_state.save_state()
        logger.info("Scheduler started - next run: %s (CRON: '%s' in %s)",
                    next_run.strftime("%Y-%m-%d %H:%M:%S %Z"), SCHEDULE_CRON, SCHEDULE_TZ)
    else:
        logger.warning("Could not calculate next run time for CRON: %s", SCHEDULE_CRON)
