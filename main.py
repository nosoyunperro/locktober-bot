import os
import logging
from typing import Final

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# ============================================================
# CONFIGURATION
# ============================================================

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Put your welcome image URL here, or use a Telegram file_id.
WELCOME_PHOTO = "https://example.com/welcome.jpg"

# Rules
RULES_URL = "https://example.com/rules"

# Tariff links
TARIFF_1_URL = "https://example.com/tariff-1"
TARIFF_2_URL = "https://example.com/tariff-2"
TARIFF_3_URL = "https://example.com/tariff-3"


# OF URLs
DISCOUNT_URLS = [
    "https://example.com/link-1",
    "https://example.com/link-2",
    "https://example.com/link-3",
    "https://example.com/link-4",
    "https://example.com/link-5",
    "https://example.com/link-6",
]

# Where applications should be sent.
# Put your Telegram numeric chat ID here.
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "")

# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


# ============================================================
# CONVERSATION STATES
# ============================================================

(
    WELCOME,
    NAME_AGE,
    SOCIAL_HANDLE,
    LOCATION,
    DEVICE,
    GOODBYE,
    EXPERIENCE,
    PLACEHOLDER,
    RULES,
    TARIFFS,
    SIX_LINKS,
    PAYMENT_SCREENSHOT,
    CONGRATULATIONS,
    REGULAR_PAYMENT,
) = range(14)


