import logging
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database import db
from config import Config
from plugins.timezone import get_current_ist_timestamp, display_subscription_date

# Setup logging
logger = logging.getLogger(__name__)

# NOTE: All chat functionality has been moved to PTB (ptb_commands.py) to prevent conflicts
# This file is kept for compatibility but all handlers are removed

# List active chats for admins - kept in Pyrogram for admin use
@Client.on_message(filters.private & filters.command(['activechats']))
async def list_active_chats(client, message):
    user_id = message.from_user.id

    # Check if user is admin/owner
    if not Config.is_sudo_user(user_id):
        return await message.reply_text("❌ You don't have permission to use this command!", quote=True)

    try:
        active_chats = await db.get_all_active_chats()

        if not active_chats:
            return await message.reply_text(
                "<b>📋 No Active Chat Sessions</b>\n\n"
                "<b>No active chat sessions found.</b>",
                quote=True
            )

        chats_text = "<b>📋 Active Chat Sessions</b>\n\n"

        for i, chat in enumerate(active_chats, 1):
            admin_id = chat.get('admin_id', 'Unknown')
            target_user_id = chat.get('target_user_id', 'Unknown')
            created_at = chat.get('created_at', 'Unknown')

            if isinstance(created_at, datetime):
                created_str = created_at.strftime('%Y-%m-%d %H:%M')
            else:
                created_str = str(created_at)

            chats_text += f"<b>{i}. Session ID:</b> <code>{chat['_id']}</code>\n"
            chats_text += f"   <b>Admin:</b> <code>{admin_id}</code>\n"
            chats_text += f"   <b>User:</b> <code>{target_user_id}</code>\n"
            chats_text += f"   <b>Started:</b> {created_str}\n\n"

        await message.reply_text(chats_text, quote=True)

    except Exception as e:
        logger.error(f"Error listing active chats: {e}", exc_info=True)
        await message.reply_text("❌ An error occurred while fetching active chats.", quote=True)