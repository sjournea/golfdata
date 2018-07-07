"""game_best_ball.py - Best Ball Golf Game class."""
import ast
from .game_net import GameNet, NetPlayer
from .game import GolfTeam

class BestBallTeam(GolfTeam):
  def setup(self, min_handicap=None):
    """Setup holes and scores for match play."""
    self.course = self.game.golf_round.course
    self._net = [None for _ in range(len(self.course.holes))]
    self._hole = [None for _ in range(len(self.course.holes))]
    self._score = [None for _ in range(len(self.course.holes))]
    self._in = 0
    self._out = 0
    self._total = 0
    self._win = None
    self._status = 'All Square'

  @property
  def status(self):
    return self._status

  def print_net_scores(self):
    print('team:{}'.format(self.name))
    for pl in self.players:
      print('  {:<10}: {}'.format(pl.player.nick_name, pl.dct_net['holes'])) 

  
  def calculate_score(self, index):
    # net scores have already set.
    self._net[index] = min([pl.dct_net['holes'][index] for pl in self.players])

  def update_points(self, index, other_team):
    if self._net[index] < other_team._net[index]:
      # win hole 
      self._hole[index] = 1
      self._total += 1
      self._score[index] = self._total
    elif self._net[index] > other_team._net[index]:
      # lose hole
      self._hole[index] = -1
      self._total -= 1
      self._score[index] = self._total
    else: 
      # hole tied
      self._hole[index] = 0
      self._score[index] = self._total
    self._out = sum([sc for sc in self._hole[:9] if isinstance(sc, int)])
    self._in  = sum([sc for sc in self._hole[9:] if isinstance(sc, int)])

  def update_status(self, to_play):
    if self._total == 0:
      self._status = 'All Square' if to_play > 0 else 'Draw'
    if self._total > 0:  
      # In the lead
      self._status = '{} Up'.format(self._total)
      if self._total > to_play:
        self._win = True
        if to_play > 0:
          self._status = '{} & {}'.format(self._total, to_play)
    if self._total < 0:
      # losing
      self._status = '{} Down'.format(abs(self._total))
      if self._total + to_play > 0:
        self._win = False
        self._status = ''
    if self._win is None and to_play > 0 and to_play < 5:
      self._status += ' {} to play'.format(to_play)
    return self._win
  
  def get_scorecard(self, index):
    """Scorecard for team."""
    def score_string(index, score):
      s = ''
      if score is not None:
        if score > 0:
          s = '{:d}'.format(score)
        elif index == 0 and score == 0:
          s = 'AS'
        else:
          s = '-'
      return s
    #
    dct = {'team': self.name }
    dct['in'] = self._in
    dct['out'] = self._out
    dct['total'] = self._total
    dct['holes'] = self._score
    line = '{:<6}'.format(self.name)
    for i,score in enumerate(self._score[:9]):
      line += ' {:>3}'.format(score_string(index, score))
    line += ' {:>4}'.format(score_string(index, self._out))
    for i,score in enumerate(self._score[9:]):
      line += ' {:>3}'.format(score_string(index, score))
    line += ' {:>4} {:>4}'.format(score_string(index, self._in), score_string(index, self._total))
    dct['line'] = line
    return dct

  def __str__(self):
    return 'name:{} status:{}'.format(self.name, self.status)
  
