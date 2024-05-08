from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiofiles import open
from aiofiles import os as aioos
import asyncio
import random
import os
import markovify

bot = Bot(os.getenv('CARROT_BOT_TOKEN'))
dp = Dispatcher()

@dp.message()
async def handle_message(message: types.Message):
    datasets_list = await aioos.listdir('datasets')
    if message.text is None or message.text.startswith('/') or message.text.lower() == '@carrot_chatbot':
        return None
    if not f'chat_{message.chat.id}.txt' in datasets_list:
        async with open(f'datasets/chat_{message.chat.id}.txt', 'w') as f:
            await f.write(f'{message.text.lower().replace("@carrot_chatbot", "")}\n')
        async with open('datasets/global_dataset.txt', 'a') as f:
            await f.write(f'{message.text.lower().replace("@carrot_chatbot", "")}\n')
    else:
        async with open(f'datasets/chat_{message.chat.id}.txt', 'a+') as f:
            await f.write(f'{message.text.lower().replace("@carrot_chatbot", "")}\n')
        async with open('datasets/global_dataset.txt', 'a') as f:
            await f.write(f'{message.text.lower().replace("@carrot_chatbot", "")}\n')
        if '@carrot_chatbot' in message.text.lower() or random.randint(2, 10) == 5:
            async with open(f'datasets/chat_{message.chat.id}.txt') as f:
                chain = markovify.NewlineText(await f.read())
                query = message.text.lower().replace('@carrot_chatbot', '')
                response = await chain.make_short_sentence(150)
            if not response:
                print("Empty")
                return None
            async with open(f'datasets/chat_{message.chat.id}.txt', 'a+') as f:
                lines = len((await f.read()).split('\n'))
                if lines >= 150:
                    await f.write(f'{response}\n')
            async with open('datasets/global_dataset.txt', 'a+') as f:
                lines = len((await f.read()).split('\n'))
                if lines >= 150:
                    await f.write(f'{response}\n')
            await message.answer(response)
        

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
