"""sql_game_factory.py -- factory for games."""
from .exceptions import GolfException
from .game_gross import GameGross
from .game_net import GameNet
#from .sql_game_skins import SqlGameSkins
from .game_putts import GamePutts
#from .sql_game_stableford import SqlGameStableford
#from .sql_game_greenie import SqlGameGreenie
#from .sql_game_snake import SqlGameSnake
#from .sql_game_best_ball import SqlGameBestBall
#from .sql_game_six_point import SqlGameSixPoint
#from .sql_game_eighty_one import SqlGameEightyOne
#from .sql_game_match import SqlGameMatch
#from .sql_game_rewards import SqlGameRewards

dctGames = { 
  'gross': GameGross,
  'net': GameNet,
  #'skins': SqlGameSkins,
  'putts': GamePutts,
  #'stableford': SqlGameStableford,
  #'greenie': SqlGameGreenie,
  #'snake': SqlGameSnake,
  #'bestball': SqlGameBestBall,
  #'six_point': SqlGameSixPoint,
  #'eighty_one': SqlGameEightyOne,
  #'match': SqlGameMatch,
  #'rewards': SqlGameRewards,
}

def GolfGameFactory(game):
  """Return the SQL game class.
  
  Args:
    game: name of game.
  Returns:
    game class
  Raises:
    GolfException - bad game name.
  """
  if game in dctGames:
    return dctGames[game]
  raise GolfException('Game "{}" not supported'.format(game))

def GolfGameOptions(game):
  """Return the SQL game options.
  
  Args:
    game: name of game.
  Returns:
    dictionary of game options.
  Raises:
    GolfException - bad game name.
  """
  if game in dctGames:
    return dctGames[game].game_options
  raise GolfException('Game "{}" not supported'.format(game))

def GolfGameList():
  """Return list of available games."""
  lst = dctGames.keys()
  return sorted(lst) 
  
