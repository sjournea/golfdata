""" game_greenie.py - GolfGame class."""
from collections import OrderedDict
from .game import GolfGame, GamePlayer
from .exceptions import GolfGameException

class GreeniePlayer(GamePlayer):
  def __init__(self, game, result):
    super().__init__(game, result)
    self.dct_greens = [None for _ in range(len(self.game.golf_round.course.holes))],
    self.dct_points = self._init_dict()
    self.dct_money = self._init_dict(score_type=float) if game.wager else None

class GameGreenie(GolfGame):
  """Basic Par 3 games."""
  short_description = 'Greenie'
  description = """
Closest shot to the pin on par 3 (on the green) and makes a par or better wins the hole.

Options:
  double_birdie: Birdies are worth double points. 
  carry_over: If nobody wins a par 3 then carries over to next par 3.
  last_par_3_carry: If nobody wins last par 3 then carry over to next hole and on green in regulation quailifies.  
"""
  game_options = {
    'double_birdie':    { 'default': False, 'type': 'bool',  'desc': 'Birdies are worth double points.'},
    'carry_over':       { 'default': True,  'type': 'bool',  'desc': 'If nobody wins a par 3 then carries over to next par 3.'},    
    'last_par_3_carry': { 'default': True,  'type': 'bool',  'desc': 'If nobody wins last par 3 then carry over to next hole and on green in regulation quailifies.'},    
    'wager':            { 'default': 0,     'type': 'float', 'desc': 'Wager per hole.'},    
  }
  
  def setup(self, **kwargs):
    """setup the game."""
    #self.carry_over = kwargs.get('carry_over', True)
    #self.double_birdie = kwargs.get('double_birdie', False)
    #self.last_par_3_carry = kwargs.get('last_par_3_carry', True)
    self._holes = [hole.num for hole in self.golf_round.course.get_holes_with_par(3)]
    if self.last_par_3_carry:
      self._last_par_3 = self._holes[-1]
      self._holes += [hole.num for hole in self.golf_round.course.holes[self._last_par_3:]]
    self._players = [GreeniePlayer(self, result) for result in self.golf_round.results]
    self._carry = 0
    self._next_hole = 0
    self._use_green_in_regulation = False
    self._thru = 0
    # add header to scorecard
    self.dctScorecard['header'] = '{0:*^98}'.format(' '+ self.short_description + ' ')
  
  def update(self):
    """Update gross results for all scores so far."""
    #print('holes:{}'.format(self._holes)) 
    dct_greens = {hole_num: None for hole_num in self._holes}
    for pl, result in zip(self._players, self.golf_round.doc.results):
      for n, score in enumerate(result.scores):
        n = score.num
        if n in self._holes:
          if dct_greens[n] is None:
            dct_greens[n] = []
          par = self.golf_round.course.holes[n-1].par
          if score.gross - score.putts == par - 2:
            dct_greens[n].append((pl, score))

    self.thru = self.golf_round.get_completed_holes()
    hole_nums = sorted(dct_greens.keys())
    for index in range(self.thru):
      hole_num = index + 1
      if hole_num in dct_greens:
        lst_winners = dct_greens[hole_num]
        par = self.golf_round.course.holes[index].par
        #print('hole_num:{} par:{} lst_winners:{}'.format(hole_num, par, lst_winners)) 
        # par 4 and 5 only valid if there is a carry
        if par > 3 and self._carry == 0:
          break
        if len(lst_winners) > 1:
          if hole_num in self.game._game_data and self.game._game_data[hole_num].get('qualified'):
            qualified = self.game._game_data[hole_num]['qualified']
            lst_winners = [w for w in lst_winners if str(w[0].player.nick_name) == qualified]
          else:
            dct = {
              'hole_num': hole_num,
              'players': [w[0].player for w in lst_winners],
              'key': 'qualified',
              'msg': 'Which player was closest to the pin on hole {}?'.format(hole_num),
              'game' : self,
             }
            raise GolfGameException(dct)
        if len(lst_winners) == 1:
          winner, score = lst_winners[0]
          # validate winner had 2 putts or less
          if score.putts < 3:
            # only get points on par 3
            value = 1 if par == 3 else 0
            winner.dct_points['holes'][index] = value + self._carry
            self._carry = 0
            if self.double_birdie and self.gross < par:
              # birdie or better
              winner.dct_points['holes'][index] *= 2
            if self.wager:
              winner.dct_money['holes'][index] = winner.dct_points['holes'][index]*len(self._players)
          else:
            lst_winners = []
        if not lst_winners:
          if self.carry_over and par == 3:
            self._carry += 1
    for pl in self._players:
      pl.update_totals(pl.dct_points)
      #pl.update_totals(pl.dct_money)
      
  def getScorecard(self, **kwargs):
    """Scorecard with all players."""
    lstPlayers = []
    for n,score in enumerate(self._players):
      dct = {'player': score.doc }
      dct['in'] = score.dct_points['in']
      dct['out'] = score.dct_points['out']
      dct['total'] = score.dct_points['total']
      dct['holes'] = score.dct_points['holes']
      # build line for stdout
      line = '{:<6}'.format(score.nick_name)
      for point in score.dct_points['holes'][:9]:
        line += ' {:>3}'.format(point) if point is not None else '    '
      line += ' {:>4}'.format(dct['out'])
      for point in score.dct_points['holes'][9:]:
        line += ' {:>3}'.format(point) if point is not None else '    '
      line += ' {:>4} {:>4}'.format(dct['in'], dct['total'])
      dct['line'] = line
      lstPlayers.append(dct)
    self.dctScorecard['players'] = lstPlayers
    return self.dctScorecard

  def getLeaderboard(self, **kwargs):
    board = []
    sort_type = kwargs.get('sort_type', 'points')
    if sort_type == 'money' and self.wager:
      self.dctLeaderboard['hdr'] = 'Pos Name  Money  Thru'
      scores = sorted(self._players, key=lambda score: score.dct_money['total'], reverse=True)
      sort_by = 'money'
    else:
      self.dctLeaderboard['hdr'] = 'Pos Name  Points Thru'
      scores = sorted(self._players, key=lambda score: score.dct_points['total'], reverse=True)
      sort_by = 'total'
    pos = 1
    prev_total = None
    for sc in scores:
      score_dct = {
        'player': sc.doc,
        'total' : sc.dct_points['total'],
        'money' : sc.dct_money['total'] if self.wager else None,
      }
      if prev_total != None and score_dct[sort_by] != prev_total:
        pos += 1
      prev_total = score_dct[sort_by]
      score_dct['pos'] = pos
      score_dct['thru'] = self._thru
      if sort_by == 'money':
        money = '--' if score_dct['money'] == 0.0 else '${:<2g}'.format(score_dct['money'])
        score_dct['line'] = '{:<3} {:<6} {:^5} {:>4}'.format(
          score_dct['pos'], score_dct['player'].nick_name, money, score_dct['thru'])
      else:
        score_dct['line'] = '{:<3} {:<6} {:>5} {:>4}'.format(
          score_dct['pos'], score_dct['player'].nick_name, score_dct['total'], score_dct['thru'])
      board.append(score_dct)
    self.dctLeaderboard['leaderboard'] = board
    return self.dctLeaderboard

  def getStatus(self, **kwargs):
    """Scorecard with all players."""
    if self._next_hole is None:
      self.dctStatus['next_hole'] = None
      self.dctStatus['line'] = 'Round complete'
    else:
      self.dctStatus['next_hole'] = self._next_hole+1
      line = ''
      if self._next_hole in self._holes:
        self.dctStatus['par'] = self.golf_round.course.holes[self._next_hole].par
        self.dctStatus['handicap'] = self.golf_round.course.holes[self._next_hole].handicap
        line = 'Hole {} Par {} Hdcp {} '.format(
            self.dctStatus['next_hole'], self.dctStatus['par'], self.dctStatus['handicap'])
      line += 'Carry:{}'.format(self._carry)
      if self.wager and self._carry:
        line += ' ${:<6g}'.format(self._carry*self.wager*len(self._players))
      if self._use_green_in_regulation:
        line += ' All greens in play'
      self.dctStatus['line'] = line
    return self.dctStatus

  @property
  def total_payout(self):
    """Overload to only count Par 3 holes."""
    # calc total payout, game only uses Par 3
    if self.wager:
      return len(self._par_3_holes)*self.wager*len(self._players)
    return None

