import os
import datetime
import random
from django.core.management.base import BaseCommand
from asgiref.sync import sync_to_async

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from bot_app.models import Quote, FavoriteQuote

TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', 'TELEGRAM_BOT_TOKEN')

FORISMATIC_URL = (
    "https://api.forismatic.com/api/1.0/"
    "?method=getQuote&format=json&lang=ru"
)

MAIN_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        ["🚀 Start Dialogue"],
        ["📜 Get a Quote", "⭐ My Favorites"],
        ["⚙️ Project Info"],
    ],
    resize_keyboard=True,
    one_time_keyboard=False,
    input_field_placeholder="Choose an action from the menu...",
)
EASTER_EGGS = {
    "hello": (
        "👋 Hello, dear user! Glad to see you.\n"
        "Use the menu below to get a dose of wisdom."
    ),
    "hi": (
        "👋 Hi there! Hope you are having a great day.\n"
        "Type <code>help</code> or use the buttons below to interact with me."
    ),
    "help": (
        "🆘 Need help? Here is a quick cheat sheet:\n\n"
        "📜 <b>Get a Quote</b> — fetches a random quote from the API.\n"
        "⭐ <b>My Favorites</b> — shows your last 5 saved quotes.\n"
        "⚙️ <b>Project Info</b> — technical details about this bot.\n\n"
        "For everything else, just press the buttons!"
    ),
    "author": (
        "🧑‍💻 This bot was created as part of a final project for the "
        "'Python Programming' course.\n\n"
        "Stack: <b>python-telegram-bot 20+</b>, <b>Django ORM</b>, "
        "<b>SQLite</b>, <b>Forismatic API</b>."
    ),
    "joke": (
        "😄 A programmer walks into a bar and orders 1 beer.\n"
        "Then he orders 0 beers. Then he orders -1 beers.\n"
        "The bartender says: 'Alright, look, just log out and log in again.'\n\n"
        "<i>— A classic joke 😄</i>"
    ),
    "database": (
        "🗄 All your favorite quotes are saved in an <b>SQLite</b> database "
        "using <b>Django ORM</b>.\n"
        "Click '⭐ My Favorites' to see your last 5 entries."
    ),
    "django": (
        "🌐 <b>Django</b> is a powerful web framework for Python.\n\n"
        "In this project, it acts as the backend: it manages data models, "
        "migrations, and the SQLite database. The bot communicates with the DB directly via Django ORM."
    ),
    "python": (
        "🐍 <b>Python</b> is the programming language this bot is built on.\n\n"
        "Version: 3.10+. Libraries used: "
        "<code>python-telegram-bot</code>, <code>django</code>, "
        "<code>requests</code>. Simple and powerful!"
    ),
    "luck": (
        "🍀 Luck is on your side today! Here is a special bonus:\n\n"
        "<i>«Luck is what happens when preparation meets opportunity.»</i>\n"
        "— Seneca\n\n"
        "Click '📜 Get a Quote' to get another one!"
    ),
    "time": (
        "🕐 Current server time: <b>{time}</b>\n\n"
        "It's a perfect time to read an inspiring quote, isn't it? 😊"
    ),
    "weather": (
        "🌤 Unfortunately, I cannot check the weather — I am a quote bot!\n\n"
        "However, I can charge you with motivation: click '📜 Get a Quote'."
    ),
}


def _build_quote_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("❤️ Save to Django", callback_data="save_quote")]]
    )


def get_categories_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("💪 Motivation", callback_data="category_motivation"),
            InlineKeyboardButton("🎯 Success", callback_data="category_success")
        ],
        [
            InlineKeyboardButton("🧠 Wisdom", callback_data="category_wisdom")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    welcome = (
        f"👋 Hello, <b>{user.first_name}</b>!\n\n"
        "I am a <b>Hybrid Quote Bot</b>.\n"
        "Get wise thoughts from great people and save your favorites directly into the database.\n\n"
        "Use the menu below ⬇️"
    )
    await update.message.reply_html(welcome, reply_markup=MAIN_KEYBOARD)


async def get_quote_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        text="Please choose a category for your quote:",
        reply_markup=get_categories_keyboard()
    )

@sync_to_async
def get_user_favorites(user_id):
    return list(FavoriteQuote.objects.filter(user_id=user_id).order_by("-id")[:5])


@sync_to_async
def save_user_quote(user_id, text, author):
    return FavoriteQuote.objects.create(user_id=user_id, text=text, author=author)


@sync_to_async
def get_quote_by_category(category_name: str):
    quotes = Quote.objects.filter(category__iexact=category_name)
    if quotes.exists():
        return random.choice(quotes)
    return None


