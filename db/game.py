""" game.py - GolfGame class."""
from .exceptions import GolfException
from .doc import Doc
from util.tl_logger import TLLog

log = TLLog.getLogger('game')

class GolfGame(Doc):
  """Class for all golf games."""
  description = '<Description not set>'
  short_description = '<Not set>'

  # define game options:
  #    '<attribute>': {
  #      'default': <default>,           Default value
  #      'type': <data type>,            'int', 'float', 'string', 'choice'
  #      'desc': '<option description>',  
  #      'choices': (choice1, choice2,...),   for type 'choice'
  #    },
  game_options = {}

  def __init__(self, doc, golf_round):
    super().__init__(doc)
    self.golf_round = golf_round
    self.dctScorecard = {}
    self.dctLeaderboard = {}
    self.dctStatus = {}
    # set game options
    self.load_game_options()
    # setup and validate
    self.print_options()
    self.setup(**doc.options)
    self.validate()

  def validate(self):
    """Overload to validate a game setup."""
    pass

  def load_game_options(self, **kwargs):
    """setup game options from game_options dictionary."""
    def set_value(dct, value):
      if dct['type'] == 'int':
        dct['value'] = int(value)
      elif dct['type'] == 'bool':
        dct['value'] = bool(value)
      elif dct['type'] == 'float':
        dct['value'] = float(value)
      elif dct['type'] == 'string':
        dct['value'] = str(value)
      elif dct['type'] == 'choice':
        value = str(value)
        # find matching choice
        lst = [n for n,choice in enumerate(dct['choices']) if value in choice]
        if not lst:
          raise GolfException('No matching choice with {} in {}'.format(value, dct['choices']))
        if len(lst) > 1:
          raise GolfException('Multiple matches with choice {} in {}'.format(value, dct['choices']))
        value = lst[0]
        dct['value'] = dct['choices'][value]
      elif dct['type'] == 'tuple[2][2]':
        # tuple : ([int,int], [int,int])
        #print('{} isinstance:{} value:"{}"'.format(dct['type'], type(value), value))
        dct['value'] = ast.literal_eval(value)
      elif dct['type'] == 'tuple[2]':
        # tuple[2] : (int,int)
        #print('{} isinstance:{} value:"{}"'.format(dct['type'], type(value), value))
        dct['value'] = ast.literal_eval(value)
      else:
        raise GolfException('option type "{}" not supported'.format(dct['type']))
    # start here
    #print('kwargs:{}'.format(kwargs))
    for key, dct in self.game_options.items():
      set_value(dct, kwargs.get(key, dct['default']))
      setattr(self, key, dct['value'])

  def print_options(self):
    print('{} - {} options'.format(self.__class__.__name__, len(self.game_options)))
    for key in self.game_options.keys():
      print('  {:<20} : {}'.format(key, getattr(self, key)))

  def setup(self, **kwargs):
    """Overload to add custom initialization from __init__()."""
    pass

  def update(self):
    """Overload to update the game."""
    pass

  def getScorecard(self, **kwargs):
    """Return scorecard dictionary for this game."""
    return self.dctScorecard

  def getLeaderboard(self, **kwargs):
    """Return leaderboard for this game.

    Returns:
      list of dictionaries sorted in the order of 1st to last.
    """
    return self.dctLeaderboard

  def getStatus(self, **kwargs):
    """Return simple status for state of game."""
    return self.dctStatus

  def __str__(self):
    return '{} options:{} leaderboard:{} scorecard:{} status:{}'.format(
      self.__class__.__name__, self.options, self.leaderboard, self.scorecard, self.status)

class GamePlayer(Doc):
  # TODO: Should inherit from DPlayer
  def __init__(self, game, result):
    super().__init__(result.player)
    self.game = game
    self.result = result

  def getFullName(self):
    return '{} {}'.format(self.first_name, self.last_name)

  def getInitials(self):
    return self.first_name[0] + self.last_name[0]
  
  dct_plural_gender = {'man': 'mens', 'woman': 'womens'}
  @property
  def genderPlural(self):
    return self.dct_plural_gender[self.gender]
  
  def _init_dict(self, score_type=int):
    """Create and initialize scoring dictionary.

      add holes, in, out, total.
    """
    return {
      'holes': [None for _ in range(len(self.game.golf_round.course.holes))],
      'in' : score_type(0),
      'out': score_type(0),
      'total': score_type(0),
    }

  def update_totals(self, dct):
    """Update totals in a dictionary. If a value is None it is not added.

       dct must contain the following keys:
         holes: list of number scores
         in: total for holes 10..18
         out: total for holes 1..9
         total: in + out + overall (if set).
    """
    dct['out'] = sum([sc for sc in dct['holes'][:9] if sc is not None])
    dct['in']  = sum([sc for sc in dct['holes'][9:] if sc is not None])
    dct['total'] = dct['in'] + dct['out'] + dct.get('overall', 0)

  def calc_bumps(self, min_handicap):
    return self.game.golf_round.course.calcBumps(self.result.course_handicap - min_handicap)


class GolfTeam(object):
  """Base class for all golf teams."""
  def __init__(self, game, players, **kwargs):
    self.game = game
    self.name = kwargs.get('name')
    self.players = players[:]
    if not self.name:
      self.name = '/'.join([pl.player.getInitials() for pl in self.players])

  def setup(self, min_handicap=None):
    pass

  def calculate_score(self, index):
    pass

  def update_points(self, index, other_team):
    pass