# ============================================================
# /start
# ============================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show the welcome screen."""

    context.user_data.clear()

    keyboard = [
        [
            InlineKeyboardButton(
                "I'm ready",
                callback_data="ready",
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_photo(
        photo=WELCOME_PHOTO,
        caption=(
            "👋 Welcome!\n\n"
            "We're excited to have you take part in the challenge.\n\n"
            "When you're ready to begin, click the button below."
        ),
        reply_markup=reply_markup,
    )

    return WELCOME


# ============================================================
# STATE 1 -> STATE 2
# ============================================================

async def ready(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """User clicked I'm ready."""

    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "Great! Let's get started.\n\n"
        "Please enter your name and age.\n\n"
        "For example: John, 25"
    )

    return NAME_AGE


# ============================================================
# STATE 2: NAME + AGE
# ============================================================

async def receive_name_age(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:

    context.user_data["name_age"] = update.message.text.strip()

    await update.message.reply_text(
        "Thank you!\n\n"
        "Now please enter your handle on your social media platform.\n\n"
        "For example: @username"
    )

    return SOCIAL_HANDLE


# ============================================================
# STATE 3: SOCIAL HANDLE
# ============================================================

async def receive_social_handle(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:

    context.user_data["social_handle"] = update.message.text.strip()

    await update.message.reply_text(
        "Got it.\n\n"
        "Please enter your location."
    )

    return LOCATION


# ============================================================
# STATE 4: LOCATION
# ============================================================

async def receive_location(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:

    context.user_data["location"] = update.message.text.strip()

    keyboard = [
        [
            InlineKeyboardButton(
                "Yes, I have one.",
                callback_data="device_yes",
            )
        ],
        [
            InlineKeyboardButton(
                "Not yet, but I will get one.",
                callback_data="device_later",
            )
        ],
        [
            InlineKeyboardButton(
                "No, and I don't plan to get one.",
                callback_data="device_no",
            )
        ],
    ]

    await update.message.reply_text(
        "Do you have a device that you can use for the challenge?",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    return DEVICE


# ============================================================
# STATE 5: DEVICE
# ============================================================

async def device_choice(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:

    query = update.callback_query
    await query.answer()

    choice = query.data

    if choice == "device_no":
        return await goodbye_no_device(update, context)

    if choice == "device_yes":
        context.user_data["device"] = "Yes, I have one."

    elif choice == "device_later":
        context.user_data["device"] = "Not yet, but I will get one."

    # The user goes directly to state 7.
    await query.message.reply_text(
        "Perfect!\n\n"
        "Please tell us about your level of experience."
    )

    return EXPERIENCE


# ============================================================
# STATE 6: GOODBYE
# ============================================================

async def goodbye_no_device(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:

    query = update.callback_query

    await query.message.reply_text(
        "Thank you for your interest in the challenge.\n\n"
        "Unfortunately, you need access to a device to participate.\n\n"
        "We hope to see you another time!"
    )

    return ConversationHandler.END


# ============================================================
# STATE 7: EXPERIENCE
# ============================================================

async def receive_experience(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:

    context.user_data["experience"] = update.message.text.strip()

    await update.message.reply_text(
        "Thank you!\n\n"
        "PLACEHOLDER: This question will be added later.\n\n"
        "For now, please type your answer or any text to continue."
    )

    return PLACEHOLDER


# ============================================================
# STATE 8: PLACEHOLDER
# ============================================================

async def receive_placeholder(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:

    context.user_data["placeholder"] = update.message.text.strip()

    keyboard = [
        [
            InlineKeyboardButton(
                "📖 Read the rules",
                url=RULES_URL,
            )
        ],
        [
            InlineKeyboardButton(
                "I agree.",
                callback_data="agree_rules",
            ),
        ],
        [
            InlineKeyboardButton(
                "I disagree.",
                callback_data="disagree_rules",
            ),
        ],
    ]

    await update.message.reply_text(
        "Please confirm you have read the rules and agree.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    return RULES


# ============================================================
# STATE 9: RULES
# ============================================================

async def rules_choice(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:

    query = update.callback_query
    await query.answer()

    if query.data == "disagree_rules":

        await query.message.reply_text(
            "You must agree to the rules to participate.\n\n"
            "Come back if you change your mind."
        )

        return ConversationHandler.END

    # User agreed.
    context.user_data["rules_agreed"] = True

    await show_tariffs(query.message)

    # Start the 2-minute discount timer.
    if context.job_queue:
        context.job_queue.run_once(
            send_discount_offer,
            when=120,
            chat_id=update.effective_chat.id,
            name=f"discount_{update.effective_user.id}",
        )

    return TARIFFS


# ============================================================
# STATE 10: TARIFFS
# ============================================================

async def show_tariffs(message) -> None:

    keyboard = [
        [
            InlineKeyboardButton(
                "Level 1",
                url=TARIFF_1_URL,
            )
        ],
        [
            InlineKeyboardButton(
                "Level 2",
                url=TARIFF_2_URL,
            )
        ],
        [
            InlineKeyboardButton(
                "Level 3",
                url=TARIFF_3_URL,
            )
        ],
    ]

    await message.reply_text(
        "💳 Please choose your tariff:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def send_discount_offer(
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Called two minutes after entering the tariff page."""

    job = context.job

    if not job:
        return

    chat_id = job.chat_id

    keyboard = [
        [
            InlineKeyboardButton(
                "🔥 Unlock a bigger discount",
                url=DISCOUNT_URL,
            )
        ]
    ]

    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            "You have doubts?\n\n"
            "Would you like to unlock a bigger discount?"
        ),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ============================================================
# STATE 11: SIX BUTTONS
# ============================================================

async def show_six_links(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:

    # This function can be called from wherever you decide
    # the user should enter state 11.

    keyboard = [
        [
            InlineKeyboardButton(
                "Button 1",
                url=STATE_11_URLS[0],
            )
        ],
        [
            InlineKeyboardButton(
                "Button 2",
                url=STATE_11_URLS[1],
            )
        ],
        [
            InlineKeyboardButton(
                "Button 3",
                url=STATE_11_URLS[2],
            )
        ],
        [
            InlineKeyboardButton(
                "Button 4",
                url=STATE_11_URLS[3],
            )
        ],
        [
            InlineKeyboardButton(
                "Button 5",
                url=STATE_11_URLS[4],
            )
        ],
        [
            InlineKeyboardButton(
                "Button 6",
                url=STATE_11_URLS[5],
            )
        ],
    ]

    await update.effective_message.reply_text(
        "Please choose one of the following options:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    return SIX_LINKS


# ============================================================
# STATE 12: PAYMENT SCREENSHOT
# ============================================================

async def request_payment_screenshot(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:

    await update.effective_message.reply_text(
        "💳 Please complete your payment and send a screenshot "
        "of the payment confirmation here."
    )

    return PAYMENT_SCREENSHOT


async def receive_payment_screenshot(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:

    # Telegram photos arrive as a list of PhotoSize objects.
    if update.message.photo:

        photo = update.message.photo[-1]

        context.user_data["payment_screenshot_file_id"] = photo.file_id

        # Forward the screenshot to the administrator.
        if ADMIN_CHAT_ID:
            await context.bot.forward_message(
                chat_id=ADMIN_CHAT_ID,
                from_chat_id=update.effective_chat.id,
                message_id=update.message.message_id,
            )

            # Send the collected application information to admin.
            await send_application_to_admin(update, context)

        await update.message.reply_text(
            "Thank you! Your payment confirmation has been received."
        )

        await show_congratulations(update, context)

        return CONGRATULATIONS

    await update.message.reply_text(
        "Please send the payment confirmation as a screenshot/photo."
    )

    return PAYMENT_SCREENSHOT


# ============================================================
# APPLICATION DATA -> ADMIN
# ============================================================

async def send_application_to_admin(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    if not ADMIN_CHAT_ID:
        logger.warning("ADMIN_CHAT_ID is not configured.")
        return

    data = context.user_data

    user = update.effective_user

    username = f"@{user.username}" if user.username else "No Telegram username"

    message = (
        "📥 NEW CHALLENGE APPLICATION\n\n"
        f"Telegram ID: {user.id}\n"
        f"Telegram username: {username}\n\n"
        f"Name + age: {data.get('name_age', '-')}\n"
        f"Social handle: {data.get('social_handle', '-')}\n"
        f"Location: {data.get('location', '-')}\n"
        f"Device: {data.get('device', '-')}\n"
        f"Experience: {data.get('experience', '-')}\n"
        f"Placeholder: {data.get('placeholder', '-')}\n"
        f"Rules agreed: {data.get('rules_agreed', False)}"
    )

    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=message,
    )


# ============================================================
# STATE 13: CONGRATULATIONS
# ============================================================

async def show_congratulations(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:

    keyboard = [
        [
            InlineKeyboardButton(
                "Regular payment method",
                callback_data="regular_payment",
            )
        ]
    ]

    await update.effective_message.reply_text(
        "🎉 Congratulations!\n\n"
        "Your application has been received successfully.\n\n"
        "Thank you for applying to the challenge.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    return CONGRATULATIONS


# ============================================================
# STATE 13 -> STATE 14
# ============================================================

async def regular_payment(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:

    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "💳 Regular payment method\n\n"
        "PLACEHOLDER: Add your regular payment instructions "
        "or payment link here."
    )

    return REGULAR_PAYMENT


# ============================================================
# /cancel
# ============================================================

async def cancel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:

    await update.effective_message.reply_text(
        "The application has been cancelled.\n\n"
        "You can use /start whenever you're ready to begin again."
    )

    return ConversationHandler.END


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        raise RuntimeError(
            "Please set BOT_TOKEN before starting the bot."
        )

    application: Application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .build()
    )

    conversation = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
        ],

        states={

            WELCOME: [
                CallbackQueryHandler(
                    ready,
                    pattern="^ready$",
                )
            ],

            NAME_AGE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    receive_name_age,
                )
            ],

            SOCIAL_HANDLE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    receive_social_handle,
                )
            ],

            LOCATION: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    receive_location,
                )
            ],

            DEVICE: [
                CallbackQueryHandler(
                    device_choice,
                    pattern="^device_(yes|later|no)$",
                )
            ],

            EXPERIENCE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    receive_experience,
                )
            ],

            PLACEHOLDER: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    receive_placeholder,
                )
            ],

            RULES: [
                CallbackQueryHandler(
                    rules_choice,
                    pattern="^(agree_rules|disagree_rules)$",
                )
            ],

            TARIFFS: [
                # The tariff buttons are URL buttons, so Telegram
                # opens the links directly and doesn't send a callback.
                #
                # Add whatever event should advance the user to
                # state 11 here.
                CommandHandler(
                    "continue",
                    show_six_links,
                )
            ],

            SIX_LINKS: [
                CommandHandler(
                    "payment",
                    request_payment_screenshot,
                )
            ],

            PAYMENT_SCREENSHOT: [
                MessageHandler(
                    filters.PHOTO,
                    receive_payment_screenshot,
                )
            ],

            CONGRATULATIONS: [
                CallbackQueryHandler(
                    regular_payment,
                    pattern="^regular_payment$",
                )
            ],

            REGULAR_PAYMENT: [],

        },

        fallbacks=[
            CommandHandler("cancel", cancel),
        ],

        allow_reentry=True,
    )

    application.add_handler(conversation)

    logger.info("Bot is running...")

    application.run_polling()


if __name__ == "__main__":
    main()
