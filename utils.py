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
            # Если запрос пуст, выбираем случайное начальное слово
            all_possible_starts = list(self.markov_chain.keys())
            if not all_possible_starts:
                return ""
            last_word = random.choice(all_possible_starts)
        else:
            last_word = words[-1]
            if last_word not in self.markov_chain:
                # Если последнее слово запроса не найдено, выбираем случайное слово
                all_possible_starts = list(self.markov_chain.keys())
                if not all_possible_starts:
                    return ""
                last_word = random.choice(all_possible_starts)

        response = [last_word]
        current_word = last_word
        
        while len(response) < 50:
            next_words = list(self.markov_chain[current_word].keys())
            if not next_words:
                # Если нет следующих слов, выбираем случайное новое начальное слово
                all_possible_starts = list(self.markov_chain.keys())
                if not all_possible_starts:
                    break
                current_word = random.choice(all_possible_starts)
                continue
            next_word = random.choice(next_words)
            response.append(next_word)
            current_word = next_word

        return ' '.join(response)

