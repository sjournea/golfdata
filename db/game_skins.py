""" game.py - GolfGame class."""
from operator import itemgetter
from .game import GolfGame,GamePlayer

class SkinsPlayer(GamePlayer):
  def __init__(self, game, result, min_handicap):
    super().__init__(game, result)
    self.dct_nets = self._init_dict()
    self._bumps = self.calc_bumps(min_handicap)
    self.dct_skins = self._init_dict()


class GameSkins(GolfGame):
  """The Skins game."""
  short_description = 'Skins'
  description = """
Skins is very much a match play format, but it is usually played between three or four players.
Each hole is played separately, and is won by the player with the lowest score on the hole -- that golfer wins 'the skin'.
The interesting part of the game happens when two or more players tie for the low score.
In this case there is 'no blood,' and the skin 'carries over' to the next hole, doubling its worth.
At the end of the game, each player settles up based on the number of skins they have. 

Skins games are played using handicaps by playing off of the lowest handicap golfer.
For example, imagine three golfers of handicaps 8, 16, and 28 were to play a game of skins.
In this match the lowest handicap golfer would play straight up,
the 16 handicap golfer would receive 8 strokes on the hardest 8 holes (as denoted by the HDCP number on the scorecard),
and the 28 handicap golfer would receive 2 strokes on the hardest two holes and a stroke on the rest of the holes.

Each person brings a skin to the hole, and the winner of the hole wins a skin from each of the losing players.
For a threesome this means that the winner wins two skins on a hole. For a foursome, this means three skins.
In both cases the other players each lose a skin. 
"""
  game_options = {
    'use_carryover': {'default': True, 'type': 'bool', 'desc': 'If use_carryover is set then skins not won will carry to the next hole'},
  }
  
  def setup(self, **kwargs):
    """Start the skins game."""
    # find min handicap in all players
    min_handicap = min([result.course_handicap for result in self.golf_round.results])
    self._players = [SkinsPlayer(self, result, min_handicap) for result in self.golf_round.results]
    # skins carryover set to 1
    self.carryover = 1
    self.dctScorecard['header'] = '{0:*^98}'.format(' Skins ')
    self.dctLeaderboard['hdr'] = 'Pos Name   Skins Thru'

  def update(self):
    """Update gross results for all scores so far."""
    for pl, result in zip(self._players, self.golf_round.doc.results):
      # calculate net
      for score in result.scores:
        n = score.num-1
        pl.dct_nets['holes'][n] = score.gross - pl._bumps[n] 
    for n in range(len(self.golf_round.course.holes)):
      if pl.dct_nets['holes'][n] == None:
        continue
      net_scores = [pl.dct_nets['holes'][n] for pl in self._players]
      net_scores.sort()
      winner = net_scores[0] < net_scores[1]
      for pl in self._players:
        if winner and pl.dct_nets['holes'][n] == net_scores[0]:
          win = self.carryover * (len(self._players)-1)
          pl.dct_skins['holes'][n] = win
          self.carryover = 1
        pl.update_totals(pl.dct_skins)
      if not winner and self.use_carryover:
        self.carryover += 1

  def getScorecard(self, **kwargs):
    """Scorecard with all players."""
    lstPlayers = []
    for n,sc in enumerate(self._players):
      dct = {'player': sc.doc }
      dct['in'] = sc.dct_skins['in']
      dct['out'] = sc.dct_skins['out']
      dct['total'] = sc.dct_skins['total']
      dct['holes'] = sc.dct_skins['holes']
      line = '{:<6}'.format(sc.nick_name)
      for skin,bumps in zip(sc.dct_skins['holes'][:9], sc._bumps[:9]):
        # show bumps
        sk = bumps*'*'
        if skin and skin > 0:
          sk += '{:d}'.format(skin)
        line += ' {:>3}'.format(sk)
      line += ' {:>4d}'.format(dct['out'])
      for skin,bumps in zip(sc.dct_skins['holes'][9:], sc._bumps[9:]):
        # show bumps
        sk = bumps*'*'
        if skin and skin > 0:
          sk += '{:d}'.format(skin)
        line += ' {:>3}'.format(sk)
      line += ' {:>4d} {:>4d}'.format(dct['in'], dct['total'])
      dct['line'] = line
      lstPlayers.append(dct)
    self.dctScorecard['players'] = lstPlayers
    return self.dctScorecard
  
  def getLeaderboard(self, **kwargs):
    board = []
    scores = sorted(self._players, key=lambda score: score.dct_skins['total'], reverse=True)
    pos = 1
    prev_total = None
    for sc in scores:
      score_dct = {
        'player': sc.doc,
        'total' : sc.dct_skins['total'],
      }
      if prev_total != None and score_dct['total'] < prev_total:
        pos += 1

      prev_total = score_dct['total']
      score_dct['pos'] = pos
      for n,net in enumerate(sc.dct_nets['holes']):
        if net is None:
          break
      else:
        n += 1
      score_dct['thru'] = n
      score_dct['line'] = '{:<3} {:<6} {:>+5} {:>4}'.format(
        score_dct['pos'], score_dct['player'].nick_name, score_dct['total'], score_dct['thru'])
      board.append(score_dct)
    self.dctLeaderboard['leaderboard'] = board
    return self.dctLeaderboard

  def getStatus(self, **kwargs):
    for n,net in enumerate(self._players[0].dct_nets['holes']):
      if net is None:
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
        self.dctStatus['line'] += ' Skins:{}'.format(self.carryover)
        break
    else:
      # round complete
      self.dctStatus['next_hole'] = None
      self.dctStatus['par'] = self.golf_round.course.total
      self.dctStatus['handicap'] = None
      self.dctStatus['line'] = 'Round Complete'
    return self.dctStatus
