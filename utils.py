import aiofiles
import random
from collections import defaultdict

class MarkovChat:
    def __init__(self):
        # Используем словарь для хранения биграмм
        self.markov_chain = defaultdict(lambda: defaultdict(int))

    async def train(self, filepath, weight=1):
        async with aiofiles.open(filepath, mode='r', encoding='utf-8') as file:
            previous_word = None
            async for line in file:
                words = line.strip().split()
                for current_word in words:
                    if previous_word is not None:
                        self.markov_chain[previous_word][current_word] += weight
                    previous_word = current_word
                # Сбросить контекст после обработки строки
                previous_word = None

    async def generate_response(self, query):
        words = query.split()
        if not words:
            return ""

        # Начинаем ответ с последнего слова запроса, если возможно
        last_word = words[-1]
        if last_word not in self.markov_chain:
            return ""

        response = [last_word]
        current_word = last_word
        
        while len(response) < 50:
            next_words = list(self.markov_chain[current_word].keys())
            if not next_words:
                break
            next_word = random.choice(next_words)
            response.append(next_word)
            current_word = next_word

        return ' '.join(response)

