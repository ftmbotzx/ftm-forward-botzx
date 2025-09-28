import logging
from pyrogram import Client, filters
from config import Config

# Setup logging
logger = logging.getLogger(__name__)

# NOTE: All chat functionality has been removed to prevent errors
# Chat system is no longer available - users should contact admin directly at @ftmdeveloperzbot

# Placeholder to maintain file structure
@Client.on_message(filters.private & filters.command(['activechats']))
async def list_active_chats(client, message):
    user_id = message.from_user.id

    # Check if user is admin/owner
    if not Config.is_sudo_user(user_id):
        return await message.reply_text("❌ You don't have permission to use this command!", quote=True)

    await message.reply_text(
        "<b>📋 Chat System Unavailable</b>\n\n"
        "<b>The chat system has been disabled.</b>\n"
        "<b>For support, contact:</b> @ftmdeveloperzbot",
        quote=True
    )