async def handle_favorites(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    try:
        quotes = await get_user_favorites(user_id)
    except Exception as exc:
        print(f"[ERROR] Error reading from DB: {exc}")
        await update.message.reply_text("Failed to load favorites. Please try again later.")
        return

    if not quotes:
        await update.message.reply_html(
            "⭐ You don't have any saved quotes yet.\n\n"
            "Click '📜 Get a Quote' and save the one you like!"
        )
        return

    lines = ["⭐ <b>Your last saved quotes:</b>\n"]
    for idx, q in enumerate(quotes, start=1):
        author_label = q.author if q.author else "Unknown Author"
        lines.append(f"{idx}. <i>«{q.text}»</i>\n   — <b>{author_label}</b>\n")

    await update.message.reply_html("\n".join(lines))


async def handle_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    info = (
        "⚙️ <b>Project Info</b>\n\n"
        "📌 <b>Name:</b> Hybrid Telegram Bot for Finding and Storing Quotes\n"
        "🐍 <b>Language:</b> Python 3.10+\n"
        "📚 <b>Libraries:</b> python-telegram-bot 20+, Django, requests\n"
        "🗄 <b>Database:</b> SQLite via Django ORM\n"
        "🌐 <b>Quote API:</b> Forismatic (forismatic.com)\n"
        "🎓 <b>Course:</b> Python Programming\n\n"
        "<i>Save your favorite quotes and stay inspired every day!</i>"
    )
    await update.message.reply_html(info)


async def handle_start_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_html(
        "🚀 <b>Dialogue started!</b>\n\n"
        "I am ready to help you. What are you interested in?\n"
        "Use the menu buttons or type one of the keywords:\n"
        "<code>hello</code>, <code>help</code>, <code>python</code>, "
        "<code>django</code>, <code>luck</code>, etc. 🙂"
    )


async def handle_save_quote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    raw_text = query.message.text

    if not raw_text:
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text("Unable to determine the quote to save.")
        return

    try:
        clean_text = raw_text.replace('✨', '').replace('«', '').replace('»', '').strip()
        
        if "—" in clean_text:
            parts = clean_text.split("—", 1)
        elif "–" in clean_text:
            parts = clean_text.split("–", 1)
        elif "-" in clean_text:
            parts = clean_text.split("-", 1)
        else:
            parts = [clean_text, "Unknown Author"]

        quote_text = parts[0].strip()
        author = parts[1].strip() if len(parts) > 1 else "Unknown Author"

        await save_user_quote(user_id, quote_text, author)
        
        await query.edit_message_text(
            text=(
                f"✅ <b>Successfully saved to the Django database!</b>\n\n"
                f"✨ <i>«{quote_text}»</i>\n— <b>{author}</b>"
            ),
            parse_mode="HTML",
            reply_markup=None,
        )
    except Exception as exc:
        print(f"[ERROR] Error writing to database: {exc}")
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text("There was an error saving to the database. Please try again later.")


async def category_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer() 
    selected_category = query.data.replace("category_", "")
    
    quote = await get_quote_by_category(selected_category)
    
    if quote:
        message = f"📜 «{quote.text}» — {quote.author}"
        await query.edit_message_text(text=message, reply_markup=_build_quote_inline())
    else:
        message = f"No quotes found in *{selected_category.capitalize()}* category yet. But keep moving forward!"
        await query.edit_message_text(text=message, parse_mode="Markdown")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (update.message.text or "").strip().lower()

    if text == "📜 get a quote":
        await get_quote_handler(update, context)
        return

    if text == "⭐ my favorites":
        await handle_favorites(update, context)
        return

    if text == "⚙️ project info":
        await handle_info(update, context)
        return

    if text == "🚀 start dialogue":
        await handle_start_dialog(update, context)
        return

    if text in EASTER_EGGS:
        template = EASTER_EGGS[text]
        if "{time}" in template:
            now = datetime.datetime.now().strftime("%H:%M:%S")
            reply = template.format(time=now)
        else:
            reply = template
        await update.message.reply_html(reply)
        return

    await update.message.reply_html(
        "🤔 I don't understand this command.\n\n"
        "Please use the menu buttons below ⬇️ "
        "or write one of the keywords: "
        "<code>hello</code>, <code>help</code>, <code>python</code>.",
        reply_markup=MAIN_KEYBOARD,
    )


class Command(BaseCommand):
    help = "Launches a Telegram bot (integrated with Django)"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("🤖 Initializing Django command for Telegram bot..."))

        app = ApplicationBuilder().token(TOKEN).build()

        app.add_handler(CommandHandler("start", cmd_start))
        app.add_handler(CallbackQueryHandler(handle_save_quote, pattern="^save_quote$"))
        app.add_handler(CallbackQueryHandler(category_callback_handler, pattern="^category_"))
        
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

        self.stdout.write(self.style.SUCCESS("✅ The bot has been successfully launched and is listening to the server. Press Ctrl+C to stop."))
        app.run_polling(drop_pending_updates=True)