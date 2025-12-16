from player import *
from engine import GameEngine
from logger import Logger
from datetime import datetime
import os

def competition(P1: Player, P2: Player, P3: Player, P4: Player, game_count: int, fdpu=False, directory=None, logs=True):
    print(f"Playing {game_count} games...", end="")
    game_nbr = 1
    points = {0: 0, 1: 0}
    wins = {0: 0, 1: 0}
    for _ in range(game_count):
        logger = Logger(filename=f"game{game_nbr}-{datetime.now().strftime('%m-%d-%y-%I:%M%p')}.txt", directory=directory)
        players = [
            P1(1, 3, team=0),
            P2(2, 4, team=1),
            P3(3, 1, team=0),
            P4(4, 2, team=1)
        ]
        engine = GameEngine(players, fdpu, logger)
        engine.play_game()
        for team, score in engine.scores.items():
            if score >= 10: wins[team] += 1
            points[team] += score
        if logs: logger.save()
        game_nbr += 1
    print(f" done!")

    print(f"Team 0 Wins: {wins[0]}")
    print(f"Team 0 Avg Points: {round(points[0] / game_count, 3)}")
    print(f"Team 1 Wins: {wins[1]}")
    print(f"Team 1 Avg Points: {round(points[1] / game_count, 3)}")

    if directory:
        os.makedirs(directory, exist_ok=True)
        filepath = os.path.join(directory, "00summary.txt")

    with open(filepath, "w") as f:
        f.write(f"Team 0 Wins: {wins[0]}\n")
        f.write(f"Team 0 Avg Points: {round(points[0] / game_count, 3)}\n")
        f.write(f"Team 1 Wins: {wins[1]}\n")
        f.write(f"Team 1 Avg Points: {round(points[1] / game_count, 3)}\n")
    
    
if __name__ == "__main__":
    competition(HighValue, HighWithCaution, LowValue, HighValue, 31, fdpu=False, directory="Logs/Test1", logs=False)