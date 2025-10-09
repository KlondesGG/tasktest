def analyze_temperature(temperatures):
    """
    Анализирует температуру за неделю и возвращает статистику.
    
    Args:
        temperatures (list): Список температур за 7 дней
        
    Returns:
        dict: Словарь с результатами анализа
        
    Raises:
        ValueError: Если список не содержит ровно 7 дней
    """
    # Проверка что список содержит ровно 7 дней
    if len(temperatures) != 7:
        raise ValueError("Список должен содержать ровно 7 дней")
    
    # Подсчет жарких дней (≥ 25°C)
    hot_days = sum(1 for temp in temperatures if temp >= 25)
    
    # Подсчет холодных дней (< 10°C)
    cold_days = sum(1 for temp in temperatures if temp < 10)
    
    # Расчет средней температуры
    average_temp = sum(temperatures) / len(temperatures)
    
    # Нахождение максимальной и минимальной температуры
    max_temp = max(temperatures)
    min_temp = min(temperatures)
    
    # Определение рекомендации
    if hot_days >= 3:
        recommendation = "Жаркая неделя, рекомендуется пить больше воды"
    elif cold_days >= 3:
        recommendation = "Холодная неделя, рекомендуется одеваться теплее"
    else:
        recommendation = "Умеренная неделя, хорошая погода для прогулок"
    
    return {
        'hot_days': hot_days,
        'cold_days': cold_days,
        'average_temperature': round(average_temp, 2),
        'max_temperature': max_temp,
        'min_temperature': min_temp,
        'recommendation': recommendation
    }