class GameBestBall(GameNet):
  """The Best ball golf game."""
  short_description = 'BestBall'
  description = """
Two-Person Best Ball: Two golfers play as a team, each with their own ball. The best score on each hole is taken as the 'Team' Score.
Best ball games can be played as match or as medal for 9 holes, 18 holes, or even as a Nassau. 

Three-Person Best Ball (a.k.a Canadian Best Ball): In Canadian Best Ball, two golfers team up and play against a third 
(usually the low handicapper). The two partners play their best ball against the third. 

Four-Person Best Ball: Here, the best ball team is composed of all four players. Again, the lowest score on each 
hole counts as the tam score. Games can also be played that use the best two scores or best three scores of the foursome. 

Allocating Handicap Strokes for Best Ball Games % of Course Handicap
Game	 	                        Men %	Women %
Two-Person Best Ball (stroke)	 	 90%	 95%
Two-Person Best Ball (match)	 	100%	100%
Four-Person Best Ball	 	         80%	 90%
Four-Person Best Two Balls	 	 90%	 95%
"""
  #    '<attribute>': {'default': <default>, 'type': <data type>, 'desc': 'Option description>'},
  game_options = {
    'teams':  { 'default': [(0,1),(2,3)], 'type': 'tuple[2][2]',  'desc': 'Set teams for best ball match.' },
  }
  def validate(self):
    if len(self._players) != 4:
      raise GolfException('Best ball game must have 4 players, {} found.'.format(len(self.scores)))
    if len(self.teams) != 2:
      raise GolfException('2 teams of 2 players must be set.')
    lst = [0 for n in range(4)]
    for team in self.teams:
      if len(team) != 2:
        raise GolfException('Teams must have 2 players.')
      lst[team[0]] += 1 
      lst[team[1]] += 1
    for cnt in lst:
      if cnt != 1:
        raise GolfException('Malformed team.')

  @property
  def final(self):
    return bool(self.winner or self.to_play == 0)
  
  def setup(self, **kwargs):
    """Start the match game."""
    self.use_full_net = True
    self.winner = None
    self.thru = None
    # TODO - for stroke play will need to adjust handicap
    handicap_multiplier = 1
    # find min handicap in all players
    #min_handicap = min([result.course_handicap*handicap_multiplier for result in self.golf_round.results])
    self._players = [NetPlayer(self, result, 0) for result in self.golf_round.results]
    # create teams
    self.team_list = [BestBallTeam(self, [self._players[i1], self._players[i2]]) for (i1,i2) in self.teams]
    for team in self.team_list:
      team.setup()
      
    self.to_play = len(self.golf_round.course.holes)
    self.dctScorecard['header'] = '{0:*^98}'.format(' BestBall - Match Play')
    self.dctLeaderboard['hdr'] = 'Pos Name   Points Thru'

  def update(self):
    # call base class to update net scores
    super().update()
    # now do team updates
    self.thru = self.golf_round.get_completed_holes()
    self.to_play = len(self.golf_round.course.holes) - self.thru
    for index in range(self.thru):
      for team in self.team_list:
        # print net scores
        #team.print_net_scores()
        team.calculate_score(index)
      self.team_list[0].update_points(index, self.team_list[1])  
      self.team_list[1].update_points(index, self.team_list[0])  
    # update match status
    for team in self.team_list:
      if team.update_status(self.to_play):
        self.winner = team
      
  def getScorecard(self, **kwargs):
    """Scorecard with all players."""
    self.dctScorecard['players'] = [team.get_scorecard(index) for index,team in enumerate(self.team_list)]
    return self.dctScorecard
  
  def getLeaderboard(self, **kwargs):
    self.dctLeaderboard['thru'] = self.thru
    self.dctLeaderboard['to_play'] = self.to_play
    self.dctLeaderboard['final'] = self.final
    board = []
    for n,team in enumerate(self.team_list):
      line = '{:<10}'.format(team.name)
      if team._total > 0 or (team._total == 0 and n == 0):
        line += team.status
      dct = {
        'team': team.name,
        'line': line,
        'status': team.status,
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
      for pl in self._players:
        if pl._bumps[n] > 0:
          dct = {'player': pl.doc, 'bumps': pl._bumps[n]}
          bumps.append(dct)
          bump_line.append('{}{}'.format(pl.nick_name, '({})'.format(dct['bumps']) if dct['bumps'] > 1 else ''))
      self.dctStatus['bumps'] = bumps
      self.dctStatus['line'] = 'Hole {} Par {} Hdcp {}'.format(
        self.dctStatus['next_hole'], self.dctStatus['par'], self.dctStatus['handicap'])
      if bumps:
        self.dctStatus['line'] += ' Bumps:{}'.format(','.join(bump_line))
    else:
      # round complete
      self.dctStatus['next_hole'] = None
      self.dctStatus['par'] = self.golf_round.course.total
      self.dctStatus['handicap'] = None
      self.dctStatus['line'] = 'Round Complete'
    return self.dctStatus


