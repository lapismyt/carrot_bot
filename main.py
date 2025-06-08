import os
import random
import markovify
from telebot import TeleBot, types
from telebot.util import content_type_media

os.makedirs('datasets', exist_ok=True)

bot = TeleBot(os.getenv('CARROT_BOT_TOKEN'))
BOT_USERNAME = "carrot_chatbot"

global_model = None
global_dataset_path = 'datasets/global.txt'
if os.path.exists(global_dataset_path):
    with open(global_dataset_path, 'r', encoding='utf-8') as f:
        global_model = markovify.NewlineText(f.read(), well_formed=False)

def get_chat_model(chat_id):
    chat_file = f'datasets/chat_{chat_id}.txt'
    if os.path.exists(chat_file):
        with open(chat_file, 'r', encoding='utf-8') as f:
            chat_model = markovify.NewlineText(f.read(), well_formed=False)
        if global_model:
            return markovify.combine([chat_model, global_model], [2, 1])
        return chat_model
    return global_model

def generate_text(chat_id, init_text=None):
    chat_model = get_chat_model(chat_id)
    if not chat_model:
        return None

    if init_text:
        try:
            return chat_model.make_sentence_with_start(
                init_text, 
                max_words=40, 
                tries=100,
                strict=False
            )
        except Exception:
            pass
    
    return chat_model.make_sentence(max_words=40, tries=100)

def save_message(chat_id, text):
    chat_file = f'datasets/chat_{chat_id}.txt'
    with open(chat_file, 'a', encoding='utf-8') as f:
        f.write(text + '\n')
    
    with open(global_dataset_path, 'a', encoding='utf-8') as f:
        f.write(text + '\n')

@bot.message_handler(content_types=['text'])
def handle_message(message: types.Message):
    if message.from_user.is_bot:
        return

    chat_id = message.chat.id
    text = message.text.strip()
    mentioned = f"@{BOT_USERNAME}".lower() in text.lower()
    
    save_message(chat_id, text)
    
    if mentioned or random.randint(1, 8) == 1:
        query_words = text.replace(f"@{BOT_USERNAME}", "").split()[-2:]
        init_text = " ".join(query_words) if query_words else None
        
        generated = generate_text(chat_id, init_text)
        if generated:
            bot.reply_to(message, generated.replace('@', ''))

if __name__ == '__main__':
    print("Bot is running...")
    bot.infinity_polling()
