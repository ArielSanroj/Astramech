"""X Content Bot Client - Main Entry Point."""
import asyncio
import logging

from client_config import (
    QUERIES, AUTO, MAX_CONCURRENT_POSTS, RETRY_CONFIG,
    ENABLE_SCHEDULER, RUN_ON_STARTUP
)
from bot_state import bot_state
from bot_runner import run_once, schedule_client

logger = logging.getLogger("x-mcp-client")


async def main():
    """Main entry point with enhanced logging and state management."""
    logger.info("X Content Bot starting up...")
    logger.info("Configuration: queries=%s, auto=%s, max_concurrent=%d, retry_config=%s",
                QUERIES, AUTO, MAX_CONCURRENT_POSTS, RETRY_CONFIG)

    if bot_state.last_run_time:
        logger.info("Previous run: %s (%d posts processed, %d posted)",
                    bot_state.last_run_time.strftime("%Y-%m-%d %H:%M:%S"),
                    bot_state.total_posts_processed, bot_state.total_posts_posted)

    if ENABLE_SCHEDULER:
        logger.info("Scheduler mode enabled")
        schedule_client()

        if RUN_ON_STARTUP:
            logger.info("Running on startup...")
            await run_once()

        logger.info("Scheduler running - bot will continue in background")
        try:
            while True:
                await asyncio.sleep(3600)
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            bot_state.save_state()
    else:
        logger.info("One-time run mode")
        await run_once()
        bot_state.save_state()
        logger.info("One-time run completed")


if __name__ == "__main__":
    asyncio.run(main())
