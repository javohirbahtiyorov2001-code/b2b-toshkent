"""
AI Qualifier Bot — Telegram bot that qualifies B2B leads via conversation.
Uses Claude API to ask budget/timeline questions and book Calendly calls.
Pipeline: Lead from CRM → Telegram message → Claude qualifies → books call
"""

import os
import json
import asyncio
from anthropic import Anthropic
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
CALENDLY_LINK = os.environ.get("CALENDLY_LINK", "https://calendly.com/your-link/30min")
INTERNAL_CHAT_ID = os.environ.get("INTERNAL_CHAT_ID")  # Your Telegram ID for lead notifications

anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)

QUALIFIER_SYSTEM = """You are a friendly B2B sales assistant for a web development agency in Uzbekistan.
Your job is to qualify potential clients via Telegram chat. Be warm, professional, speak Uzbek or Russian
depending on what the user writes.

Your qualification goals (ask naturally, not like a form):
1. What kind of website/app do they need? (landing, e-commerce, CRM, mobile app)
2. What is their business type and niche?
3. What is their approximate budget? Guide: landing 1-3M UZS, web app 5-15M UZS, CRM 5-20M UZS
4. When do they need it? (urgency)
5. Do they have existing brand materials (logo, colors)?

Once you have enough info (at least 3 of the 5 points), summarize what they need and offer to book
a free 30-minute discovery call via Calendly.

Keep responses SHORT (2-3 sentences max). Be conversational, not robotic.
When ready to book, say exactly: [BOOK_CALL] at the start of your message, then your text."""

# In-memory conversation storage (replace with DB in production)
conversations: dict[int, list] = {}
lead_data: dict[int, dict] = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    conversations[chat_id] = []
    lead_data[chat_id] = {"name": user.full_name, "username": user.username, "chat_id": chat_id}

    keyboard = [
        [InlineKeyboardButton("Veb-sayt", callback_data="need_website"),
         InlineKeyboardButton("Mobil ilova", callback_data="need_app")],
        [InlineKeyboardButton("CRM tizim", callback_data="need_crm"),
         InlineKeyboardButton("Boshqa", callback_data="need_other")],
    ]
    await update.message.reply_text(
        f"Assalomu alaykum {user.first_name}! 👋\n\n"
        "Men sizning loyihangiz uchun eng yaxshi yechimni topishga yordam beraman.\n"
        "Sizga nima kerak?",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id

    need_map = {
        "need_website": "Veb-sayt kerak",
        "need_app": "Mobil ilova kerak",
        "need_crm": "CRM tizim kerak",
        "need_other": "Boshqa narsa kerak",
    }
    user_text = need_map.get(query.data, query.data)
    lead_data[chat_id]["initial_need"] = user_text

    await handle_message_text(chat_id, user_text, query.message, context)


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text

    if chat_id not in conversations:
        conversations[chat_id] = []
        lead_data[chat_id] = {
            "name": update.effective_user.full_name,
            "username": update.effective_user.username,
            "chat_id": chat_id,
        }

    await handle_message_text(chat_id, text, update.message, context)


async def handle_message_text(chat_id: int, text: str, message, context: ContextTypes.DEFAULT_TYPE):
    conversations[chat_id].append({"role": "user", "content": text})

    # Get AI response
    response = anthropic.messages.create(
        model="claude-opus-4-8",
        max_tokens=400,
        thinking={"type": "adaptive"},
        system=QUALIFIER_SYSTEM,
        messages=conversations[chat_id],
    )

    reply = response.content[-1].text
    book_call = reply.startswith("[BOOK_CALL]")
    clean_reply = reply.replace("[BOOK_CALL]", "").strip()

    conversations[chat_id].append({"role": "assistant", "content": clean_reply})

    if book_call:
        keyboard = [[InlineKeyboardButton(
            "📅 Bepul konsultatsiya band qilish",
            url=CALENDLY_LINK
        )]]
        await message.reply_text(
            clean_reply,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML",
        )
        # Notify internal team
        await notify_team(context, chat_id, lead_data.get(chat_id, {}))
    else:
        await message.reply_text(clean_reply, parse_mode="HTML")


async def notify_team(context: ContextTypes.DEFAULT_TYPE, chat_id: int, lead: dict):
    """Send lead summary to internal team Telegram chat."""
    if not INTERNAL_CHAT_ID:
        return
    convo = conversations.get(chat_id, [])
    convo_text = "\n".join(
        f"{'👤' if m['role']=='user' else '🤖'} {m['content']}"
        for m in convo[-10:]
    )
    msg = (
        f"🔥 <b>Yangi leed!</b>\n\n"
        f"👤 <b>Ism:</b> {lead.get('name')}\n"
        f"📱 <b>Username:</b> @{lead.get('username', 'N/A')}\n"
        f"🎯 <b>Ehtiyoj:</b> {lead.get('initial_need', 'N/A')}\n\n"
        f"<b>Suhbat:</b>\n{convo_text}"
    )
    await context.bot.send_message(
        chat_id=INTERNAL_CHAT_ID,
        text=msg,
        parse_mode="HTML",
    )


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    print("Qualifier bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()
