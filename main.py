from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiofiles import os, open
from utils import MarkovChat
import asyncio
import random

bot = Bot(os.getenv('CARROT_BOT_TOKEN'))
dp = Dispatcher()

@dp.message()
async def handle_message(message: types.Message):
    datasets_list = await os.listdir('datasets')
    if not f'{message.chat.id}.txt' in datasets_list:
        async with open(f'datasets/{message.chat.id}.txt', 'w') as f:
            await f.write(f'{message.text} <|end|>\n')
        async with open('datasets/global_dataset.txt', 'a') as f:
            await f.write(f'{message.text} <|end|>\n')
    else:
        async with open(f'datasets/{message.chat.id}.txt', 'a+') as f:
            await f.write(f'{message.text} <|end|>\n')
        async with open('datasets/global_dataset.txt', 'a') as f:
            await f.write(f'{message.text} <|end|>\n')
        if '@carrot_chatbot' in message.text.lower() or random.randint(0, 10) == 5:
            chain = MarkovChat()
            await chain.train('datasets/global_dataset.txt', weight=1)
            await chain.train(f'datasets/{message.chat.id}.txt', weight=5)
            response = await chain.generate_response(message.text)
            async with open(f'datasets/{message.chat.id}.txt', 'a+') as f:
                await f.write(f'{response} <|end|>\n')
            async with open('datasets/global_dataset.txt', 'a') as f:
                await f.write(f'{response} <|end|>\n')
            await message.answer(response)
        

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())