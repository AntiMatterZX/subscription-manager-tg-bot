import logging
import asyncio
import json
from datetime import datetime
from typing import Dict, Optional, Tuple
from telegram import Update, ChatMember, Bot
from telegram.ext import (
    Application,
    ChatMemberHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from telegram.constants import ChatMemberStatus
from telegram.error import TelegramError
import threading

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


class TelegramGroupBotService:
    def __init__(self, bot_token: str = None):

        self.bot_token = bot_token
        self.application = Application.builder().token(bot_token).build()
        self.bot = Bot(token=bot_token)

        # Store invite links with custom tokens
        self.invite_links: Dict[str, Dict] = {}

        # Store group information
        self.groups: Dict[int, Dict] = {}

        # Threading for running bot alongside Flask
        self.bot_thread = None
        self.running = False

        self.setup_handlers()

    def init_app(self, app):
        self.app = app

    def setup_handlers(self):
        """Setup all event handlers"""
        # Chat member updates (bot added/removed, user joins/leaves)
        self.application.add_handler(
            ChatMemberHandler(
                self.handle_chat_member_update, ChatMemberHandler.CHAT_MEMBER
            )
        )

        # My chat member updates (specifically for bot being added/removed)
        self.application.add_handler(
            ChatMemberHandler(
                self.handle_my_chat_member_update, ChatMemberHandler.MY_CHAT_MEMBER
            )
        )

        # Message handler for tracking joins via invite links
        self.application.add_handler(
            MessageHandler(
                filters.StatusUpdate.NEW_CHAT_MEMBERS, self.handle_new_members
            )
        )

    async def handle_my_chat_member_update(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle bot being added or removed from groups"""
        try:
            chat = update.effective_chat
            new_member = update.my_chat_member.new_chat_member
            old_member = update.my_chat_member.old_chat_member

            # Bot added to group
            if old_member.status in [
                ChatMemberStatus.LEFT,
            ] and new_member.status in [
                ChatMemberStatus.MEMBER,
                ChatMemberStatus.ADMINISTRATOR,
            ]:

                await self.on_bot_added_to_group(chat, context)

            # Bot removed from group
            elif old_member.status in [
                ChatMemberStatus.MEMBER,
                ChatMemberStatus.ADMINISTRATOR,
            ] and new_member.status in [ChatMemberStatus.LEFT]:

                await self.on_bot_removed_from_group(chat, context)

        except Exception as e:
            logger.exception(f"Error handling my chat member update: {e}")

    async def handle_chat_member_update(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle regular chat member updates (users joining/leaving)"""
        try:
            chat = update.effective_chat
            user = update.chat_member.from_user
            new_member = update.chat_member.new_chat_member
            old_member = update.chat_member.old_chat_member

            # User joined the group
            if old_member.status in [
                ChatMemberStatus.LEFT,
            ] and new_member.status in [
                ChatMemberStatus.MEMBER,
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.RESTRICTED,
            ]:

                await self.on_user_joined_group(chat, user, context)

            # User left the group
            elif old_member.status in [
                ChatMemberStatus.MEMBER,
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.RESTRICTED,
            ] and new_member.status in [ChatMemberStatus.LEFT]:

                await self.on_user_left_group(chat, user, context)

        except Exception as e:
            logger.error(f"Error handling chat member update: {e}")

    async def handle_new_members(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle new members joining via invite links"""
        try:
            chat = update.effective_chat
            new_members = update.message.new_chat_members

            for member in new_members:
                # Try to identify which invite link was used
                invite_token = await self.identify_invite_token(
                    chat.id, member.id, context
                )
                if invite_token:
                    await self.on_user_joined_via_invite(
                        chat, member, invite_token, context
                    )

        except Exception as e:
            logger.error(f"Error handling new members: {e}")

    async def on_bot_added_to_group(self, chat, context: ContextTypes.DEFAULT_TYPE):
        """Called when bot is added to a group"""
        group_info = {
            "id": chat.id,
            "title": chat.title,
            "type": chat.type,
            "added_at": datetime.now().isoformat(),
            "invite_links": {},
        }

        self.groups[chat.id] = group_info

        logger.info(f"🟢 Bot added to group: {chat.title} (ID: {chat.id})")
        with self.app.app_context():
            from app.services.telegram_group_service import TelegramGroupService

            TelegramGroupService.create_or_update_group(chat.id, chat.title)

        # Send welcome message
        try:
            welcome_text = (
                f"🎉 Hello! I've been added to **{chat.title}**\n\n"
                "I can help you manage this group with the following features:\n"
                "• Track invite links with custom tokens\n"
                "• Remove users via API\n"
                "• Monitor group activities\n\n"
                "The bot is now ready to receive API commands!"
            )
            await context.bot.send_message(
                chat_id=chat.id, text=welcome_text, parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Could not send welcome message: {e}")

    async def on_bot_removed_from_group(self, chat, context: ContextTypes.DEFAULT_TYPE):
        """Called when bot is removed from a group"""
        logger.info(f"🔴 Bot removed from group: {chat.title} (ID: {chat.id})")

        # Clean up group data
        if chat.id in self.groups:
            del self.groups[chat.id]

        # Clean up invite links for this group
        links_to_remove = [
            link_id
            for link_id, link_data in self.invite_links.items()
            if link_data["chat_id"] == chat.id
        ]
        for link_id in links_to_remove:
            del self.invite_links[link_id]

        with self.app.app_context():
            from app.services.telegram_group_service import TelegramGroupService

            TelegramGroupService.mark_group_as_inactive(chat.id)

    async def on_user_joined_group(
        self, chat, user, context: ContextTypes.DEFAULT_TYPE
    ):
        """Called when a user joins the group"""
        logger.info(
            f"👤 User {user.full_name} (ID: {user.id}) joined group {chat.title}"
        )

    async def on_user_left_group(self, chat, user, context: ContextTypes.DEFAULT_TYPE):
        """Called when a user leaves the group"""
        logger.info(f"👋 User {user.full_name} (ID: {user.id}) left group {chat.title}")

    async def on_user_joined_via_invite(
        self, chat, user, invite_token: str, context: ContextTypes.DEFAULT_TYPE
    ):
        """Called when a user joins via a tracked invite link"""
        logger.info(
            f"🔗 User {user.full_name} (ID: {user.id}) joined {chat.title} via invite token: {invite_token}"
        )

        # Update invite link usage
        if invite_token in self.invite_links:
            self.invite_links[invite_token]["usage_count"] += 1
            self.invite_links[invite_token]["last_used"] = datetime.now().isoformat()
            self.invite_links[invite_token]["users"].append(
                {
                    "user_id": user.id,
                    "username": user.username,
                    "full_name": user.full_name,
                    "joined_at": datetime.now().isoformat(),
                }
            )
            from app.services.subscription_service import SubscriptionService

            with self.app.app_context():
                SubscriptionService.update_subscription_with_telegram_user(
                    invite_token, user.id, user.username
                )

    async def identify_invite_token(
        self, chat_id: int, user_id: int, context: ContextTypes.DEFAULT_TYPE
    ) -> Optional[str]:
        """Try to identify which invite link was used"""
        # Simple approach - return the most recently created active invite for this chat
        recent_invite = None
        recent_time = None

        for token, link_data in self.invite_links.items():
            if link_data["chat_id"] == chat_id and link_data["active"]:
                if recent_time is None or link_data["created_at"] > recent_time:
                    recent_time = link_data["created_at"]
                    recent_invite = token

        return recent_invite

    # API METHODS - Called from Flask

    async def create_invite_link_api(
        self, chat_id: int, token: str, created_by_user_id: int = None
    ) -> Tuple[bool, str, Optional[str]]:
        """
        API method to create an invite link with custom token
        Returns: (success: bool, message: str, invite_link: Optional[str])
        """
        try:
            # Check if chat exists in our records
            if chat_id not in self.groups:
                return False, f"Bot is not in chat {chat_id}", None

            # Check if token already exists
            if token in self.invite_links:
                return False, f"Token '{token}' already exists", None

            # Get chat info
            try:
                chat = await self.bot.get_chat(chat_id)
            except TelegramError as e:
                return False, f"Could not access chat: {str(e)}", None

            # Create invite link
            invite_link = await self.bot.create_chat_invite_link(
                chat_id=chat_id,
                name=f"API Link - {token}",
                member_limit=None,
                expire_date=None,
            )

            # Store the invite link with token
            link_data = {
                "chat_id": chat_id,
                "chat_title": chat.title,
                "token": token,
                "invite_link": invite_link.invite_link,
                "created_by": created_by_user_id,
                "created_at": datetime.now().isoformat(),
                "active": True,
                "usage_count": 0,
                "users": [],
                "last_used": None,
            }

            self.invite_links[token] = link_data

            logger.info(
                f"✅ API: Created invite link for chat {chat_id} with token {token}"
            )
            return True, "Invite link created successfully", invite_link.invite_link

        except Exception as e:
            logger.error(f"❌ API: Error creating invite link: {e}")
            return False, f"Error creating invite link: {str(e)}", None

    async def remove_user_api(self, chat_id: int, user_id: int) -> Tuple[bool, str]:
        """
        API method to remove a user from a group
        Returns: (success: bool, message: str)
        """
        try:
            # Check if chat exists in our records
            if chat_id not in self.groups:
                return False, f"Bot is not in chat {chat_id}"

            # Check if user exists in chat
            try:
                member = await self.bot.get_chat_member(chat_id, user_id)
                if member.status in [ChatMemberStatus.LEFT]:
                    return False, f"User {user_id} is not in the chat"
            except TelegramError as e:
                return False, f"Could not find user in chat: {str(e)}"

            # Remove user
            await self.bot.ban_chat_member(chat_id, user_id)
            await self.bot.unban_chat_member(
                chat_id, user_id
            )  # Unban to allow rejoining

            logger.info(f"✅ API: Removed user {user_id} from chat {chat_id}")
            return True, f"User {user_id} removed successfully"

        except Exception as e:
            logger.error(f"❌ API: Error removing user: {e}")
            return False, f"Error removing user: {str(e)}"

    async def get_invite_link_info_api(
        self, token: str
    ) -> Tuple[bool, str, Optional[Dict]]:
        """
        API method to get invite link information
        Returns: (success: bool, message: str, data: Optional[Dict])
        """
        try:
            if token not in self.invite_links:
                return False, f"Token '{token}' not found", None

            link_data = self.invite_links[token].copy()
            return True, "Invite link data retrieved", link_data

        except Exception as e:
            logger.error(f"❌ API: Error getting invite link info: {e}")
            return False, f"Error getting invite link info: {str(e)}", None

    async def list_group_invites_api(
        self, chat_id: int
    ) -> Tuple[bool, str, Optional[list]]:
        """
        API method to list all invite links for a group
        Returns: (success: bool, message: str, invites: Optional[list])
        """
        try:
            if chat_id not in self.groups:
                return False, f"Bot is not in chat {chat_id}", None

            chat_invites = [
                link
                for link in self.invite_links.values()
                if link["chat_id"] == chat_id and link["active"]
            ]

            return True, f"Found {len(chat_invites)} active invites", chat_invites

        except Exception as e:
            logger.error(f"❌ API: Error listing invites: {e}")
            return False, f"Error listing invites: {str(e)}", None

    async def deactivate_invite_link_api(self, token: str) -> Tuple[bool, str]:
        """
        API method to deactivate an invite link
        Returns: (success: bool, message: str)
        """
        try:
            if token not in self.invite_links:
                return False, f"Token '{token}' not found"

            # Revoke the invite link
            chat_id = self.invite_links[token]["chat_id"]
            invite_link = self.invite_links[token]["invite_link"]

            await self.bot.revoke_chat_invite_link(chat_id, invite_link)

            # Mark as inactive
            self.invite_links[token]["active"] = False
            self.invite_links[token]["deactivated_at"] = datetime.now().isoformat()

            logger.info(f"✅ API: Deactivated invite link with token {token}")
            return True, f"Invite link '{token}' deactivated successfully"

        except Exception as e:
            logger.error(f"❌ API: Error deactivating invite link: {e}")
            return False, f"Error deactivating invite link: {str(e)}"

    async def get_group_info_api(
        self, chat_id: int
    ) -> Tuple[bool, str, Optional[Dict]]:
        """
        API method to get group information
        Returns: (success: bool, message: str, data: Optional[Dict])
        """
        try:
            if chat_id not in self.groups:
                return False, f"Bot is not in chat {chat_id}", None

            # Get current chat info
            chat = await self.bot.get_chat(chat_id)
            member_count = await self.bot.get_chat_member_count(chat_id)

            # Get administrators
            admins = await self.bot.get_chat_administrators(chat_id)
            admin_count = len([admin for admin in admins if not admin.user.is_bot])

            group_data = {
                "id": chat.id,
                "title": chat.title,
                "type": chat.type,
                "description": chat.description,
                "member_count": member_count,
                "admin_count": admin_count,
                "active_invites": len(
                    [
                        l
                        for l in self.invite_links.values()
                        if l["chat_id"] == chat_id and l["active"]
                    ]
                ),
                "bot_added_at": self.groups[chat_id].get("added_at"),
            }

            return True, "Group information retrieved", group_data

        except Exception as e:
            logger.error(f"❌ API: Error getting group info: {e}")
            return False, f"Error getting group info: {str(e)}", None

    # SYNCHRONOUS WRAPPERS FOR FLASK API

    def create_invite_link(
        self, chat_id: int, token: str, created_by_user_id: int = None
    ) -> Tuple[bool, str, Optional[str]]:
        """Synchronous wrapper for create_invite_link_api"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self.create_invite_link_api(chat_id, token, created_by_user_id)
            )
        finally:
            loop.close()

    def remove_user(self, chat_id: int, user_id: int) -> Tuple[bool, str]:
        """Synchronous wrapper for remove_user_api"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.remove_user_api(chat_id, user_id))
        finally:
            loop.close()

    def get_invite_link_info(self, token: str) -> Tuple[bool, str, Optional[Dict]]:
        """Synchronous wrapper for get_invite_link_info_api"""
        return (
            True if token in self.invite_links else False,
            "Found" if token in self.invite_links else "Not found",
            self.invite_links.get(token),
        )

    def list_group_invites(self, chat_id: int) -> Tuple[bool, str, Optional[list]]:
        """Synchronous wrapper for list_group_invites_api"""
        if chat_id not in self.groups:
            return False, f"Bot is not in chat {chat_id}", None

        chat_invites = [
            link
            for link in self.invite_links.values()
            if link["chat_id"] == chat_id and link["active"]
        ]

        return True, f"Found {len(chat_invites)} active invites", chat_invites

    def deactivate_invite_link(self, token: str) -> Tuple[bool, str]:
        """Synchronous wrapper for deactivate_invite_link_api"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.deactivate_invite_link_api(token))
        finally:
            loop.close()

    def get_group_info(self, chat_id: int) -> Tuple[bool, str, Optional[Dict]]:
        """Synchronous wrapper for get_group_info_api"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.get_group_info_api(chat_id))
        finally:
            loop.close()

    # BOT LIFECYCLE MANAGEMENT

    def start_bot(self):
        """Start the bot in a separate thread"""

        def run_bot():
            logger.info("🚀 Starting Telegram Bot Service...")
            self.running = True
            import asyncio

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self.application.run_polling(allowed_updates=Update.ALL_TYPES)

        if not self.running:
            self.bot_thread = threading.Thread(target=run_bot, daemon=True)
            self.bot_thread.start()
            logger.info("✅ Bot service started in background thread")

    def stop_bot(self):
        """Stop the bot"""
        if self.running:
            self.running = False
            if self.application.updater:
                self.application.updater.stop()
            logger.info("🛑 Bot service stopped")


import os

tg_bot = TelegramGroupBotService(os.environ.get("TELEGRAM_BOT_TOKEN"))
