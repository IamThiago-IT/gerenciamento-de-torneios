#!/usr/bin/env python3
# coding: utf-8
"""
tournament_system.py
Sistema simples para gestão de jogadores, equipes e torneios.
Funcionalidades:
 - cadastro/edição de jogadores e equipes
 - torneios individuais (jogador vs jogador) e coletivos (equipe vs equipe)
 - geração automática de rodadas (mata-mata e pontos corridos/round-robin)
 - registro manual de resultados
 - simulação automática de resultados
 - geração de rankings e estatísticas (vitórias/derrotas/empates)
 - persistência usando padrão DAO: JSON (texto) e pickle (binário)
 - exportar ranking final
"""

from __future__ import annotations
import json
import pickle
import random
import math
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple, Union
from datetime import datetime
import uuid
import os

# --------------------------
# Domínio: Jogadores/Equipes
# --------------------------

@dataclass
class Player:
    id: str
    name: str
    age: int
    sport: str
    player_type: str = "amador"  # "amador" ou "profissional"
    matches_played: int = 0
    wins: int = 0
    losses: int = 0
    draws: int = 0
    rating: float = 1000.0  # para simular força (optional)

    def record_result(self, scored: int, conceded: int):
        self.matches_played += 1
        if scored > conceded:
            self.wins += 1
        elif scored < conceded:
            self.losses += 1
        else:
            self.draws += 1

@dataclass
class Team:
    id: str
    name: str
    members: List[str] = field(default_factory=list)  # lista de player ids
    matches_played: int = 0
    wins: int = 0
    losses: int = 0
    draws: int = 0

    def record_result(self, scored: int, conceded: int):
        self.matches_played += 1
        if scored > conceded:
            self.wins += 1
        elif scored < conceded:
            self.losses += 1
        else:
            self.draws += 1

# --------------------------
# DAO: Persistência (padrão)
# --------------------------

class PersistenceDAO:
    """Interface simplificada"""
    def save_players(self, players: Dict[str, Player]) -> None: raise NotImplementedError
    def load_players(self) -> Dict[str, Player]: raise NotImplementedError
    def save_teams(self, teams: Dict[str, Team]) -> None: raise NotImplementedError
    def load_teams(self) -> Dict[str, Team]: raise NotImplementedError
    def save_tournament(self, tournament_data: dict, filename: str) -> None: raise NotImplementedError
    def load_tournament(self, filename: str) -> dict: raise NotImplementedError
    def export_ranking(self, ranking: List[Tuple[str, int]], filename: str) -> None: raise NotImplementedError

