import aiofiles
import random
from collections import defaultdict

class MarkovChat:
    def __init__(self):
        # Используем словарь для хранения триграмм
        self.markov_chain = defaultdict(lambda: defaultdict(int))

    async def train(self, filepath, weight=1):
        async with aiofiles.open(filepath, mode='r', encoding='utf-8') as file:
            previous_words = (None, None)
            async for line in file:
                words = line.strip().split()
                for current_word in words:
                    if previous_words[1] is not None:
                        self.markov_chain[previous_words][current_word] += weight
                    previous_words = (previous_words[1], current_word)
                # Сбросить контекст после обработки строки
                previous_words = (None, None)

    async def generate_response(self, query):
        words = query.split()
        if not words:
            return ""

        # Начинаем ответ с последнего слова запроса, если возможно
        last_word = words[-1]
        possible_starts = [key for key in self.markov_chain.keys() if key[1] == last_word]
        if not possible_starts:
            return ""

        current_pair = random.choice(possible_starts)
        response = [current_pair[0], current_pair[1]]
        
        while len(response) < 50:
            next_words = list(self.markov_chain[current_pair].keys())
            if not next_words:
                break
            next_word = random.choice(next_words)
            response.append(next_word)
            current_pair = (current_pair[1], next_word)

        return ' '.join(response)

