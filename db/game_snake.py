""" game_snake.py - Implement."""
from .game import GolfGame,GamePlayer
from .exceptions import GolfGameException

class SnakePlayer(GamePlayer):
  def __init__(self, game, result):
    super().__init__(game, result)
    self.dct_points = self._init_dict()
    self.dct_snake = [None for _ in range(len(self.game.golf_round.course.holes))]

class GameSnake(GolfGame):
  """3 putt game."""
  short_description = 'Snake'
  description = """
3 putt a green and you could lose.
"""
  game_options = {
    'snake_type': {'choices': ('Points', 'Hold'), 'default': 'Hold', 'type': 'choice', 'desc': 'Points will lose every 3 putt. Hold will only lose when you already have the snake, always pays on 9 and 18.'},
  }
  
  def setup(self, **kwargs):
    """Start the game."""
    self._players = [SnakePlayer(self, result) for result in self.golf_round.results]
    self._has_snake = None
    # update header to scorecard
    title = ' Snake - {} '.format(self.snake_type)
    self.dctScorecard['header'] = '{0:*^98}'.format(title)
    self._thru = ''

  def _pay_snake(self, index, snake_winner):
    # immediate payout and release snake
    snake_winner.dct_points['holes'][index] = -1
    snake_winner.update_totals(snake_winner.dct_points)
    self._has_snake = None
    
  def _set_snake(self, index, snake_winner):
    # You just got the snake
    snake_winner.dct_snake[index] = 'S'
    self._has_snake = snake_winner
    
  def update(self):
    """Update gross results for all scores so far."""
    dct_three_putts = {hole.num: None for hole in self.golf_round.course.holes}
    for pl, result in zip(self._players, self.golf_round.doc.results):
      for score in result.scores:
        n = score.num
        if dct_three_putts[n] is None:
            dct_three_putts[n] = []
        if score.putts >= 3:
            dct_three_putts[n].append((pl, score.putts))
    hole_nums = sorted(dct_three_putts.keys())
    for hole_num in hole_nums:
      lst_losers = dct_three_putts[hole_num]
      if lst_losers == None:
        break
      self._thru = hole_num
      index = hole_num-1
      if self.snake_type == 'Points':
        # all 3 putters lose a point
        for pl,putts in lst_losers:
          self._pay_snake(index, pl)
      elif self.snake_type == 'Hold':
        # only one loser allowed
        if len(lst_losers) > 1:
          # Determine which 3 putt gets snake
          # 1st, is there a largest putt
          max_putts = max([tup[1] for tup in lst_losers])
          lst_losers = [tup for tup in lst_losers if tup[1] == max_putts]
          if len(lst_losers) > 1:
            if str(hole_num) in self.hole_data:
              loser = self.hole_data[str(hole_num)]['closest_3_putt']
              lst_losers = [tup for tup in lst_losers if tup[0].nick_name == loser]
            if len(lst_losers) > 1:
              dct = {
                'hole_num': hole_num,
                'players': [w[0].doc for w in lst_losers],
                'key': 'closest_3_putt',
                'msg': 'Which 3 putt player had the closest 1st putt on hole {}?'.format(hole_num),
                'game' : self,
              }
              raise GolfGameException(dct)
        #
        if len(lst_losers) == 1:
          # we have a 3 putt winner (loser)
          snake_winner = lst_losers[0][0]
          if self._has_snake and self._has_snake == snake_winner:
            # immediate payout and release snake
            self._pay_snake(index, snake_winner)
          else:
            self._has_snake = snake_winner
        if self._has_snake:
          self._set_snake(index, self._has_snake)
        # snake automatic payout on 9 and 18
        if hole_num in (9, 18) and self._has_snake:
          self._pay_snake(index, self._has_snake)

  def getScorecard(self, **kwargs):
    """Scorecard with all players."""
    lstPlayers = []
    for n,score in enumerate(self._players):
      dct = {'player': score.doc }
      dct['in'] = score.dct_points['in']
      dct['out'] = score.dct_points['out']
      dct['total'] = score.dct_points['total']
      dct['holes'] = score.dct_points['holes']
      dct['snake'] = score.dct_snake
      # build line for stdout
      line = '{:<6}'.format(score.nick_name)
      for putt,snake in zip(score.dct_points['holes'][:9], score.dct_snake[:9]):
        s = ''
        if putt:
          s = putt
        elif snake:
          s = snake
        line += ' {:>3}'.format(s)
      line += ' {:>4}'.format(dct['out'])
      for putt,snake in zip(score.dct_points['holes'][9:], score.dct_snake[9:]):
        s = ''
        if putt:
          s = putt
        elif snake:
          s = snake
        line += ' {:>3}'.format(s)
      line += ' {:>4} {:>4}'.format(dct['in'], dct['total'])
      dct['line'] = line
      lstPlayers.append(dct)
    self.dctScorecard['players'] = lstPlayers
    return self.dctScorecard

  def getLeaderboard(self, **kwargs):
    board = []
    self.dctLeaderboard['hdr'] = 'Pos Name  Points Thru'
    scores = sorted(self._players, key=lambda score: score.dct_points['total'], reverse=True)
    sort_by = 'total'
    pos = 1
    prev_total = None
    for sc in scores:
      score_dct = {
        'player': sc.doc,
        'total' : sc.dct_points['total'],
        'has_snake' : sc == self._has_snake,
      }
      if prev_total != None and score_dct[sort_by] != prev_total:
        pos += 1
      prev_total = score_dct[sort_by]
      score_dct['pos'] = pos
      score_dct['thru'] = self._thru
      score_dct['line'] = '{:<2} {}{:<6} {:>5} {:>4}'.format(
        score_dct['pos'], '*' if score_dct['has_snake'] else ' ', score_dct['player'].nick_name, score_dct['total'], score_dct['thru'])
      board.append(score_dct)
    self.dctLeaderboard['leaderboard'] = board
    return self.dctLeaderboard

  def getStatus(self, **kwargs):
    """Scorecard with all players."""
    for n,putt in enumerate(self._players[0].dct_points['holes']):
      if putt is None:
        self.dctStatus['next_hole'] = n+1
        line = ''
        if self.snake_type == 'Hold':
          if self._has_snake:
            line = '{} has the snake.'.format(self._has_snake.nick_name)
          else:
            line = 'snake is free.'
        self.dctStatus['line'] = line
        break
    else:
      # round complete
      self.dctStatus['next_hole'] = None
      self.dctStatus['line'] = 'Round complete'
    return self.dctStatus