class JsonFileDAO(PersistenceDAO):
    def __init__(self, folder: str = "data_json"):
        self.folder = folder
        os.makedirs(self.folder, exist_ok=True)
        self.players_file = os.path.join(self.folder, "players.json")
        self.teams_file = os.path.join(self.folder, "teams.json")

    def save_players(self, players: Dict[str, Player]) -> None:
        with open(self.players_file, "w", encoding="utf-8") as f:
            json.dump({pid: asdict(p) for pid, p in players.items()}, f, ensure_ascii=False, indent=2)

    def load_players(self) -> Dict[str, Player]:
        if not os.path.exists(self.players_file):
            return {}
        with open(self.players_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {pid: Player(**pdata) for pid, pdata in data.items()}

    def save_teams(self, teams: Dict[str, Team]) -> None:
        with open(self.teams_file, "w", encoding="utf-8") as f:
            json.dump({tid: asdict(t) for tid, t in teams.items()}, f, ensure_ascii=False, indent=2)

    def load_teams(self) -> Dict[str, Team]:
        if not os.path.exists(self.teams_file):
            return {}
        with open(self.teams_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {tid: Team(**tdata) for tid, tdata in data.items()}

    def save_tournament(self, tournament_data: dict, filename: str) -> None:
        path = os.path.join(self.folder, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(tournament_data, f, ensure_ascii=False, indent=2)

    def load_tournament(self, filename: str) -> dict:
        path = os.path.join(self.folder, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def export_ranking(self, ranking: List[Tuple[str, int]], filename: str) -> None:
        path = os.path.join(self.folder, filename)
        with open(path, "w", encoding="utf-8") as f:
            for pos, (name, pts) in enumerate(ranking, start=1):
                f.write(f"{pos}. {name} - {pts}\n")

class PickleDAO(PersistenceDAO):
    def __init__(self, folder: str = "data_bin"):
        self.folder = folder
        os.makedirs(self.folder, exist_ok=True)
        self.players_file = os.path.join(self.folder, "players.pkl")
        self.teams_file = os.path.join(self.folder, "teams.pkl")

    def save_players(self, players: Dict[str, Player]) -> None:
        with open(self.players_file, "wb") as f:
            pickle.dump(players, f)

    def load_players(self) -> Dict[str, Player]:
        if not os.path.exists(self.players_file):
            return {}
        with open(self.players_file, "rb") as f:
            return pickle.load(f)

    def save_teams(self, teams: Dict[str, Team]) -> None:
        with open(self.teams_file, "wb") as f:
            pickle.dump(teams, f)

    def load_teams(self) -> Dict[str, Team]:
        if not os.path.exists(self.teams_file):
            return {}
        with open(self.teams_file, "rb") as f:
            return pickle.load(f)

    def save_tournament(self, tournament_data: dict, filename: str) -> None:
        path = os.path.join(self.folder, filename)
        with open(path, "wb") as f:
            pickle.dump(tournament_data, f)

    def load_tournament(self, filename: str) -> dict:
        path = os.path.join(self.folder, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        with open(path, "rb") as f:
            return pickle.load(f)

    def export_ranking(self, ranking: List[Tuple[str, int]], filename: str) -> None:
        path = os.path.join(self.folder, filename)
        with open(path, "w", encoding="utf-8") as f:
            for pos, (name, pts) in enumerate(ranking, start=1):
                f.write(f"{pos}. {name} - {pts}\n")

# --------------------------
# Torneios e Partidas
# --------------------------

@dataclass
class Match:
    id: str
    a: str  # id do competidor A (player id ou team id)
    b: str  # id do competidor B
    score_a: Optional[int] = None
    score_b: Optional[int] = None
    played: bool = False
    round_number: Optional[int] = None

    def set_result(self, score_a: int, score_b: int):
        self.score_a = score_a
        self.score_b = score_b
        self.played = True

class Tournament:
    def __init__(self, id: Optional[str], name: str, competitors: List[str], kind: str = "individual"):
        # kind: "individual" or "team"
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.kind = kind
        self.competitors = competitors[:]  # lista de ids (players ou teams)
        self.matches: List[Match] = []
        self.type: str = "pontos_corridos"  # ou "mata_mata"
        self.created_at = datetime.utcnow().isoformat()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "kind": self.kind,
            "competitors": self.competitors,
            "matches": [asdict(m) for m in self.matches],
            "type": self.type,
            "created_at": self.created_at,
        }

    # Geração de torneio: mata-mata ou round-robin
    def generate_round_robin(self):
        """Round-robin (todos contra todos) gera matches e round numbers (rodadas)."""
        players = self.competitors[:]
        n = len(players)
        if n < 2:
            return
        # se ímpar, adiciona bye (None)
        bye = None
        if n % 2 == 1:
            players.append("BYE")
            n += 1
        half = n // 2
        rounds = n - 1
        schedule = []
        arr = players[:]
        for r in range(rounds):
            pairs = []
            for i in range(half):
                a = arr[i]
                b = arr[n - 1 - i]
                if a != "BYE" and b != "BYE":
                    pairs.append((a, b))
            schedule.append(pairs)
            # rotate
            arr = [arr[0]] + [arr[-1]] + arr[1:-1]
        # transformar em matches
        self.matches = []
        mid = 1
        for rnd_pairs in schedule:
            for (a,b) in rnd_pairs:
                m = Match(id=str(uuid.uuid4()), a=a, b=b, round_number=mid)
                self.matches.append(m)
            mid += 1

    def generate_knockout(self):
        """Gera bracket simples (preenche com byes se necessário)."""
        players = self.competitors[:]
        n = len(players)
        if n < 2:
            return
        # próxima potência de dois
        power = 1
        while power < n:
            power *= 2
        # adicionar BYE para completar
        while len(players) < power:
            players.append("BYE")
        random.shuffle(players)
        # primeira rodada pares
        self.matches = []
        round_no = 1
        pairs = []
        for i in range(0, len(players), 2):
            a = players[i]
            b = players[i+1]
            if a != "BYE" and b != "BYE":
                pairs.append((a, b))
            elif a != "BYE" and b == "BYE":
                # auto avança; cria uma match marcada como já jogada com vitória de a
                m = Match(id=str(uuid.uuid4()), a=a, b=b, round_number=round_no)
                m.set_result(1, 0)
                m.played = True
                self.matches.append(m)
                continue
            elif a == "BYE" and b != "BYE":
                m = Match(id=str(uuid.uuid4()), a=a, b=b, round_number=round_no)
                m.set_result(0, 1)
                m.played = True
                self.matches.append(m)
                continue
            m = Match(id=str(uuid.uuid4()), a=a, b=b, round_number=round_no)
            self.matches.append(m)
        # future rounds serão gerados dinamicamente conforme resultados
        self.type = "mata_mata"

    def get_unplayed_matches(self) -> List[Match]:
        return [m for m in self.matches if not m.played]

    def register_result_manual(self, match_id: str, score_a: int, score_b: int):
        m = next((x for x in self.matches if x.id == match_id), None)
        if not m:
            raise ValueError("Match not found")
        m.set_result(score_a, score_b)

    def simulate_match(self, match: Match, players_db: Dict[str, Player], teams_db: Dict[str, Team], rng=random):
        """Simula resultado e atualiza a partida. Usa ratings se for jogador."""
        # If BYE present, skip
        if match.a == "BYE" or match.b == "BYE":
            if match.a == "BYE":
                match.set_result(0, 1)
            else:
                match.set_result(1, 0)
            return match
        # get strengths
        def strength_of(id_):
            if id_ in players_db:
                p = players_db[id_]
                base = p.rating
                if p.player_type == "profissional":
                    base *= 1.05
                return base
            elif id_ in teams_db:
                t = teams_db[id_]
                # average player rating
                vals = [players_db[mid].rating for mid in t.members if mid in players_db]
                if not vals:
                    return 1000.0
                return sum(vals) / len(vals)
            else:
                # unknown id -> neutral
                return 1000.0
        sa = strength_of(match.a)
        sb = strength_of(match.b)
        # probabilidades usando logistic
        prob_a = 1.0 / (1.0 + math.exp((sb - sa) / 400.0))
        # simulate goals/points: sample from Poisson-like by mean
        mean_total = 2.5  # média de gols/pontos
        # allocate expected values by prob
        ea = mean_total * prob_a
        eb = mean_total * (1 - prob_a)
        # sample integer scores
        score_a = rng.poissonlike(ea) if hasattr(rng, "poissonlike") else max(0, int(rng.gauss(ea, 1.2)))
        score_b = rng.poissonlike(eb) if hasattr(rng, "poissonlike") else max(0, int(rng.gauss(eb, 1.2)))
        # avoid too many draws? it's ok
        match.set_result(score_a, score_b)
        return match

    def apply_match_result_to_entities(self, match: Match, players_db: Dict[str, Player], teams_db: Dict[str, Team]):
        a = match.a
        b = match.b
        if a == "BYE" or b == "BYE":
            # winner already assigned as 1-0
            winner = a if match.score_a > match.score_b else b
            # update appropriate entity
            if winner in players_db:
                players_db[winner].record_result(match.score_a, match.score_b)
            elif winner in teams_db:
                teams_db[winner].record_result(match.score_a, match.score_b)
            return

        # if individual tournament, update players
        if self.kind == "individual":
            pa = players_db.get(a)
            pb = players_db.get(b)
            if not pa or not pb:
                # ignore or raise
                return
            pa.record_result(match.score_a, match.score_b)
            pb.record_result(match.score_b, match.score_a)
        else:
            ta = teams_db.get(a)
            tb = teams_db.get(b)
            if not ta or not tb:
                return
            ta.record_result(match.score_a, match.score_b)
            tb.record_result(match.score_b, match.score_a)

    # After finishing a knockout round, build next round matches if winners determined
    def advance_knockout_rounds(self):
        if self.type != "mata_mata":
            return
        # collect played matches grouped by round
        rounds = {}
        for m in self.matches:
            rounds.setdefault(m.round_number or 0, []).append(m)
        highest_round = max(rounds.keys())
        # find last round matches and if all played create next round pairs of winners
        last_round_matches = rounds.get(highest_round, [])
        if not last_round_matches:
            return
        if not all(m.played for m in last_round_matches):
            return
        # winners in order
        winners = []
        for m in last_round_matches:
            if m.score_a > m.score_b:
                winners.append(m.a)
            else:
                winners.append(m.b)
        if len(winners) <= 1:
            # tournament finished
            return
        # pad if odd with BYE
        if len(winners) % 2 == 1:
            winners.append("BYE")
        # create next round matches
        next_round = highest_round + 1
        for i in range(0, len(winners), 2):
            a = winners[i]
            b = winners[i+1]
            if a == "BYE" and b == "BYE":
                continue
            m = Match(id=str(uuid.uuid4()), a=a, b=b, round_number=next_round)
            self.matches.append(m)

    def standings(self, players_db: Dict[str, Player], teams_db: Dict[str, Team]) -> List[Tuple[str, int]]:
        """Gera ranking simples: para pontos corridos, 3/1/0; para individual->players else teams"""
        table = {}
        if self.kind == "individual":
            for pid in self.competitors:
                p = players_db.get(pid)
                if p:
                    pts = p.wins * 3 + p.draws * 1
                    table[pid] = pts
        else:
            for tid in self.competitors:
                t = teams_db.get(tid)
                if t:
                    pts = t.wins * 3 + t.draws * 1
                    table[tid] = pts
        # sort desc
        sorted_items = sorted(table.items(), key=lambda kv: (-kv[1], kv[0]))
        # convert ids to names
        result = []
        for id_, pts in sorted_items:
            name = players_db[id_].name if id_ in players_db else teams_db[id_].name if id_ in teams_db else id_
            result.append((name, pts))
        return result

# --------------------------
# Sistema/Serviços
# --------------------------

class TournamentSystem:
    def __init__(self, dao: PersistenceDAO):
        self.dao = dao
        self.players: Dict[str, Player] = self.dao.load_players()
        self.teams: Dict[str, Team] = self.dao.load_teams()
        # tournaments saved in memory; persistence via dao.save_tournament/load_tournament
        self.tournaments: Dict[str, Tournament] = {}

    # Player management
    def create_player(self, name: str, age: int, sport: str, player_type: str = "amador") -> Player:
        pid = str(uuid.uuid4())
        p = Player(id=pid, name=name, age=age, sport=sport, player_type=player_type)
        self.players[pid] = p
        return p

    def edit_player(self, pid: str, **kwargs) -> Player:
        p = self.players.get(pid)
        if not p:
            raise KeyError("Player não encontrado")
        for k, v in kwargs.items():
            if hasattr(p, k):
                setattr(p, k, v)
        return p

    def delete_player(self, pid: str):
        if pid in self.players:
            del self.players[pid]

    # Team management
    def create_team(self, name: str, member_ids: List[str]) -> Team:
        tid = str(uuid.uuid4())
        t = Team(id=tid, name=name, members=member_ids[:])
        self.teams[tid] = t
        return t

    def edit_team(self, tid: str, **kwargs) -> Team:
        t = self.teams.get(tid)
        if not t:
            raise KeyError("Team não encontrado")
        for k, v in kwargs.items():
            if hasattr(t, k):
                setattr(t, k, v)
        return t

    def add_member_to_team(self, tid: str, pid: str):
        t = self.teams.get(tid)
        if not t:
            raise KeyError("Team não encontrado")
        if pid not in t.members:
            t.members.append(pid)

    def remove_member_from_team(self, tid: str, pid: str):
        t = self.teams.get(tid)
        if not t:
            raise KeyError("Team não encontrado")
        if pid in t.members:
            t.members.remove(pid)

    # Persistence
    def save_all(self):
        self.dao.save_players(self.players)
        self.dao.save_teams(self.teams)

    def load_all(self):
        self.players = self.dao.load_players()
        self.teams = self.dao.load_teams()

    # Tournament related
    def create_tournament(self, name: str, competitors: List[str], kind: str = "individual", type_: str = "pontos_corridos") -> Tournament:
        t = Tournament(id=None, name=name, competitors=competitors, kind=kind)
        t.type = type_
        if type_ == "pontos_corridos":
            t.generate_round_robin()
        elif type_ == "mata_mata":
            t.generate_knockout()
        self.tournaments[t.id] = t
        return t

    def save_tournament(self, tournament_id: str, filename: str):
        t = self.tournaments.get(tournament_id)
        if not t:
            raise KeyError("Torneio não encontrado")
        data = t.to_dict()
        self.dao.save_tournament(data, filename)

    def load_tournament(self, filename: str) -> Tournament:
        data = self.dao.load_tournament(filename)
        t = Tournament(id=data["id"], name=data["name"], competitors=data["competitors"], kind=data.get("kind", "individual"))
        t.type = data.get("type", "pontos_corridos")
        # rebuild matches
        t.matches = []
        for md in data.get("matches", []):
            m = Match(**md)
            t.matches.append(m)
        self.tournaments[t.id] = t
        return t

    def register_result(self, tournament_id: str, match_id: str, score_a: int, score_b: int):
        t = self.tournaments.get(tournament_id)
        if not t:
            raise KeyError("Torneio não encontrado")
        t.register_result_manual(match_id, score_a, score_b)
        m = next((x for x in t.matches if x.id == match_id), None)
        if m and m.played:
            t.apply_match_result_to_entities(m, self.players, self.teams)
        if t.type == "mata_mata":
            t.advance_knockout_rounds()

    def simulate_unplayed_matches(self, tournament_id: str, random_seed: Optional[int] = None):
        t = self.tournaments.get(tournament_id)
        if not t:
            raise KeyError("Torneio não encontrado")
        rng = random.Random(random_seed)
        # add gaussian & poissonlike helpers to rng
        def poissonlike(mean):
            # simple Poisson-ish: sample from Poisson using Knuth algorithm for small means
            L = math.exp(-mean)
            k = 0
            p = 1.0
            while p > L:
                k += 1
                p *= rng.random()
            return k - 1
        # monkey patch
        setattr(rng, "poissonlike", poissonlike)
        for m in [x for x in t.matches if not x.played]:
            t.simulate_match(m, self.players, self.teams, rng=rng)
            t.apply_match_result_to_entities(m, self.players, self.teams)
        if t.type == "mata_mata":
            # loop to advance rounds until finished
            while True:
                before = len([x for x in t.matches if not x.played])
                t.advance_knockout_rounds()
                # simulate newly added matches
                new_unplayed = [x for x in t.matches if not x.played]
                if not new_unplayed:
                    break
                for m in new_unplayed:
                    t.simulate_match(m, self.players, self.teams, rng=rng)
                    t.apply_match_result_to_entities(m, self.players, self.teams)
                after = len([x for x in t.matches if not x.played])
                if after == before:
                    break

    def get_ranking(self, tournament_id: str) -> List[Tuple[str, int]]:
        t = self.tournaments.get(tournament_id)
        if not t:
            raise KeyError("Torneio não encontrado")
        return t.standings(self.players, self.teams)

    def export_ranking(self, tournament_id: str, filename: str):
        ranking = self.get_ranking(tournament_id)
        self.dao.export_ranking(ranking, filename)

# --------------------------
# Utilitários e demo simples
# --------------------------

def simple_demo():
    print("Inicializando sistema com DAO JSON...")
    dao = JsonFileDAO()
    system = TournamentSystem(dao)

    # criar alguns jogadores
    p1 = system.create_player("Ana", 22, "Futebol", "profissional")
    p2 = system.create_player("Bruno", 24, "Futebol", "amador")
    p3 = system.create_player("Carlos", 20, "Futebol", "amador")
    p4 = system.create_player("Daniela", 23, "Futebol", "profissional")
    # ajustar rating para simulação
    system.players[p1.id].rating = 1200
    system.players[p4.id].rating = 1150
    system.players[p2.id].rating = 980
    system.players[p3.id].rating = 900

    print("Jogadores criados:", [p.name for p in system.players.values()])

    # criar equipe
    team = system.create_team("Tropa FC", [p1.id, p2.id])
    print("Time criado:", team.name, "membros:", team.members)

    # criar torneio individual (pontos corridos)
    t = system.create_tournament("Copa Amostra", competitors=list(system.players.keys()), kind="individual", type_="pontos_corridos")
    print("Torneio criado:", t.name, "| tipo:", t.type, "| partidas:", len(t.matches))

    # simular todas as partidas
    system.simulate_unplayed_matches(t.id, random_seed=42)
    print("Simulação concluída. Rankings:")
    ranking = system.get_ranking(t.id)
    for pos, (name, pts) in enumerate(ranking, start=1):
        print(f"{pos}. {name} - {pts} pontos")

    # salvar dados
    system.save_all()
    system.save_tournament(t.id, "cup_demo.json")
    system.export_ranking(t.id, "cup_demo_ranking.txt")
    print("Dados salvos em pasta data_json/")

# The following provides a very small textual menu to interact minimally.
def run_repl():
    dao = JsonFileDAO()
    sys = TournamentSystem(dao)
    print("Sistema de Torneios (simples). Dados em data_json/ .")
    while True:
        print("\nEscolha (1) Criar jogador  (2) Criar time  (3) Criar torneio  (4) Listar jogadores  (5) Simular torneio  (6) Ver ranking  (7) Salvar/Carregar  (0) Sair")
        opt = input("opção: ").strip()
        if opt == "1":
            name = input("Nome: ")
            age = int(input("Idade: "))
            sport = input("Esporte: ")
            ptype = input("Tipo (amador/profissional) [amador]: ") or "amador"
            p = sys.create_player(name, age, sport, ptype)
            print("Criado:", p.id, p.name)
        elif opt == "2":
            name = input("Nome do time: ")
            mems = input("IDs de membros separados por vírgula (deixe vazio para adicionar depois): ")
            member_ids = [m.strip() for m in mems.split(",")] if mems.strip() else []
            t = sys.create_team(name, member_ids)
            print("Time criado:", t.id, t.name)
        elif opt == "3":
            name = input("Nome do torneio: ")
            mode = input("Tipo (pontos_corridos/mata_mata) [pontos_corridos]: ") or "pontos_corridos"
            kind = input("Competidores (individual/team) [individual]: ") or "individual"
            if kind == "individual":
                comps = input("IDs dos jogadores separados por vírgula (vazio = todos): ").strip()
                if not comps:
                    competitors = list(sys.players.keys())
                else:
                    competitors = [c.strip() for c in comps.split(",")]
            else:
                comps = input("IDs dos times separados por vírgula (vazio = todos): ").strip()
                if not comps:
                    competitors = list(sys.teams.keys())
                else:
                    competitors = [c.strip() for c in comps.split(",")]
            t = sys.create_tournament(name, competitors, kind=kind, type_=mode)
            print("Torneio criado:", t.id, "| partidas:", len(t.matches))
        elif opt == "4":
            for pid, p in sys.players.items():
                print(pid, "-", p.name, "|", p.player_type, "| matches:", p.matches_played, "W/D/L:", p.wins, p.draws, p.losses)
        elif opt == "5":
            tid = input("ID do torneio: ").strip()
            try:
                sys.simulate_unplayed_matches(tid)
                print("Simulação concluída.")
            except Exception as e:
                print("Erro:", e)
        elif opt == "6":
            tid = input("ID do torneio: ").strip()
            try:
                ranking = sys.get_ranking(tid)
                for i, (name, pts) in enumerate(ranking, start=1):
                    print(f"{i}. {name} - {pts}")
            except Exception as e:
                print("Erro:", e)
        elif opt == "7":
            sys.save_all()
            print("Players e Teams salvos.")
            # lista torneios em memória
            for tid, t in sys.tournaments.items():
                fname = f"tournament_{t.name.replace(' ', '_')}_{tid[:6]}.json"
                sys.save_tournament(tid, fname)
                print("Salvo torneio:", t.name, "->", fname)
            print("Export ranking example for first tournament (if any).")
            if sys.tournaments:
                any_tid = next(iter(sys.tournaments))
                sys.export_ranking(any_tid, "export_ranking.txt")
                print("Ranking exportado para data_json/export_ranking.txt")
        elif opt == "0":
            print("Saindo.")
            break
        else:
            print("Opção inválida.")

# --------------------------
# Entrypoint
# --------------------------
if __name__ == "__main__":
    print("Executando demo. Para usar a interface interativa, rode run_repl()")
    simple_demo()
    # Uncomment the next line to run REPL instead of demo:
    # run_repl()
