import datetime
import re
from typing import List, Dict, Any, Optional, Tuple


def parse_match_data(match_string: str) -> Dict[str, Any]:
    """
    Парсит строку с информацией о матче и возвращает структурированные данные.
    """
    parts = match_string.split(' | ')
    if len(parts) != 4:
        raise ValueError("Invalid format: expected 4 parts separated by ' | '")
    
    date_str, teams_score_str, stadium_str, attendance_str = parts
    
    # Валидация даты
    try:
        year, month, day = map(int, date_str.split('-'))
        datetime.date(year, month, day)
    except (ValueError, TypeError):
        raise ValueError("Invalid date format: expected YYYY-MM-DD")
    
    # Валидация формата команд и счёта - более гибкое регулярное выражение
    # Теперь захватываем любые символы (включая пустые) для счёта и команд
    pattern = r'^\s*(.*?)\s*\(([^:]+):([^)]+)\)\s*(.*?)\s*$'
    match = re.match(pattern, teams_score_str.strip())
    if not match:
        raise ValueError("Invalid teams/score format: expected 'Team1 (X:Y) Team2'")
    
    team1, score1_str, score2_str, team2 = match.groups()
    
    # Валидация названий команд и стадиона
    team1 = team1.strip()
    team2 = team2.strip()
    stadium_str = stadium_str.strip()
    
    if not team1 or not team2 or not stadium_str:
        raise ValueError("Team names and stadium cannot be empty")
    
    # Валидация счёта
    try:
        score1 = int(score1_str)
        score2 = int(score2_str)
        if score1 < 0 or score2 < 0:
            raise ValueError("Invalid score: must be non-negative integers")
    except ValueError:
        raise ValueError("Invalid score: must be non-negative integers")
    
    # Валидация посещаемости
    try:
        attendance = int(attendance_str)
        if attendance <= 0:
            raise ValueError("Invalid attendance: must be a positive integer")
    except ValueError:
        raise ValueError("Invalid attendance: must be a positive integer")
    
    return {
        "date": date_str,
        "team1": team1,
        "score1": score1,
        "team2": team2,
        "score2": score2,
        "stadium": stadium_str,
        "attendance": attendance
    }


def filter_matches_by_criteria(matches_list: List[Dict[str, Any]], **criteria) -> List[Dict[str, Any]]:
    """
    Фильтрует список матчей по произвольным критериям.
    """
    if not matches_list:
        return []
    
    filtered_matches = matches_list.copy()
    
    for key, value in criteria.items():
        if key == 'team':
            filtered_matches = [m for m in filtered_matches 
                              if m['team1'] == value or m['team2'] == value]
        
        elif key == 'date_from':
            filtered_matches = [m for m in filtered_matches if m['date'] >= value]
        
        elif key == 'date_to':
            filtered_matches = [m for m in filtered_matches if m['date'] <= value]
        
        elif key == 'min_attendance':
            filtered_matches = [m for m in filtered_matches if m['attendance'] >= value]
        
        elif key == 'max_attendance':
            filtered_matches = [m for m in filtered_matches if m['attendance'] <= value]
        
        elif key == 'min_total_goals':
            filtered_matches = [m for m in filtered_matches 
                              if (m['score1'] + m['score2']) >= value]
        
        elif key == 'stadium':
            filtered_matches = [m for m in filtered_matches if m['stadium'] == value]
    
    return filtered_matches


