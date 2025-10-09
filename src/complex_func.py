import re
from collections import Counter
from typing import Dict, Any, List, Optional

def analyze_text_statistics(text: str, min_word_length: int = 1) -> Dict[str, Any]:
    """
    Анализирует статистику текста.
    
    Args:
        text: Текст для анализа
        min_word_length: Минимальная длина слова для учета в статистике
        
    Returns:
        Словарь с различными статистическими показателями текста
    """
    # Проверка входных данных
    if not isinstance(text, str):
        raise TypeError("Text must be a string")
    
    if not text.strip():
        raise ValueError("Text cannot be empty or contain only whitespace")
    
    # Очистка текста и разделение на слова
    words = re.findall(r'\b[a-zA-Zа-яА-Я]+\b', text.lower())
    
    # Фильтрация слов по минимальной длине
    filtered_words = [word for word in words if len(word) >= min_word_length]
    
    # Подсчет предложений
    sentences = re.split(r'[.!?]+', text)
    total_sentences = len([s for s in sentences if s.strip()])
    
    # Базовая статистика
    total_words = len(filtered_words)
    total_characters = len(text)
    
    # Самое длинное и короткое слово
    longest_word = max(filtered_words, key=len) if filtered_words else None
    shortest_word = min(filtered_words, key=len) if filtered_words else None
    
    # Частота слов
    word_frequency = dict(Counter(filtered_words))
    
    # Топ-3 слов
    top_3_words = [{"word": word, "count": count} for word, count in 
                   Counter(filtered_words).most_common(3)]
    
    # Уникальные слова
    unique_words_count = len(set(filtered_words))
    unique_words_percentage = (unique_words_count / total_words * 100) if total_words > 0 else 0.0
    
    # Средняя длина слова
    average_word_length = sum(len(word) for word in filtered_words) / total_words if total_words > 0 else 0.0
    
    return {
        "total_words": total_words,
        "total_sentences": total_sentences,
        "total_characters": total_characters,
        "longest_word": longest_word,
        "shortest_word": shortest_word,
        "word_frequency": word_frequency,
        "top_3_words": top_3_words,
        "unique_words_count": unique_words_count,
        "unique_words_percentage": unique_words_percentage,
        "average_word_length": average_word_length
    }

