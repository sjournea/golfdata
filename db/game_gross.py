""" game_gross.py - GolfGame class."""
from .game import GolfGame, GamePlayer

class GrossPlayer(GamePlayer):
  def __init__(self, game, result):
    super().__init__(game, result)
    self.dct_gross = self._init_dict()
    self.esc = 0
  
class GameGross(GolfGame):
  """Basic gross game. Man's golf."""
  short_description = 'Gross'
  description = """
Basic golf game, the players simply add up their scores and compare. You score 97. I score 96. I win.
"""
  def setup(self, **kwargs):
    """Start the game."""
    player_class = kwargs.get('player_class', GrossPlayer)
    self._players = [player_class(self, result) for result in self.golf_round.results]
    # add header to scorecard
    self.dctScorecard['course'] = self.golf_round.course.getScorecard(ESC=1)
    self.dctScorecard['header'] = '{0:*^98}'.format(' Gross ')
    self.dctLeaderboard['hdr'] = 'Pos Name   Gross Thru'
  
  def update(self):
    """Update gross results for all scores so far."""
    for pl, result in zip(self._players, self.golf_round.doc.results):
      pl.esc = 0
      for score in result.scores:
        # update gross
        n = score.num-1
        pl.dct_gross['holes'][n] = score.gross
        pl.esc += self.golf_round.course.calcESC(n, score.gross, result.course_handicap)
      pl.update_totals(pl.dct_gross)
    
  def getScorecard(self, **kwargs):
    """Scorecard with all players."""
    lstPlayers = []
    for n,score in enumerate(self._players):
      dct = {'player': score.result.player }
      dct['in'] = score.dct_gross['in']
      dct['out'] = score.dct_gross['out']
      dct['total'] = score.dct_gross['total']
      dct['esc'] = score.esc
      dct['holes'] = score.dct_gross['holes']
      # build line for stdout
      line = '{:<6}'.format(score.player.nick_name)
      for gross in score.dct_gross['holes'][:9]:
        line += ' {:>3}'.format(gross) if gross is not None else '    '
      line += ' {:>4}'.format(dct['out'])
      for gross in score.dct_gross['holes'][9:]:
        line += ' {:>3}'.format(gross) if gross is not None else '    '
      line += ' {:>4} {:>4} {:>4}'.format(dct['in'], dct['total'], score.esc)
      dct['line'] = line
      lstPlayers.append(dct)
    self.dctScorecard['players'] = lstPlayers
    return self.dctScorecard

  def getLeaderboard(self, **kwargs):
    """Scorecard with all players."""
    board = []
    scores = sorted(self._players, key=lambda score: score.dct_gross['total'])
    pos = 1
    prev_total = None
    for score in scores:
      score_dct = {
        'player': score.player,
        'total' : score.dct_gross['total'],
      }
      if prev_total != None and score_dct['total'] > prev_total:
        pos += 1
      prev_total = score_dct['total']
      score_dct['pos'] = pos
      for n,gross in enumerate(score.dct_gross['holes']):
        if gross is None:
          break
      else:
        n += 1
      score_dct['thru'] = n
      score_dct['line'] = '{:<3} {:<6} {:>5} {:>4}'.format(
        score_dct['pos'], score_dct['player'].nick_name, score_dct['total'], score_dct['thru'])
      board.append(score_dct)
    self.dctLeaderboard['leaderboard'] = board
    return self.dctLeaderboard

  def getStatus(self, **kwargs):
    """Scorecard with all players."""
    for n,gross in enumerate(self._players[0].dct_gross['holes']):
      if gross is None:
        self.dctStatus['next_hole'] = n+1
        self.dctStatus['par'] = self.golf_round.course.holes[n].par
        self.dctStatus['handicap'] = self.golf_round.course.holes[n].handicap
        self.dctStatus['line'] = 'Hole {} Par {} Hdcp {}'.format(
          self.dctStatus['next_hole'], self.dctStatus['par'], self.dctStatus['handicap'])
        break
    else:
      # round complete
      self.dctStatus['next_hole'] = None
      self.dctStatus['par'] = self.golf_round.course.total
      self.dctStatus['handicap'] = None
      self.dctStatus['line'] = 'Round complete'
    return self.dctStatus

