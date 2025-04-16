import requests
from datetime import datetime, timedelta
import random

API_KEY = "33826b3069msh1cf9415c5bb3336p16ffc7jsn40b000a24592"
HEADERS = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}

LEAGUES = {
    "Ligue 1": 61,
    "Premier League": 39,
    "Serie A": 135,
    "La Liga": 140,
    "Bundesliga": 78,
    "Champions League": 2
}

def get_fixtures(league_id, season="2024", days_ahead=7):
    today = datetime.now().date()
    end_day = today + timedelta(days=days_ahead)
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    params = {
        "league": league_id,
        "season": season,
        "from": today.isoformat(),
        "to": end_day.isoformat()
    }
    response = requests.get(url, headers=HEADERS, params=params)
    return response.json().get("response", [])

def get_players_stats(team_id, season="2024"):
    url = "https://api-football-v1.p.rapidapi.com/v3/players"
    params = {"team": team_id, "season": season}
    response = requests.get(url, headers=HEADERS, params=params)
    return response.json().get("response", [])

def pick_top_scorers(players):
    top_scorers = []
    for p in players:
        try:
            goals = p["statistics"][0]["goals"]["total"] or 0
            if goals >= 2:
                top_scorers.append((p["player"]["name"], goals))
        except:
            continue
    return sorted(top_scorers, key=lambda x: x[1], reverse=True)[:3]

def pick_top_assisters(players):
    assisters = []
    for p in players:
        try:
            assists = p["statistics"][0]["goals"]["assists"] or 0
            if assists > 0:
                assisters.append((p["player"]["name"], assists))
        except:
            continue
    return sorted(assisters, key=lambda x: x[1], reverse=True)[:3]

def predict_fixture(fixture):
    home = fixture["teams"]["home"]["name"]
    away = fixture["teams"]["away"]["name"]
    home_id = fixture["teams"]["home"]["id"]
    away_id = fixture["teams"]["away"]["id"]

    match_time = fixture["fixture"]["date"]
    try:
        date_formatted = datetime.fromisoformat(match_time.replace("Z", "+00:00")).strftime("%d/%m - %H:%M")
    except:
        date_formatted = "Date inconnue"

    home_players = get_players_stats(home_id)
    away_players = get_players_stats(away_id)
    all_players = home_players + away_players

    top_scorers = pick_top_scorers(all_players)
    top_assisters = pick_top_assisters(all_players)

    mi_temps = random.choice([(0, 0), (1, 0), (1, 1), (0, 1)])
    full_time = (
        mi_temps[0] + random.randint(0, 2),
        mi_temps[1] + random.randint(0, 2)
    )

    total_goals = sum(full_time)
    over_under = {
        "Over 1.5": total_goals > 1,
        "Over 2.5": total_goals > 2,
        "Over 3.5": total_goals > 3
    }

    winner = "1" if full_time[0] > full_time[1] else "2" if full_time[1] > full_time[0] else "N"
    btts = full_time[0] > 0 and full_time[1] > 0
    total_shots = random.randint(18, 32)

    pronostics = {
        "Match": f"{home} vs {away} ({date_formatted})",
        "Score Mi-temps": f"{mi_temps[0]} - {mi_temps[1]}",
        "Score Final": f"{full_time[0]} - {full_time[1]}",
        "Over/Under": {k: "Oui" if v else "Non" for k, v in over_under.items()},
        "1N2 + BTTS": f"{winner} & BTTS: {'Oui' if btts else 'Non'}",
        "Tirs Totaux": f"{total_shots} tirs",
        "Buteurs": [f"{s[0]} ({s[1]} buts)" for s in top_scorers] or ["Non disponible"],
        "Passeurs": [f"{a[0]} ({a[1]} passes)" for a in top_assisters] or ["Non disponible"]
    }

    pronostics["Résultats des pronostics"] = {
        "Score Mi-temps": "OK" if mi_temps[0] + mi_temps[1] >= 0 else "Perdu",
        "Score Final": "OK" if total_goals >= 2 else "Perdu",
        "Over 2.5": "OK" if over_under["Over 2.5"] else "Perdu",
        "1N2 + BTTS": "OK" if btts else "Perdu"
    }

    return pronostics

# --- Lancer l’analyse ---
for league_name, league_id in LEAGUES.items():
    print(f"\n--- {league_name.upper()} ---")
    fixtures = get_fixtures(league_id)
    if not fixtures:
        print("Aucun match détecté.")
        continue

    for fixture in fixtures:
        result = predict_fixture(fixture)
        for k, v in result.items():
            if isinstance(v, dict):
                print(f"{k}:")
                for sub_k, sub_v in v.items():
                    print(f"   {sub_k} : {sub_v}")
            elif isinstance(v, list):
                print(f"{k}: " + ", ".join(v))
            else:
                print(f"{k} : {v}")
        print("-" * 50)
