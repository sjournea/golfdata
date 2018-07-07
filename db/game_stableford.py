""" game_stableford.py - Stableford Golf Game class."""
import ast
from .game import GolfGame,GamePlayer
from .exceptions import GolfException

class StablefordPlayer(GamePlayer):
  def __init__(self, game, result):
    super().__init__(game, result)
    self._bumps = self.calc_bumps(0)
    self.dct_points = self._init_dict()
    self._jokers = game.jokers[n] if game.stableford_type == 'Spanish' else None

class GameStableford(GolfGame):
  """The Stableford game."""
  short_description = 'Stableford'
  description = """
Stableford isn't played very often anymore (like knickers, some feel it should remain in the nineteenth century), but 
in a sport where people trek across the Atlantic to see 'the old course,' a game of Stableford may bring a bit of classic 
excitement to your round. In Stableford, you play against everyone else in your foursome (or if you have multiple 
foursomes, everyone else who is playing that day). The game is based on a point system, where the points you earn 
are determined by your score on the hole. Every point is worth a set monetary amount (some people play 10 cents, 
some people play ten dollars) that is decided in advance of the game. How many points is a hole worth? 
Over time, variations on the game have arisen, and so we list three below: 

Stableford Variants:

                 Modified  Classic  British	Spanish
Double Eagle	    8         8        -	
Eagle	 	    5         5        4 	Same as
Birdie	 	    2         2        3 	British Stableford
Par	 	    1         1        2 	but with Joker
Bogey	 	   -1        -1        1        holes (points on
Double Bogey	   -3        -2        -	hole are doubled)*

*Before you tee off, each golfer declares two joker holes - one on the front nine and one on the back nine.

Since most people have a hard time shooting double eagles and eagles, golfers often play Stableford
(especially classic Stableford) using their full handicaps."""

  dct_scoring = {
    'Modified': { -3: 8, -2: 5, -1: 2, 0: 1, 1: -1, 2:-3, 'min':8, 'max': -3},
    'Classic':  { -3: 8, -2: 5, -1: 2, 0: 0, 1: -1, 2:-2, 'min':8, 'max': -2},
    'British':  { -3: 4, -2: 4, -1: 3, 0: 2, 1:  1, 2: 0, 'min':4, 'max': 0 },
    'Spanish':  { -3: 4, -2: 4, -1: 3, 0: 2, 1:  1, 2: 0, 'min':4, 'max': 0 },
  }

  #    '<attribute>': {'default': <default>, 'type': <data type>, 'desc': 'Option description>'},
  game_options = {
    'stableford_type':  { 'default': 'British', 'type': 'choice',  'choices': ('Modified', 'Classic', 'British', 'Spanish'), 'desc': 'Modified, Classic, British or Spanish' },
    'jokers':           { 'default': '(9,18)',    'type': 'tuple[2]',   'desc': 'Set joker holes for each player. One in front 9 and one in back 9'},    
    'wager':            { 'default': 0.0,       'type': 'float', 'desc': 'Wager per point.'},    
  }

  def validate(self):
    super().validate()
    if self.stableford_type not in self.dct_scoring:
      raise GolfException('stableford_type {} not supported.'.format(self.stableford_type))
    if self.stableford_type == 'Spanish':
      if not self.jokers:
        raise GolfException('stableford_type Spanish needs jokers set.')
      if len(self.jokers) != len(self.scores):
        raise GolfException('stableford_type Spanish needs a joker set for each player.')
      for joker in self.jokers:
        if len(joker) != 2:
          raise GolfException('stableford_type Spanish jokers must have 2 values.')
        if joker[0] not in (1,2,3,4,5,6,7,8,9):
          raise GolfException('stableford_type Spanish joker[0] must be in 1-9.')
        if joker[1] not in (10,11,12,13,14,15,16,17,18):
          raise GolfException('stableford_type Spanish joker[1] must be in 10-18.')

  def setup(self, **kwargs):
    self.dct_stableford = self.dct_scoring[self.stableford_type]
    # use full handicap for all players
    self._players = [StablefordPlayer(self, result) for result in self.golf_round.results]
    self.dctScorecard['header'] = '{0:*^98}'.format(' Stableford ')
    self._thru = 0

  def update(self):
    """Update gross results for all scores so far."""
    for pl, result in zip(self._players, self.golf_round.doc.results):
      # calculate net
      for n, score in enumerate(result.scores):
        net_score = score.gross - pl._bumps[n] 
        pl.dct_points['holes'][n] = self._calc_score(net_score - self.golf_round.course.holes[n].par)
        if pl._jokers:
          if (n+1) in pl._jokers:
            pl.dct_points['holes'][n] *= 2
        pl.update_totals(pl.dct_points)

  def _calc_score(self, net_score):
    if net_score in self.dct_stableford:
      return self.dct_stableford[net_score]
    if net_score < 0:
      return self.dct_stableford['min']
    else:
      return self.dct_stableford['max']

  def getScorecard(self, **kwargs):
    """Scorecard with all players."""
    lstPlayers = []
    for n,sc in enumerate(self._players):
      dct = {'player': sc.doc }
      dct['in'] = sc.dct_points['in']
      dct['out'] = sc.dct_points['out']
      dct['total'] = sc.dct_points['total']
      dct['holes'] = sc.dct_points['holes']
      dct['bumps'] = sc._bumps
      line = '{:<6}'.format(sc.nick_name)
      for i,(point,bump) in enumerate(zip(sc.dct_points['holes'][:9], sc._bumps[:9])):
        s = '{}'.format(bump*'*')
        s += '' if point is None else '{:d}'.format(point)
        s += 'j' if sc._jokers and (i+1) in sc._jokers else ''
        line += ' {:>3}'.format(s)
      line += ' {:>4d}'.format(dct['out'])
      for i,(point,bump) in enumerate(zip(sc.dct_points['holes'][9:], sc._bumps[9:])):
        s = '{}'.format(bump*'*')
        s += '' if point is None else '{:d}'.format(point)
        s += 'j' if sc._jokers and (i+1) in sc._jokers else ''
        line += ' {:>3}'.format(s)
      line += ' {:>4d} {:>4d}'.format(dct['in'], dct['total'])
      dct['line'] = line
      lstPlayers.append(dct)
    self.dctScorecard['players'] = lstPlayers
    return self.dctScorecard

  def getLeaderboard(self, **kwargs):
    board = []
    sort_type = kwargs.get('sort_type', 'points')
    if sort_type == 'money' and self.wager:
      self.dctLeaderboard['hdr'] = 'Pos Name  Money  Thru'
      scores = sorted(self.scores, key=lambda score: score.dct_money['total'], reverse=True)
      sort_by = 'money'
    else:
      self.dctLeaderboard['hdr'] = 'Pos Name  Points  Thru'
      scores = sorted(self._players, key=lambda score: score.dct_points['total'], reverse=True)
      sort_by = 'total'
    pos = 1
    prev_total = None
    for sc in scores:
      score_dct = {
        'player': sc.doc,
        'total' : sc.dct_points['total'],
      }
      if prev_total != None and score_dct[sort_by] != prev_total:
        pos += 1
      prev_total = score_dct[sort_by]
      score_dct['pos'] = pos

      for n,point in enumerate(sc.dct_points['holes']):
        if point is None:
          break
      else:
        n += 1
      score_dct['thru'] = n
      if sort_by == 'money':
        money = '---' if score_dct['money'] == 0.0 else '${:2g}'.format(score_dct['money'])
        score_dct['line'] = '{:<3} {:<6} {:>5} {:>4}'.format(
          score_dct['pos'], score_dct['player'].nick_name, money, score_dct['thru'])
      else:
        score_dct['line'] = '{:<3} {:<6} {:>5} {:>4}'.format(
          score_dct['pos'], score_dct['player'].nick_name, score_dct['total'], score_dct['thru'])
      board.append(score_dct)
    self.dctLeaderboard['leaderboard'] = board
    return self.dctLeaderboard

  def getStatus(self, **kwargs):
    for n,points in enumerate(self._players[0].dct_points['holes']):
      if points is None:
        self.dctStatus['next_hole'] = n+1
        self.dctStatus['par'] = self.golf_round.course.holes[n].par
        self.dctStatus['handicap'] = self.golf_round.course.holes[n].handicap
        bumps = []
        bump_line = []
        for sc in self._players:
          if sc._bumps[n] > 0:
            dct = {'player': sc.doc, 'bumps': sc._bumps[n]}
            bumps.append(dct)
            bump_line.append('{}{}'.format(sc.nick_name, '({})'.format(dct['bumps']) if dct['bumps'] > 1 else ''))
        self.dctStatus['bumps'] = bumps
        self.dctStatus['line'] = 'Hole {} Par {} Hdcp {}'.format(
          self.dctStatus['next_hole'], self.dctStatus['par'], self.dctStatus['handicap'])
        if bumps:
          self.dctStatus['line'] += ' Bumps:{}'.format(','.join(bump_line))
        break
    else:
      # round complete
      self.dctStatus['next_hole'] = None
      self.dctStatus['par'] = self.golf_round.course.total
      self.dctStatus['handicap'] = None
      self.dctStatus['line'] = 'Round Complete'
    return self.dctStatus
