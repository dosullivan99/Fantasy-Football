# fpl_data.py
import requests


class FPLPlayer:
    def __init__(self, raw_data):
        self.id = raw_data["id"]
        self.first_name = raw_data["first_name"]
        self.second_name = raw_data["second_name"]
        self.team_id = raw_data["team"]
        self.element_type = raw_data["element_type"]
        self.now_cost = raw_data["now_cost"] / 10
        self.form = float(raw_data.get("form", 0) or 0)
        self.ppg = float(raw_data.get("points_per_game", 0) or 0)
        self.minutes = int(raw_data.get("minutes", 0) or 0)

        self.value_score = 0
        self.adjusted_score = 0

    def calculate_value_score(self):
        if self.now_cost == 0:
            return 0
        self.value_score = ((0.6 * self.form + 0.4 * self.ppg) / self.now_cost) * (self.minutes / 1000)
        return self.value_score

    def calculate_adjusted_score(self, fdr):
        if fdr == 0:
            return 0
        self.adjusted_score = self.calculate_value_score() / fdr
        return self.adjusted_score

    def to_dict(self):
        return {
            "name": f"{self.first_name} {self.second_name}",
            "team_id": self.team_id,
            "position": self.element_type,
            "cost": self.now_cost,
            "form": self.form,
            "ppg": self.ppg,
            "minutes": self.minutes,
            "value_score": round(self.value_score, 3),
            "adjusted_score": round(self.adjusted_score, 3),
        }

class FPLTeam:
    def __init__(self, team_id, fixtures):
        self.team_id = team_id
        self.fixtures = fixtures  # list of dicts with gw, opponent, difficulty

    def average_fdr(self):
        if not self.fixtures:
            return 3.0
        return sum(f["difficulty"] for f in self.fixtures) / len(self.fixtures)

    def next_fixtures(self):
        return self.fixtures

class FPLManager:
    def __init__(self):
        self.players = []
        self.teams = {}
        self.team_id_to_name = {}

    def fetch_all_data(self):
        base_url = "https://fantasy.premierleague.com/api/"
        bootstrap = requests.get(base_url + "bootstrap-static/").json()
        fixtures = requests.get(base_url + "fixtures/").json()

        # Teams and names
        team_data = bootstrap["teams"]
        self.team_id_to_name = {t["id"]: t["name"] for t in team_data}

        # Fixture processing
        current_gw = next(event for event in bootstrap['events'] if event['is_current'])['id']
        next_fixtures = [f for f in fixtures if current_gw <= f["event"] < current_gw + 5]

        team_fixtures = {t["id"]: [] for t in team_data}

        for f in next_fixtures:
            for home_away in ["team_h", "team_a"]:
                team_id = f[home_away]
                opp_id = f["team_a"] if home_away == "team_h" else f["team_h"]
                difficulty = f[f"{home_away}_difficulty"]
                team_fixtures[team_id].append({
                    "gw": f["event"],
                    "opponent": self.team_id_to_name[opp_id],
                    "difficulty": difficulty
                })

        # Store team objects
        self.teams = {tid: FPLTeam(tid, fx) for tid, fx in team_fixtures.items()}

        # Store player objects
        raw_players = bootstrap["elements"]
        self.players = []
        for p in raw_players:
            if p["element_type"] in [1, 2, 3, 4]:  # real players only
                player = FPLPlayer(p)
                fdr = self.teams[player.team_id].average_fdr()
                player.calculate_adjusted_score(fdr)
                self.players.append(player)

    def filter_players(self, position=None, max_cost=None):
        results = self.players
        if position:
            results = [p for p in results if p.element_type == position]
        if max_cost:
            results = [p for p in results if p.now_cost <= max_cost]
        return sorted(results, key=lambda x: x.adjusted_score, reverse=True)

    def get_player_by_name(self, name):
        return next((p for p in self.players if f"{p.first_name} {p.second_name}" == name), None)
