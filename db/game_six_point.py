""" game.py - GolfGame class."""
from .game_net import GameNet, NetPlayer
from .exceptions import GolfException

class SixPointPlayer(NetPlayer):
  def __init__(self, game, result, min_handicap):
    super().__init__(game, result, min_handicap)
    self.dct_points = self._init_dict()


class GameSixPoint(GameNet):
  """Six point golf game."""
  short_description = 'Six Point'
  description = """
In the Six Point Game, three players compete for six points per hole.
Before the game, the players should agree to how much each point is worth
(consider that a player who never wins a point on any hole will owe about 100 points to his/her friends).

Handicaps are used in this game - the best player plays as scratch, and the other two players receive the
same number of strokes as the difference between their and the best player's course handicap. 

On each hole, the points can break down in four ways (as mentioned above, the scores on each hole are adjusted by the players' handicaps):
If there is a clear winner on the hole, that player wins 4 points. The golfer who finishes second receives 2 points, and the last place golfer receives nothing (4-2-0).
If two golfers tie for second they each receive 1 point, and the clear winner receives 4 points. (4-1-1).
If two golfers tie for lowest score, they win 3 points each, and the golfer with the high score receives nothing (3-3-0).
If all three golfers tie the hole, they each receive 2 points (2-2-2).
At the end of the match, all the points are totaled, with the low-point-total player paying both the other players a sum based on the difference between their final point totals. The player with the second highest point total also pays the high-point player based on the difference between their point totals.
"""
  POINTS_WIN_1ST = 4
  POINTS_TIE_1ST = 3
  POINTS_WIN_2ND = 2
  POINTS_TIE_2ND = 1
  POINTS_ALL_TIE = 2
  POINTS_3RD     = 0
  TITLE = 'Six Point'
  NAME = 'six_point'

  def validate(self):
    if len(self._players) != 3:
      raise GolfException('{} game must have 3 players, {} found.'.format(self.TITLE, len(self.scores)))

  def setup(self, **kwargs):
    """Start the skins game."""
    min_handicap = min([result.course_handicap for result in self.golf_round.results])
    self._players = [SixPointPlayer(self, result, min_handicap) for result in self.golf_round.results]
    self.dctScorecard['header'] = '{0:*^98}'.format(' {} '.format(self.TITLE))
    self.dctLeaderboard['hdr'] = 'Pos Name  Points Thru'

  def update(self):
    """Update gross results for all scores so far."""
    # call base class to update net scores
    super().update()
    # now do score updates
    self.thru = self.golf_round.get_completed_holes()
    for index in range(self.thru):
      players = sorted(self._players, key=lambda pl:pl.dct_net['holes'][index])
      scores = [pl.dct_net['holes'][index] for pl in players]
      if scores.count(scores[0]) == 3:
        # 1,1,1
        points = 3*[self.POINTS_ALL_TIE]
      elif scores.count(scores[0]) == 2:
        # 1,1,2
        points = [self.POINTS_TIE_1ST, self.POINTS_TIE_1ST, self.POINTS_3RD]
      elif scores.count(scores[1]) == 2:
        # 1,2,2
        points = [self.POINTS_WIN_1ST, self.POINTS_TIE_2ND, self.POINTS_TIE_2ND]
      else:
        # 1,2,3
        points = [self.POINTS_WIN_1ST, self.POINTS_WIN_2ND, self.POINTS_3RD]
      for pl,point in zip(players, points):
        pl.dct_points['holes'][index] = point
    for pl in self._players:
      pl.update_totals(pl.dct_points)

  def getScorecard(self, **kwargs):
    """Scorecard with all players."""
    lstPlayers = []
    for n,sc in enumerate(self._players):
      dct = {'player': sc.doc }
      dct['in'] = sc.dct_points['in']
      dct['out'] = sc.dct_points['out']
      dct['total'] = sc.dct_points['total']
      dct['holes'] = sc.dct_points['holes']
      line = '{:<6}'.format(sc.nick_name)
      for point in sc.dct_points['holes'][:9]:
        line += ' {:>3}'.format(point if point != None else '')
      line += ' {:>4d}'.format(dct['out'])
      for point in sc.dct_points['holes'][9:]:
        line += ' {:>3}'.format(point if point != None else '')
      line += ' {:>4d} {:>4d}'.format(dct['in'], dct['total'])
      dct['line'] = line
      lstPlayers.append(dct)
    self.dctScorecard['players'] = lstPlayers
    return self.dctScorecard
  
  def getLeaderboard(self, **kwargs):
    board = []
    scores = sorted(self._players, key=lambda pl: pl.dct_points['total'], reverse=True)
    pos = 1
    thru = self.golf_round.get_completed_holes()
    prev_total = None
    for sc in scores:
      score_dct = {
        'player': sc.doc,
        'total' : sc.dct_points['total'],
      }
      if prev_total != None and score_dct['total'] < prev_total:
        pos += 1
      prev_total = score_dct['total']
      score_dct['pos'] = pos
      score_dct['thru'] = thru
      score_dct['line'] = '{:<3} {:<6} {:>5} {:>4}'.format(
        score_dct['pos'], score_dct['player'].nick_name, score_dct['total'], score_dct['thru'])
      board.append(score_dct)
    self.dctLeaderboard['leaderboard'] = board
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
        self.dctStatus['line'] += ' Bumps:{}'.format(','.join(bump_line))
      self.dctStatus['line'] += ' Points:{},{},{}'.format(
        self.POINTS_WIN_1ST, self.POINTS_WIN_2ND, self.POINTS_3RD)
    else:
      # round complete
      self.dctStatus['next_hole'] = None
      self.dctStatus['par'] = self.golf_round.course.total
      self.dctStatus['handicap'] = None
      self.dctStatus['line'] = 'Round Complete'
    return self.dctStatus
