import os
import random
import markovify
from telebot import TeleBot, types

bot = TeleBot(os.getenv('CARROT_BOT_TOKEN'))

global_model = None
if os.path.exists('datasets/global.txt'):
    with open('datasets/global.txt', 'r') as f:
        global_model = markovify.NewlineText(f.read(), well_formed=False)

def get_chat_model(chat_id):
    chat_file = f'datasets/chat_{chat_id}.txt'
    if os.path.exists(chat_file):
        with open(chat_file, 'r') as f:
            chat_model = markovify.NewlineText(f.read(), well_formed=False)
        if global_model:
            chat_model = markovify.combine([chat_model, global_model], [2, 1])
        return chat_model
    else:
        if global_model:
            return global_model
        else:
            return None

def generate_text(chat_id, init_text):
    chat_model = get_chat_model(chat_id)
    if chat_model:
        if init_text:
            try:
                return chat_model.make_sentence_with_start(init_text, max_words=40, tries=100)
            except:
                return chat_model.make_sentence(max_words=40, tries=100)
            return resp
        return chat_model.make_sentence(max_words=40, tries=100)
    else:
        return None
        
@bot.message_handler(content_types=['text'])
def message_handler(message: types.Message):
    chat_id = message.chat.id
    message_text = message.text
    query = ''
    if message_text:
        query = message.text.lower().replace('@carrot_chatbot', '').strip().split()
        if len(query) >= 2:
            query = ' '.join(query[-2:])
        else:
            query = ''
    if query:
        chat_file = f'datasets/chat_{chat_id}.txt'
        with open(chat_file, 'a+') as f:
            if not message_text + "\n" in f.read():
                f.write(message_text + '\n')

        with open('datasets/global.txt', 'a+') as f:
            if not message_text + "\n" in f.read():
                f.write(message_text + '\n')

    if random.randint(1, 8) == 1 or '@carrot_chatbot' in message_text.lower():
        generated_text = generate_text(chat_id, query)
        if generated_text:
            bot.send_message(chat_id, generated_text.replace('@', '@'))

if __name__ == '__main__':
    bot.infinity_polling()
