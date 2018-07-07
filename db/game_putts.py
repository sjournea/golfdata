""" game_gross.py - GolfGame class."""
from .game import GolfGame, GamePlayer


class PuttsPlayer(GamePlayer):
  def __init__(self, game, result):
    super().__init__(game, result)
    self.dct_putts = self._init_dict()

  
class GamePutts(GolfGame):
  """Putts game."""
  short_description = 'Putts'
  description = """
Who has the fewest putts in the round. Must be on the green to be a putt.
"""
  def setup(self, **kwargs):
    """Start the game."""
    self._players = [PuttsPlayer(self, result) for result in self.golf_round.results]
    # add header to scorecard
    self.dctScorecard['course'] = self.golf_round.course.getScorecard()
    self.dctScorecard['header'] = '{0:*^98}'.format(' Putts ')
    self.dctLeaderboard['hdr'] = 'Pos Name   Putts Thru'
  
  def update(self):
    """Update gross results for all scores so far."""
    for pl, result in zip(self._players, self.golf_round.doc.results):
      for score in result.scores:
        # update gross
        n = score.num-1
        pl.dct_putts['holes'][n] = score.putts
      pl.update_totals(pl.dct_putts)
    
  def getScorecard(self, **kwargs):
    """Scorecard with all players."""
    lstPlayers = []
    for n,score in enumerate(self._players):
      dct = {'player': score.doc }
      dct['in'] = score.dct_putts['in']
      dct['out'] = score.dct_putts['out']
      dct['total'] = score.dct_putts['total']
      dct['holes'] = score.dct_putts['holes']
      # build line for stdout
      line = '{:<6}'.format(score.nick_name)
      for putt in score.dct_putts['holes'][:9]:
        line += ' {:>3}'.format(putt) if putt is not None else '    '
      line += ' {:>4}'.format(dct['out'])
      for putt in score.dct_putts['holes'][9:]:
        line += ' {:>3}'.format(putt) if putt is not None else '    '
      line += ' {:>4} {:>4}'.format(dct['in'], dct['total'])
      dct['line'] = line
      lstPlayers.append(dct)
    self.dctScorecard['players'] = lstPlayers
    return self.dctScorecard

  def getLeaderboard(self, **kwargs):
    """Scorecard with all players."""
    board = []
    scores = sorted(self._players, key=lambda score: score.dct_putts['total'])
    pos = 1
    prev_total = None
    for score in scores:
      score_dct = {
        'player': score.doc,
        'total' : score.dct_putts['total'],
      }
      if prev_total != None and score_dct['total'] > prev_total:
        pos += 1
      prev_total = score_dct['total']
      score_dct['pos'] = pos
      for n,putt in enumerate(score.dct_putts['holes']):
        if putt is None:
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
    for n,putt in enumerate(self._players[0].dct_putts['holes']):
      if putt is None:
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

