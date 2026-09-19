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
STANDARD_URLS = [
    "https://example.com/tariff-1",
    "https://example.com/tariff-2",
    "https://example.com/tariff-3"
]

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
    GOODBYE1,
    EXPERIENCE,
    KINKS,
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
            "This is a private application. Your answers will only be used to review your application and communicate with you about the challenge. I am accepting a limited number of participants, so I will ask you a few short questions first. Be honest. The goal is to find participants who are generally suited to this format."
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
        "Tell me your name and age."
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
        "Tell me your fetlife nickname.\nExample: sub_123"
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
        "What is your location / time zone?\nExample: Barcelona / UTC+2"
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
        "Do you currently have a Chastity device?",
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
# STATE 6: GOODBYE1
# ============================================================

async def goodbye_no_device(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:

    query = update.callback_query

    await query.message.reply_text(
        "A chastity device is required for this challenge. You may try to apply again when you get one. Thank you for your interest."
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
        "What is the longest you have gone without orgasm or release?\nExample: 15 days"
    )

    return KINKS


# ============================================================
# STATE 8: EXPERIENCE
# ============================================================

async def receive_kinks(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:

    context.user_data["experience"] = update.message.text.strip()

    await update.message.reply_text(
        "What is the longest you have gone without orgasm or release?\nExample: 15 days"
    )

    return RULES


# ============================================================
# STATE 8: RULES
# ============================================================

async def receive_rules(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:

    context.user_data["rules"] = update.message.text.strip()

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
                "Shadow",
                url=TARIFF_1_URL,
            )
        ],
        [
            InlineKeyboardButton(
                "Admirer",
                url=TARIFF_2_URL,
            )
        ],
        [
            InlineKeyboardButton(
                "Devotee",
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
                "UNLOCK",
                url=DISCOUNT_URL,
            )
        ]
    ]

    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            "You seem to have doubts.\n\n"
            "Want to unlock a bigger discount?"
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

    message1 = ("You can get a special discount on your Locktober tariff by subscribing to my OnlyFans.\n\n",
    "You'll get:\n",
    "- an extra way to interact with me\n",
    "**access too 100+ pieces of content**\n",
    "plenty to keep you teased and entertained throughout Locktober\n",
    "- additional tasks exclusively for my OF subscribers\n\n",
    "It makes the whole challenge much more interesting.\n\n",
    "**1 MONTH SUBSCRIPTION -- $9.99**")
    
    keyboard1 = [
        [
            InlineKeyboardButton(
                "SHADOW -- 30% OFF" + "\n" + "€50 -- **€35**",
                url=DISCOUNT_URLS[0],
            )
        ],
        [
            InlineKeyboardButton(
                "**ADMIRER -- 20% OFF**" + "\n" + "€200 -- **€160**",
                url=DISCOUNT_URLS[1],
            )
        ],
        [
            InlineKeyboardButton(
                "**DEVOTEE - 15% OFF**" + "\n" + "€500 -- **€425**",
                url=DISCOUNT_URLS[2],
            )
        ]
    ]

    message2 = "Or go for **3 MONTHS -- $29.97** and unlock an even bigger discount:"

    keyboard2 = [
        [
            InlineKeyboardButton(
                "**SHADOW -- 70% OFF**" + "\n" + "€50 -- €15",
                url=DISCOUNT_URLS[3],
            )
        ],
        [
            InlineKeyboardButton(
                "**ADMIRER -- 30% OFF**" + "\n" + "€200 -- **€140**",
                url=DISCOUNT_URLS[4],
            )
        ],
        [
            InlineKeyboardButton(
                "**DEVOTEE -- 20% OFF**" + "\n" + "€500 -- **€400**",
                url=DISCOUNT_URLS[5],
            )
        ],
    ]

    await update.effective_message.reply_text(
        message1,
        reply_markup=InlineKeyboardMarkup(keyboard1),
    )

    await update.effective_message.reply_text(
        message2,
        reply_markup=InlineKeyboardMarkup(keyboard2),
    )
    
    keyboard3 = [
            [
                InlineKeyboardButton(
                    "I SUBSCRIBED TO ONLYFANS",
                    callback_data="tariffs_to_congratulations"
                )
            ],
            [
                InlineKeyboardButton(
                    "**ADMIRER -- 30% OFF**" + "\n" + "€200 -- **€140**",
                    callback_data="tariffs_to_regular_payment"
                )
            ],
        ]

    await update.effective_message.reply_text(
        "Choose how you would like to continue:\n",
        reply_markup=InlineKeyboardMarkup(keyboard3)
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
        f"Kinks: {data.get('kinks', '-')}\n"
        f"Tariff: {data.get('tariff', '-')}\n"
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
# STATE 14: REGULAR PAYMENT
# ============================================================

async def regular_payment(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:

    message = ""
    
    keyboard = [
        [
            InlineKeyboardButton(
                "SHADOW -- €50",
                url=STANDARD_URLS[0],
            )
        ],
        [
            InlineKeyboardButton(
                "ADMIRER -- €200",
                url=STANDARD_URLS[1],
            )
        ],
        [
            InlineKeyboardButton(
                "DEVOTEE -- €500",
                url=STANDARD_URLS[2],
            )
        ]
    ]

    await update.effective_message.reply_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard),
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

            KINKS: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    receive_kinks
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
                ),
                CallbackQueryHandler(
                    tariffs_to_congratulations,
                    pattern="^tariffs_to_congratulations$",
                ),
                CallbackQueryHandler(
                tariffs_to_regular_payment,
                    pattern="^tariffs_to_regular_payment$",
                 ),
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
