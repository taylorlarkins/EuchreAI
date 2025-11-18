# main.py
from player import *
from engine import GameEngine
from logger import Logger

if __name__ == "__main__":
    logger = Logger()
    players = [
        PlayBestCard("P1", team=0),
        Player("P2", team=1),
        PlayBestCard("P3", team=0),
        Player("P4", team=1)
    ]
    engine = GameEngine(players, logger)
    engine.play_game()
    logger.save()
    print("Game complete! Logs saved.")
