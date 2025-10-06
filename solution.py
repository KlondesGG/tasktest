def analyze_temperature(temperatures):
    if temperatures is None or len(temperatures) != 7:
        return None
    
    avg_temp = sum(temperatures) / len(temperatures)
    max_temp = max(temperatures)
    min_temp = min(temperatures)
    hot_days = sum(1 for temp in temperatures if temp > 25)
    cold_days = sum(1 for temp in temperatures if temp < 10)
    
    return {
        "average": round(avg_temp, 1),
        "max": max_temp,
        "min": min_temp,
        "hot_days": hot_days,
        "cold_days": cold_days
    }