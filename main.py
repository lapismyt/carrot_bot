import os
import random
import markovify
from telebot import TeleBot, types
from telebot.util import content_type_media
from loguru import logger

logger.add("carrot_bot.log", 
           rotation="10 MB", 
           retention="7 days", 
           format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
           level="DEBUG")

os.makedirs('datasets', exist_ok=True)
logger.info("Created datasets directory")

bot = TeleBot(os.getenv('CARROT_BOT_TOKEN'))
logger.info("Bot instance created")

try:
    bot_info = bot.get_me()
    BOT_USERNAME = bot_info.username
    if not BOT_USERNAME:
        logger.warning("Bot username is not set!")
        BOT_USERNAME = "carrot_chatbot"  # fallback
    logger.success(f"Bot username: @{BOT_USERNAME}")
except Exception as e:
    logger.error(f"Failed to get bot info: {e}")
    BOT_USERNAME = "carrot_chatbot"  # fallback
    logger.warning(f"Using fallback username: @{BOT_USERNAME}")

global_model = None
global_dataset_path = 'datasets/global.txt'

if os.path.exists(global_dataset_path):
    try:
        with open(global_dataset_path, 'r', encoding='utf-8') as f:
            text = f.read()
            if text.strip():
                global_model = markovify.NewlineText(text, well_formed=False)
                logger.success("Global model loaded")
            else:
                logger.warning("Global dataset is empty")
    except Exception as e:
        logger.error(f"Error loading global model: {e}")
else:
    logger.warning("Global dataset file not found")

def get_chat_model(chat_id):
    chat_file = f'datasets/chat_{chat_id}.txt'
    if not os.path.exists(chat_file):
        logger.debug(f"Chat {chat_id} dataset not found")
        return global_model
    
    try:
        with open(chat_file, 'r', encoding='utf-8') as f:
            text = f.read()
            if not text.strip():
                logger.warning(f"Chat {chat_id} dataset is empty")
                return global_model
            
            chat_model = markovify.NewlineText(text, well_formed=False)
            logger.info(f"Chat model for {chat_id} loaded")
            
            if global_model:
                combined = markovify.combine([chat_model, global_model], [2, 1])
                logger.info(f"Models combined for chat {chat_id}")
                return combined
            return chat_model
    except Exception as e:
        logger.error(f"Error loading chat {chat_id} model: {e}")
        return global_model

def generate_text(chat_id, init_text=None):
    logger.info(f"Generating text for chat {chat_id} with init: '{init_text}'")
    
    chat_model = get_chat_model(chat_id)
    if not chat_model:
        logger.warning(f"No model available for chat {chat_id}")
        return None

    try:
        if init_text:
            sentence = chat_model.make_sentence_with_start(
                init_text, 
                max_words=20, 
                tries=100,
                strict=False
            )
            if sentence:
                logger.info(f"Generated with start '{init_text}': {sentence}")
                return sentence
            logger.info(f"Failed to generate with start '{init_text}', trying without")
        return sentence
    except Exception as e:
        logger.error(f"Generation error for chat (+init) {chat_id}: {e}")
        logger.info(f"Failed to generate with start '{init_text}', trying without")

    try:
        sentence = chat_model.make_sentence(
            max_words=20, 
            tries=200,
            max_overlap_ratio=0.9,
            max_overlap_total=20
        )
        if sentence:
            logger.info(f"Generated: {sentence}")
            return sentence
        else:
            logger.warning(f"Generation failed for chat {chat_id} (returned None)")
            return None
    except Exception as e:
        logger.error(f"Generation error for chat (-init) {chat_id}: {e}")
        return None

def save_message(chat_id, text):
    if not text.strip():
        logger.info("Empty message skipped")
        return
    
    logger.info(f"Saving message for chat {chat_id}: '{text}'")
    
    chat_file = f'datasets/chat_{chat_id}.txt'
    try:
        with open(chat_file, 'a', encoding='utf-8') as f:
            f.write(text + '\n')
        logger.info(f"Message saved to chat {chat_id} dataset")
    except Exception as e:
        logger.error(f"Error saving to chat {chat_id} dataset: {e}")
    
    try:
        with open(global_dataset_path, 'a', encoding='utf-8') as f:
            f.write(text + '\n')
        logger.info("Message saved to global dataset")
    except Exception as e:
        logger.error(f"Error saving to global dataset: {e}")

@bot.message_handler(content_types=['text'])
def handle_message(message: types.Message):
    if message.from_user.is_bot:
        logger.info(f"Ignored bot message from user {message.from_user.id}")
        return

    chat_id = message.chat.id
    text = message.text.strip()
    
    logger.info(f"Message from {message.from_user.id} in {chat_id}: {text}")
    
    mentioned = False
    if BOT_USERNAME:
        bot_mention = f"@{BOT_USERNAME}".lower()
        mentioned = bot_mention in text.lower()
        logger.info(f"Mention check: {'found' if mentioned else 'not found'}")

    if text:
        save_message(chat_id, text)
    
    should_reply = mentioned or random.randint(1, 8) == 1
    logger.info(f"Should reply: {'yes' if should_reply else 'no'}")

    if should_reply:
        init_text = None
        if mentioned:
            clean_text = text.lower().replace(f"@{BOT_USERNAME}", "").strip()
            words = clean_text.split()[-2:]
            if words:
                init_text = " ".join(words)
                logger.info(f"Using init text: '{init_text}'")
        
        generated = generate_text(chat_id, init_text)
        if generated:
            response = generated.replace('@', '')
            try:
                bot.reply_to(message, response)
                logger.success(f"Replied in chat {chat_id}: {response}")
            except Exception as e:
                logger.error(f"Failed to send message in chat {chat_id}: {e}")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    help_text = (
        "Привет! Я бот, который учится на ваших сообщениях.\n\n"
        "Просто общайтесь в чате, а я буду иногда отвечать "
        "сгенерированными фразами на основе ваших сообщений.\n\n"
        f"Чтобы обратиться ко мне напрямую, упомяните мой юзернейм: @{BOT_USERNAME}"
    )
    try:
        bot.reply_to(message, help_text)
        logger.info(f"Sent help message to {message.chat.id}")
    except Exception as e:
        logger.error(f"Failed to send help message: {e}")

if __name__ == '__main__':
    logger.info("Starting bot...")
    try:
        bot.infinity_polling()
    except Exception as e:
        logger.critical(f"Bot crashed: {e}")
        raise
