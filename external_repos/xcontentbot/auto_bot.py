#!/usr/bin/env python3
"""
Auto-posting X bot - finds posts and automatically posts replies.
"""

import asyncio
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the client functions
from x_client import run_once

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("auto-bot")

async def main():
    print("🤖 Starting Auto-Posting X Bot...")
    print("📝 Configuration:")
    print(f"   - AUTO_POST: {os.getenv('AUTO_POST', 'false')}")
    print(f"   - AUTO: {os.getenv('AUTO', 'false')}")
    print(f"   - Queries: {os.getenv('QUERIES', 'burnout')}")
    print(f"   - Max posts per query: {os.getenv('MAX_POSTS_TO_PROCESS', '3')}")
    print()
    
    if os.getenv('AUTO_POST', 'false').lower() != 'true':
        print("⚠️  WARNING: AUTO_POST is not set to 'true' in .env")
        print("   The bot will only preview replies, not post them.")
        print()
    
    if os.getenv('AUTO', 'false').lower() != 'true':
        print("⚠️  WARNING: AUTO is not set to 'true' in .env")
        print("   The bot will only preview replies, not post them.")
        print()
    
    print("🚀 Starting bot run...")
    try:
        summaries = await run_once()
        
        print("\n📊 RESULTS SUMMARY:")
        total_posted = 0
        total_preview = 0
        total_errors = 0
        
        for summary in summaries:
            query = summary.get('query', 'unknown')
            posted = summary.get('posted', 0)
            preview = summary.get('preview', 0)
            errors = summary.get('errors', 0)
            
            total_posted += posted
            total_preview += preview
            total_errors += errors
            
            print(f"   {query}: {posted} posted, {preview} previewed, {errors} errors")
        
        print(f"\n🎯 TOTALS:")
        print(f"   ✅ Posted: {total_posted}")
        print(f"   👀 Previewed: {total_preview}")
        print(f"   ❌ Errors: {total_errors}")
        
        if total_posted > 0:
            print(f"\n🎉 Successfully posted {total_posted} replies!")
        elif total_preview > 0:
            print(f"\n👀 Previewed {total_preview} replies (not posted)")
        else:
            print(f"\n😞 No replies were generated")
            
    except Exception as e:
        logger.error("Bot run failed: %s", e)
        print(f"\n❌ Bot run failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())