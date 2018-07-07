""" game_match.py - GolfGame class."""
from .game_net import GameNet, NetPlayer
from .exceptions import GolfException

class MatchPlayer(NetPlayer):
  def __init__(self, game, result, min_handicap):
    super().__init__(game, result, min_handicap)
    self.dct_score = self._init_dict()
    self.dct_score['total'] = 0
    self.status = 'All Square'
    self.win = None

  @property
  def total(self):
    return self.dct_score['total']
  
  def update_score(self, index, score):
    self.dct_score['total'] += score
    self.dct_score['holes'][index] = self.dct_score['total']
    if index == 8:
      self.dct_score['out'] = self.dct_score['total']
    elif index == 17:
      self.dct_score['in'] = self.dct_score['total']

  def update_status(self, to_play):
    if self.total == 0:
      self.status = 'All Square' if to_play > 0 else 'Draw'
    if self.total > 0:
      # In the lead
      self.status = '{} Up'.format(self.total)
      if self.total > to_play:
        self.win = True
        if to_play > 0:
          self.status = '{} & {}'.format(self.total, to_play)
          self.dct_score['holes'][-to_play:] = to_play*[None]
    if self.total < 0:
      # losing
      self.status = '{} Down'.format(abs(self.total))
      if self.total + to_play > 0:
        self.win = False
        self.status = ''
        if to_play > 0:
          self.dct_score['holes'][-to_play:] = to_play*[None]
    if self.win is None and to_play > 0 and to_play < 5:
      self.status += ' {} to play'.format(to_play)
    return self.win

class GameMatch(GameNet):
  """Match golf game."""
  short_description = 'Match'
  description = """
Match play is a hole-by-hole game where the lowest score wins the hole.
If I shoot a five, and you shoot an eight, then in medal play I should gain three strokes.
However, in match play I only win one point (no matter how many strokes better I played the hole).
If the players tie the hole, it is 'halved' (no one wins a point).
Once we are finished the golfer with the most points wins.

Handicaps are used in match play.
"""
  def validate(self):
    if len(self._players) != 2:
      raise GolfException('Match game must have 2 players, {} found.'.format(len(self._players)))

  @property
  def final(self):
    return bool(self.winner or self.to_play == 0)

  def setup(self, **kwargs):
    """Start the match game."""
    kwargs['player_class'] = MatchPlayer
    super().setup(**kwargs)
    self.winner = None
    self.to_play = len(self.golf_round.course.holes)
    self.thru = 0
    self.dctScorecard['header'] = '{0:*^98}'.format(' Match ')

  def update(self):
    """Start the match game."""
    super().update()
    self.thru = self.golf_round.get_completed_holes()
    self.to_play = len(self.golf_round.course.holes) - self.thru
    for index in range(self.thru):
      players = sorted(self._players, key=lambda pl:pl.dct_net['holes'][index])
      if players[0].dct_net['holes'][index] < players[1].dct_net['holes'][index]:
        # we have a winner
        players[0].update_score(index, 1)
        players[1].update_score(index, -1)
      else:
        # a tie
        players[0].update_score(index, 0)
        players[1].update_score(index, 0)
    for pl in self._players:
      if pl.update_status(self.to_play):
        self.winner = pl
      
  def getScorecard(self, **kwargs):
    """Scorecard with all players."""
    lstPlayers = []
    for n,sc in enumerate(self._players):
      dct = {'player': sc.doc }
      dct['in'] = sc.dct_score['in']
      dct['out'] = sc.dct_score['out']
      dct['total'] = sc.total
      dct['holes'] = sc.dct_score['holes']
      line = '{:<6}'.format(sc.nick_name)
      for x,bump in zip(sc.dct_score['holes'][:9], sc._bumps[:9]):
        xs = '{:d}'.format(x) if x is not None else ''
        xs = '{}{}'.format('*' if bump > 0 else '',xs)
        line += ' {:>3}'.format(xs)
      line += ' {:>4d}'.format(dct['out'])
      for x,bump in zip(sc.dct_score['holes'][9:], sc._bumps[9:]):
        xs = '{:d}'.format(x) if x is not None else ''
        xs = '{}{}'.format('*' if bump > 0 else '',xs)
        line += ' {:>3}'.format(xs)
      line += ' {:>4d} {:>4d}'.format(dct['in'], dct['total'])
      dct['line'] = line
      lstPlayers.append(dct)
    self.dctScorecard['players'] = lstPlayers
    return self.dctScorecard
  
  def getLeaderboard(self, **kwargs):
    self.dctLeaderboard['thru'] = self.thru
    self.dctLeaderboard['to_play'] = self.to_play
    self.dctLeaderboard['final'] = self.final
    board = []
    for n,pl in enumerate(self._players):
      line = '{:<10}'.format(pl.nick_name)
      if pl.total > 0 or (pl.total == 0 and n == 0):
        line += pl.status
      dct = {
        'player': pl.doc,
        'line': line,
        'status': pl.status,
      }
      board.append(dct)
    self.dctLeaderboard['leaderboard'] = board
    self.dctLeaderboard['hdr'] = '{:<10}{}'.format('Match', 'Final' if self.final else 'Thru {}'.format(self.thru))
    return self.dctLeaderboard

  def getStatus(self, **kwargs):
    n = self.golf_round.get_completed_holes()
    if n < len(self.golf_round.course.holes):
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
        self.dctStatus['line'] += ' Bumps: {}'.format(','.join(bump_line))
    else:
      # round complete
      self.dctStatus['next_hole'] = None
      self.dctStatus['par'] = self.golf_round.course.total
      self.dctStatus['handicap'] = None
      self.dctStatus['line'] = 'Round Complete'
    return self.dctStatus
