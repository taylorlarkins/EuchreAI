# main.py
from player import RandomAgent
from engine import GameEngine
from logger import Logger

if __name__ == "__main__":
    logger = Logger()
    players = [
        RandomAgent("P1", team=0),
        RandomAgent("P2", team=1),
        RandomAgent("P3", team=0),
        RandomAgent("P4", team=1)
    ]
    engine = GameEngine(players, logger)
    engine.play_game()
    logger.save()
    print("Game complete! Logs saved.")
