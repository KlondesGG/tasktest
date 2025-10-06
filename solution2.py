def analyze_purchases(items, prices, discount_threshold=5000):
    """
    Анализирует покупки и возвращает статистику.
    
    Args:
        items (list): Список названий товаров
        prices (list): Список цен товаров
        discount_threshold (int): Порог для применения скидки (по умолчанию 5000)
        
    Returns:
        dict: Словарь с ключами:
            - total: общая сумма
            - average: средняя цена (округленная до 2 знаков)
            - most_expensive: название самого дорогого товара
            - discount_applied: применена ли скидка
            - final_total: итоговая сумма после скидки
        или None если списки некорректны
    """
    # Проверка корректности входных данных
    if not items or not prices:
        return None
    
    if len(items) != len(prices):
        return None
    
    if any(price < 0 for price in prices):
        return None
    
    # Рассчитываем статистику
    total = sum(prices)
    average = round(total / len(prices), 2)
    
    # Находим самый дорогой товар
    max_price = max(prices)
    max_price_index = prices.index(max_price)
    most_expensive = items[max_price_index]
    
    # Проверяем применение скидки
    discount_applied = total >= discount_threshold
    final_total = total * 0.9 if discount_applied else float(total)
    
    return {
        "total": total,
        "average": average,
        "most_expensive": most_expensive,
        "discount_applied": discount_applied,
        "final_total": round(final_total, 2)
    }