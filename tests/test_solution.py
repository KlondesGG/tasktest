import pytest
import sys
import os

# Добавляем путь к src для импорта solution
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from solution import analyze_temperature


class TestAnalyzeTemperature:
    def test_normal_week(self):
        """Тест с обычными данными за неделю"""
        temperatures = [22, 28, 15, 8, 30, 18, 25]
        result = analyze_temperature(temperatures)
        
        assert result['hot_days'] == 3  # 28, 30, 25
        assert result['cold_days'] == 1  # 8
        assert result['average_temperature'] == round((22+28+15+8+30+18+25)/7, 2)
        assert result['max_temperature'] == 30
        assert result['min_temperature'] == 8
        assert "Жаркая неделя" in result['recommendation']

    def test_all_hot_days(self):
        """Тест когда все дни жаркие"""
        temperatures = [26, 27, 28, 29, 30, 31, 32]
        result = analyze_temperature(temperatures)
        
        assert result['hot_days'] == 7
        assert result['cold_days'] == 0
        assert result['average_temperature'] == round(sum(temperatures)/7, 2)
        assert result['max_temperature'] == 32
        assert result['min_temperature'] == 26
        assert "Жаркая неделя" in result['recommendation']

    def test_all_cold_days(self):
        """Тест когда все дни холодные"""
        temperatures = [5, 6, 3, 2, 8, 9, 4]
        result = analyze_temperature(temperatures)
        
        assert result['hot_days'] == 0
        assert result['cold_days'] == 7
        assert result['average_temperature'] == round(sum(temperatures)/7, 2)
        assert result['max_temperature'] == 9
        assert result['min_temperature'] == 2
        assert "Холодная неделя" in result['recommendation']

    def test_moderate_temperatures(self):
        """Тест с умеренными температурами (нет жарких и холодных дней)"""
        temperatures = [15, 16, 17, 18, 19, 20, 21]
        result = analyze_temperature(temperatures)
        
        assert result['hot_days'] == 0
        assert result['cold_days'] == 0
        assert result['average_temperature'] == round(sum(temperatures)/7, 2)
        assert result['max_temperature'] == 21
        assert result['min_temperature'] == 15
        assert "Умеренная неделя" in result['recommendation']

    def test_empty_list(self):
        """Тест с пустым списком"""
        temperatures = []
        with pytest.raises(ValueError, match="Список должен содержать ровно 7 дней"):
            analyze_temperature(temperatures)

    def test_too_few_days(self):
        """Тест с недостаточным количеством дней"""
        temperatures = [15, 16, 17]
        with pytest.raises(ValueError, match="Список должен содержать ровно 7 дней"):
            analyze_temperature(temperatures)

    def test_too_many_days(self):
        """Тест со слишком большим количеством дней"""
        temperatures = [15, 16, 17, 18, 19, 20, 21, 22]
        with pytest.raises(ValueError, match="Список должен содержать ровно 7 дней"):
            analyze_temperature(temperatures)

    def test_negative_temperatures(self):
        """Тест с отрицательными температурами"""
        temperatures = [-5, -10, 0, 5, 15, 20, 25]
        result = analyze_temperature(temperatures)
        
        assert result['hot_days'] == 1  # 25
        assert result['cold_days'] == 4  # -5, -10, 0, 5 (все < 10°C)
        assert result['average_temperature'] == round(sum(temperatures)/7, 2)
        assert result['max_temperature'] == 25
        assert result['min_temperature'] == -10

    def test_boundary_values(self):
        """Тест с граничными значениями (точно 10 и 25 градусов)"""
        temperatures = [10, 10, 25, 25, 15, 15, 20]
        result = analyze_temperature(temperatures)
        
        # 25°C считается жарким днем, 10°C не считается холодным днем
        assert result['hot_days'] == 2  # 25, 25
        assert result['cold_days'] == 0  # 10 не считается холодным
        assert result['average_temperature'] == round(sum(temperatures)/7, 2)
        assert result['max_temperature'] == 25
        assert result['min_temperature'] == 10

    def test_extreme_temperatures(self):
        """Тест с экстремальными температурами"""
        temperatures = [-30, -20, 40, 50, 0, 10, 25]
        result = analyze_temperature(temperatures)
        
        assert result['hot_days'] == 3  # 40, 50, 25
        assert result['cold_days'] == 3  # -30, -20, 0
        assert result['average_temperature'] == round(sum(temperatures)/7, 2)
        assert result['max_temperature'] == 50
        assert result['min_temperature'] == -30

    def test_all_same_temperature(self):
        """Тест когда все дни одинаковая температура"""
        temperatures = [20, 20, 20, 20, 20, 20, 20]
        result = analyze_temperature(temperatures)
        
        assert result['hot_days'] == 0
        assert result['cold_days'] == 0
        assert result['average_temperature'] == 20.0
        assert result['max_temperature'] == 20
        assert result['min_temperature'] == 20
        assert "Умеренная неделя" in result['recommendation']