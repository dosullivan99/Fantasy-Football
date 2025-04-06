import requests
import pandas as pd

# === STEP 1: Load main FPL data ===
base_url = "https://fantasy.premierleague.com/api/"
bootstrap = requests.get(base_url + "bootstrap-static/").json()
fixtures = requests.get(base_url + "fixtures/").json()

players = pd.DataFrame(bootstrap['elements'])
teams = pd.DataFrame(bootstrap['teams'])

# === STEP 2: Clean players ===
players = players[players['element_type'].isin([1, 2, 3, 4])]
team_id_to_name = dict(zip(teams['id'], teams['name']))
players['team_name'] = players['team'].map(team_id_to_name)

element_types = {1: 'Goalkeeper', 2: 'Defender', 3: 'Midfielder', 4: 'Forward'}
players['position'] = players['element_type'].map(element_types)

players['now_cost'] = players['now_cost'] / 10
players['form'] = pd.to_numeric(players['form'], errors='coerce')
players['points_per_game'] = pd.to_numeric(players['points_per_game'], errors='coerce')
players['minutes'] = pd.to_numeric(players['minutes'], errors='coerce')

# === STEP 3: Smarter value score ===
players['value_score'] = (0.6 * players['form'] + 0.4 * players['points_per_game']) / players['now_cost']
players['value_score'] *= players['minutes'] / 1000

# === STEP 4: Fixture Difficulty for Next 5 GWs ===
current_gw = next(event for event in bootstrap['events'] if event['is_current'])['id']
next_fixtures = pd.DataFrame(fixtures)
upcoming = next_fixtures[
    (next_fixtures['event'] >= current_gw) & 
    (next_fixtures['event'] < current_gw + 5)
]

# Compute avg fixture difficulty for each team
team_fdr = {}
for team_id in teams['id']:
    matches = upcoming[
        (upcoming['team_h'] == team_id) | 
        (upcoming['team_a'] == team_id)
    ]
    difficulties = []
    for _, row in matches.iterrows():
        if row['team_h'] == team_id:
            difficulties.append(row['team_h_difficulty'])
        else:
            difficulties.append(row['team_a_difficulty'])
    team_fdr[team_id] = sum(difficulties) / len(difficulties) if difficulties else 3.0

players['avg_fdr'] = players['team'].map(team_fdr)
players['adjusted_score'] = players['value_score'] / players['avg_fdr']

# === STEP 5: Output ===
players_sorted = players.sort_values(by='adjusted_score', ascending=False)

print("\n🏆 Top 30 Adjusted Players (Fixture Difficulty Included)")
print(players_sorted[['first_name', 'second_name', 'team_name', 'position', 'form', 'now_cost', 'value_score', 'avg_fdr', 'adjusted_score']].head(30))

# Save to CSV
players_sorted.to_csv("fpl_adjusted_player_rankings.csv", index=False)
