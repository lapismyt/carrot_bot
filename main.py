import os
import random
import markovify
from telebot import TeleBot, types

bot = TeleBot(os.getenv('CARROT_BOT_TOKEN'))

global_model = None
if os.path.exists('datasets/global.txt'):
    with open('datasets/global.txt', 'r') as f:
        global_model = markovify.Text(f.read())

def get_chat_model(chat_id):
    chat_file = f'datasets/chat_{chat_id}.txt'
    if os.path.exists(chat_file):
        with open(chat_file, 'r') as f:
            chat_model = markovify.Text(f.read())
        if global_model:
            chat_model = markovify.combine([chat_model, global_model], [1, 0.5])
        return chat_model
    else:
        if global_model:
            return global_model
        else:
            return None

def generate_text(chat_id):
    chat_model = get_chat_model(chat_id)
    if chat_model:
        return chat_model.make_short_sentence(140)
    else:
        return None
        
@bot.message_handler(content_types=['text'])
def message_handler(message: types.Message):
    chat_id = message.chat.id
    message_text = message.text

    chat_file = f'datasets/chat_{chat_id}.txt'
    with open(chat_file, 'a') as f:
        f.write(message_text + '\n')

    with open('datasets/global.txt', 'a') as f:
        f.write(message_text + '\n')

    if random.randint(1, 6) == 1 or '@carrot_chatbot' in message_text.lower():
        generated_text = generate_text(chat_id)
        if generated_text:
            bot.send_message(chat_id, generated_text)

if __name__ == '__main__':
    bot.infinity_polling()
