from telegram import Update
from telegram.ext import CallbackContext, ContextTypes


async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Welcome to the News Summary Bot! Use /subscribe to subscribe to a channel."
    )


async def create_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if user provided a topic name
    if context.args:
        topic_name = " ".join(context.args)

        # Create the topic in the chat
        chat = update.effective_chat

        try:
            # Create the forum topic (requires bot to be an admin with can_manage_topics permission)
            result = await chat.create_forum_topic(name=topic_name)
            await update.message.reply_text(
                f"Topic '{topic_name}' created successfully!"
            )
        except Exception as e:
            await update.message.reply_text(f"Failed to create topic: {str(e)}")
    else:
        await update.message.reply_text("Please provide a topic name.")


async def get_topics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fetch and display current topics."""
    user = update.effective_user
    chat = update.effective_chat
    thread_id = update.message.message_thread_id

    is_admin = user.id in [
        admin.user.id for admin in await context.bot.get_chat_administrators(chat.id)
    ]
    if not is_admin:
        await context.bot.send_message(
            chat_id=chat.id,
            text="Only admins use this command.",
            message_thread_id=thread_id,
        )
        return

    # check if the message is a reply to another message
    if not update.message.reply_to_message:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Please reply to a player to award a point.",
            message_thread_id=thread_id,
        )
        return
