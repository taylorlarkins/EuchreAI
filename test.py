from player import *
p = TeamPlayer(1, 3, team=0)
p.hand = [Card("Hearts", "9"), Card("Spades", "K"), Card("Hearts", "10"), Card("Clubs", "A"), Card("Diamonds", "J")]
p.reset()
p.pretty_print_chance_chart()
