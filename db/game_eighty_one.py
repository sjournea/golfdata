""" sql_game_eighty_one.py - GolfGame class."""
from .game_six_point import GameSixPoint


class GameEightyOne(GameSixPoint):
  """Eighty one golf game."""
  short_description = '81'
  description = """
Eighty One is similar to the Six Point Game, except that each hole is worth nine points (nine points times nine holes equals 81).
The results are higher scores and higher pay-outs. The points break down as follows:
The winner on the hole wins 5 points, the golfer who finishes second receives 3 points, and the last place golfer receives 1 point (5-3-1).
The winner on the hole wins 5 points, while the other two golfers who tie for second each receive 2 points (5-2-2).
The two golfers who tie for lowest score win 4 points each, while the golfer with the highest score receives 1 point (4-4-1).
The three golfers who tie on the hole each receive 3 points (3-3-3)."""
  POINTS_WIN_1ST = 5
  POINTS_TIE_1ST = 4
  POINTS_WIN_2ND = 3
  POINTS_TIE_2ND = 2
  POINTS_ALL_TIE = 3
  POINTS_3RD     = 1
  TITLE = 'Eighty One'
  NAME = 'eighty_one'