def calculate_advanced_team_stats(matches_list: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Вычисляет расширенную статистику для каждой команды.
    """
    if not matches_list:
        return {}
    
    sorted_matches = sorted(matches_list, key=lambda x: x['date'])
    
    team_stats = {}
    team_matches = {}
    
    for match in sorted_matches:
        team1, team2 = match['team1'], match['team2']
        
        if team1 not in team_matches:
            team_matches[team1] = []
        if team2 not in team_matches:
            team_matches[team2] = []
        
        team_matches[team1].append((match['date'], 'home', match))
        team_matches[team2].append((match['date'], 'away', match))
    
    for team, matches in team_matches.items():
        matches.sort(key=lambda x: x[0])
        
        points = 0
        matches_played = len(matches)
        wins = 0
        draws = 0
        losses = 0
        goals_for = 0
        goals_against = 0
        home_points = 0
        away_points = 0
        total_attendance = 0
        
        for date_str, venue, match in matches:
            is_home = venue == 'home'
            
            if is_home:
                team_score = match['score1']
                opponent_score = match['score2']
            else:
                team_score = match['score2']
                opponent_score = match['score1']
            
            goals_for += team_score
            goals_against += opponent_score
            total_attendance += match['attendance']
            
            if team_score > opponent_score:
                wins += 1
                match_points = 3
                if is_home:
                    home_points += 3
                else:
                    away_points += 3
            elif team_score == opponent_score:
                draws += 1
                match_points = 1
                if is_home:
                    home_points += 1
                else:
                    away_points += 1
            else:
                losses += 1
                match_points = 0
            
            points += match_points
        
        win_streak = 0
        for date_str, venue, match in reversed(matches):
            if venue == 'home':
                team_score = match['score1']
                opponent_score = match['score2']
            else:
                team_score = match['score2']
                opponent_score = match['score1']
            
            if team_score > opponent_score:
                win_streak += 1
            else:
                break
        
        avg_attendance = round(total_attendance / matches_played, 2) if matches_played > 0 else 0.0
        
        team_stats[team] = {
            "points": points,
            "matches_played": matches_played,
            "wins": wins,
            "draws": draws,
            "losses": losses,
            "goals_for": goals_for,
            "goals_against": goals_against,
            "goal_diff": goals_for - goals_against,
            "home_points": home_points,
            "away_points": away_points,
            "win_streak": win_streak,
            "avg_attendance": avg_attendance
        }
    
    return team_stats


def rank_teams_advanced(team_stats: Dict[str, Dict[str, Any]], 
                       tiebreaker_order: List[str] = None) -> List[Tuple[int, str, int, int]]:
    """
    Ранжирует команды с учётом каскадной сортировки при равенстве очков.
    """
    if tiebreaker_order is None:
        tiebreaker_order = ['points', 'goal_diff', 'goals_for']
    
    if not team_stats:
        return []
    
    teams_list = []
    for team, stats in team_stats.items():
        teams_list.append({
            'name': team,
            'points': stats['points'],
            'goal_diff': stats['goal_diff'],
            'goals_for': stats['goals_for'],
            'wins': stats['wins']
        })
    
    def get_sort_key(team_data):
        key = []
        for criterion in tiebreaker_order:
            if criterion == 'points':
                key.append(-team_data['points'])
            elif criterion == 'goal_diff':
                key.append(-team_data['goal_diff'])
            elif criterion == 'goals_for':
                key.append(-team_data['goals_for'])
            elif criterion == 'wins':
                key.append(-team_data['wins'])
        return tuple(key)
    
    teams_list.sort(key=get_sort_key)
    
    result = []
    current_rank = 1
    
    for i, team in enumerate(teams_list):
        if i == 0:
            result.append((current_rank, team['name'], team['points'], team['goal_diff']))
        else:
            prev_team = teams_list[i-1]
            is_tie = True
            for criterion in tiebreaker_order:
                if criterion == 'points' and team['points'] != prev_team['points']:
                    is_tie = False
                    break
                elif criterion == 'goal_diff' and team['goal_diff'] != prev_team['goal_diff']:
                    is_tie = False
                    break
                elif criterion == 'goals_for' and team['goals_for'] != prev_team['goals_for']:
                    is_tie = False
                    break
                elif criterion == 'wins' and team['wins'] != prev_team['wins']:
                    is_tie = False
                    break
            
            if is_tie:
                result.append((current_rank, team['name'], team['points'], team['goal_diff']))
            else:
                current_rank = i + 1
                result.append((current_rank, team['name'], team['points'], team['goal_diff']))
    
    return result


def generate_analytics_report(matches_list: List[Dict[str, Any]], 
                            team_stats: Dict[str, Dict[str, Any]], 
                            tournament_table: List[Tuple[int, str, int, int]]) -> Dict[str, Any]:
    """
    Генерирует итоговый аналитический отчёт.
    """
    if not matches_list or not team_stats or not tournament_table:
        return {
            "tournament_leader": "",
            "most_goals_match": {},
            "highest_attendance_match": {},
            "most_efficient_team": "",
            "biggest_upset": None,
            "goal_distribution": {},
            "attendance_by_team": {}
        }
    
    rank_dict = {}
    for rank, team, points, goal_diff in tournament_table:
        rank_dict[team] = rank
    
    tournament_leader = tournament_table[0][1] if tournament_table else ""
    
    most_goals_match = max(matches_list, key=lambda m: m['score1'] + m['score2'])
    highest_attendance_match = max(matches_list, key=lambda m: m['attendance'])
    
    most_efficient_team = ""
    max_efficiency = -1.0
    
    for team, stats in team_stats.items():
        if stats['matches_played'] > 0:
            efficiency = round(stats['points'] / stats['matches_played'], 2)
            if efficiency > max_efficiency:
                max_efficiency = efficiency
                most_efficient_team = team
            elif efficiency == max_efficiency:
                if not most_efficient_team:
                    most_efficient_team = team
    
    biggest_upset = None
    max_rank_diff = -1
    
    for match in matches_list:
        team1, team2 = match['team1'], match['team2']
        score1, score2 = match['score1'], match['score2']
        
        if score1 == score2:
            continue
        
        if team1 not in rank_dict or team2 not in rank_dict:
            continue
        
        if score1 > score2:
            winner = team1
            loser = team2
        else:
            winner = team2
            loser = team1
        
        winner_rank = rank_dict[winner]
        loser_rank = rank_dict[loser]
        
        if winner_rank > loser_rank:
            rank_diff = winner_rank - loser_rank
            if rank_diff > max_rank_diff:
                max_rank_diff = rank_diff
                biggest_upset = {
                    "match": match,
                    "winner_rank": winner_rank,
                    "loser_rank": loser_rank
                }
    
    goal_distribution = {}
    for match in matches_list:
        total_goals = match['score1'] + match['score2']
        goal_distribution[total_goals] = goal_distribution.get(total_goals, 0) + 1
    
    attendance_by_team = {}
    for team, stats in team_stats.items():
        attendance_by_team[team] = stats['avg_attendance']
    
    return {
        "tournament_leader": tournament_leader,
        "most_goals_match": most_goals_match,
        "highest_attendance_match": highest_attendance_match,
        "most_efficient_team": most_efficient_team,
        "biggest_upset": biggest_upset,
        "goal_distribution": goal_distribution,
        "attendance_by_team": attendance_by_team
    }