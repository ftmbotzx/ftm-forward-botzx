import os
import asyncio
import threading
from flask import Flask
from bot import Bot
from ptb_commands import setup_ptb_application

# Create Flask app for Render/uptime monitoring
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "✅ Fᴛᴍ Dᴇᴠᴇʟᴏᴘᴇʀᴢ bot is live with hybrid PTB support."

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=port)

# Run Flask in background
threading.Thread(target=run_flask).start()

async def run_pyrogram_bot():
    """Run the Pyrogram bot"""
    print("Starting Pyrogram bot...")
    
    # Add retry mechanism for database locks
    max_retries = 3
    for attempt in range(max_retries):
        try:
            app = Bot()
            await app.start()
            print("Pyrogram bot started successfully!")
            await asyncio.Event().wait()  # Keep running forever
            break
        except Exception as e:
            if "database is locked" in str(e).lower() and attempt < max_retries - 1:
                print(f"Database locked, retrying in {(attempt + 1) * 2} seconds...")
                await asyncio.sleep((attempt + 1) * 2)
                continue
            else:
                print(f"Failed to start Pyrogram bot: {e}")
                raise

async def run_ptb_bot():
    """Run the python-telegram-bot for specific commands"""
    print("Starting Python-Telegram-Bot for specific commands...")
    try:
        application = setup_ptb_application()
        await application.initialize()
        await application.start()
        
        # Configure updater to only handle callback queries and specific commands
        # This prevents conflicts with Pyrogram's message handling
        await application.updater.start_polling(
            allowed_updates=["message", "callback_query"], 
            drop_pending_updates=True
        )
        
        print("PTB bot started successfully!")
        
        # Keep running
        try:
            await asyncio.Event().wait()
        finally:
            print("Stopping PTB bot...")
            try:
                await application.updater.stop()
            except:
                pass
            try:
                await application.stop()
            except:
                pass
            try:
                await application.shutdown()
            except:
                pass
            
    except Exception as e:
        print(f"Error in PTB bot: {e}")
        # Don't raise the error, let it fall back to Pyrogram only
        return False

async def main():
    """Run both Pyrogram and PTB bots concurrently"""
    try:
        print("Starting both Pyrogram and PTB bots...")
        
        # Start Pyrogram first (more critical)
        pyrogram_task = asyncio.create_task(run_pyrogram_bot())
        
        # Give Pyrogram a moment to initialize
        await asyncio.sleep(2)
        
        # Try to start PTB
        try:
            ptb_task = asyncio.create_task(run_ptb_bot())
            # Run both concurrently
            await asyncio.gather(pyrogram_task, ptb_task)
        except Exception as ptb_error:
            print(f"PTB failed to start: {ptb_error}")
            print("Continuing with Pyrogram only...")
            # Just wait for Pyrogram
            await pyrogram_task
        
    except Exception as e:
        print(f"Error running bots: {e}")
        # If there's an error, try running only Pyrogram
        print("Falling back to Pyrogram only...")
        await run_pyrogram_bot()

# Safe async run
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        print(f"[!] RuntimeError: {e}")
        print("Trying alternative startup method...")
        
        # Get or create event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Create tasks for both bots
        try:
            pyrogram_task = loop.create_task(run_pyrogram_bot())
            ptb_task = loop.create_task(run_ptb_bot())
            
            print("Starting both bots with alternative method...")
            loop.run_forever()
            
        except Exception as fallback_error:
            print(f"Fallback failed: {fallback_error}")
            print("Starting only Pyrogram bot...")
            loop.create_task(run_pyrogram_bot())
            loop.run_forever()
    except KeyboardInterrupt:
        print("Bot stopped by user")
    except Exception as e:
        print(f"Unexpected error: {e}")
