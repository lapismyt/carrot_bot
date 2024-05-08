import random
import asyncio
from collections import defaultdict, Counter
from aiofiles import open

class MarkovChat:
    def __init__(self):
        self.markov_chain = defaultdict(list)
        self.start_words = defaultdict(Counter)
        self.max_length = 20

    async def train(self, filename, weight=1):
        async with open(filename) as file:
            text = (await file.read()).strip()
            messages = text.split("\n")  # Split messages by newline
            for i in range(len(messages) - 1):
                await self.add_to_chain(messages[i].strip(), messages[i + 1].strip(), weight)

    async def add_to_chain(self, current_msg, next_msg, weight=1):
        words = current_msg.split()
        for i in range(len(words) - 1):
            self.markov_chain[words[i]].extend([words[i + 1]] * weight)
        
        if next_msg:
            next_msg_words = next_msg.split()
            if next_msg_words:
                self.start_words[words[-1]].update({next_msg_words[0]: weight})

    async def generate_response(self, message):
        response = []
        words = message.split()
        if not words or words[-1] not in self.start_words:
            start_word = random.choice(list(self.start_words[random.choice(list(self.start_words.keys()))]))
        else:
            start_word = random.choice(list(self.start_words[words[-1]].elements()))

        word = start_word
        while word in self.markov_chain and len(response) < self.max_length:
            response.append(word)
            word = random.choice(self.markov_chain[word])

        return ' '.join(response)

# Example usage
async def main():
    bot = MarkovChat()
    await bot.train('global_dataset.txt', weight=1)
    await bot.train('local_dataset.txt', weight=3)
    conversation = ''
    while True:
        query = input('Вы: ')
        conversation = ' '.join([conversation, query])
        response = await bot.generate_response(conversation)
        print('Бот:', response)
        conversation = ' '.join([conversation, response])

if __name__ == '__main__':
    asyncio.run(main())

