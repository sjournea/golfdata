"""wrap.py - wrapper classes for mongoengine Documents."""
from .doc import Doc
from .game_factory import GolfGameFactory

class DPlayer(Doc):
  def getFullName(self):
    return '{} {}'.format(self.first_name, self.last_name)

  def getInitials(self):
    return self.first_name[0] + self.last_name[0]
  
  dct_plural_gender = {'man': 'mens', 'woman': 'womens'}
  @property
  def genderPlural(self):
    return self.dct_plural_gender[self.gender]
  
  def __str__(self):
    return '{:<15} - {:<6} {:<10} {:<8} {:<5} handicap {:.1f}'.format(
        self.email, self.first_name, self.last_name, self.nick_name, self.gender, self.handicap)

class DCourse(Doc):
  def setStats(self):
    """Par totals."""
    self.out_tot = sum([hole.par for hole in self.holes[:9]])
    self.in_tot  = sum([hole.par for hole in self.holes[9:]])
    self.total   = self.in_tot + self.out_tot

  def getScorecard(self, **kwargs):
    """Return hdr, par and hdcp lines for scorecard."""
    self.setStats()
    hdr  = 'Hole  '
    par  = 'Par   '
    hdcp = 'Hdcp  '
    ESC = kwargs.get('ESC', False)
    for n,hole in enumerate(self.holes[:9]):
      hdr += ' {:>3}'.format(n+1)
      par += ' {:>3}'.format(hole.par)
      hdcp += ' {:>3}'.format(hole.handicap)
    hdr += '  Out '
    par += ' {:>4} '.format(self.out_tot)
    hdcp += '      '
    for n,hole in enumerate(self.holes[9:]):
      hdr += '{:>3} '.format(n+10)
      par += '{:>3} '.format(hole.par)
      hdcp += '{:>3} '.format(hole.handicap)
    hdr += '  In  Tot'
    par += '{:>4} {:>4}'.format(self.in_tot, self.total)
    if ESC:
      hdr += '  ESC'
    return { 'title': '{0:*^98}'.format(' '+self.name+' '),
             'hdr': hdr,
             'par': par,
             'hdcp': hdcp,
           }

  def course_par(self):
    return sum([hole.par for hole in self.holes])

  def calcESC(self, hole_index, gross, course_handicap):
    """Determine ESC post value for this gross score."""
    esc = gross
    if course_handicap < 10:
      # Max double bogey
      max_gross = self.holes[hole_index].par + 2
      esc = gross if gross < max_gross else max_gross
    elif course_handicap < 20:
      # Max value of 7
      esc = gross if gross < 7 else 7
    elif course_handicap < 30:
      # Max value of 8
      esc = gross if gross < 8 else 8
    elif course_handicap < 40:
      # Max value of 9
      esc = gross if gross < 9 else 9
    else:
      # course_handicap >= 40
      # Max value of 10
      esc = gross if gross < 10 else 10
    return esc

  def calcBumps(self, handicap):
    """Determine bumps basid in this handicap.

    Args:
      handicap: course handicap.
    Returns:
      list of bumps for each hole.
    """
    bumps = [0 for _ in range(len(self.holes))]
    # handicap > 18 will bump all holes
    while handicap > 17:
      bumps = [x+1 for x in bumps]
      handicap -= 18
    # now handicaps < 18
    if handicap > 0:
      for bp in range(handicap % 18, 0, -1):
        for n,hole in enumerate(self.holes):
          if hole.handicap == bp:
            bumps[n] += 1
            break
    return bumps

  def get_holes_with_par(self, par):
    """Return list of holes with par argument.
    
    Args:
      par: par value for holes to match.
    """
    return [hole for hole in self.holes if hole.par == par]
  
  def __str__(self):
    return '{:<40} - {:>2} holes - {:>2} tees par:{}'.format(self.name, len(self.holes), len(
      self.tees), self.course_par())

class DResult(Doc):

  #def get_completed_holes(self):
    #return len(self.scores)

  def __str__(self):
    return 'player:{} tee:{} handicap:{} course_handicap:{} scores{}'.format(self.player.nick_name, self.tee, self.handicap, self.course_handicap, self.scores)

#class DGame(Doc):
  #def __init__(self, doc):
    #super().__init__(doc)
    
    
  #def CreateGame(self):
    #game_class = SqlGolfGameFactory(self.game_type)
    #game = game_class(self, self.round, **self._game_data['options'])
    #game.validate()
    #game.update()
    #return game

  #@property
  #def game_data(self):
    #return ast.literal_eval(self.dict_data)
  
  #@game_data.setter
  #def game_data(self, value):
    #self.dict_data = str(value)
    
  #def add_hole_dict_data(self, hole_num, dct_data):
    #dct = self.game_data
    #dct[hole_num] = dct_data
    #self.game_data = dct

class DRound(Doc):
  OPTIONS = {
    'handicap_type': {'type': 'enum', 'values': ('USGA', 'simple')},
  }
  def __init__(self, doc):
    super().__init__(doc)
    self.course = DCourse(doc.course)
    # create all games
    self.games = []
    for doc_game in self.doc.games:
      game_class = GolfGameFactory(doc_game.game_type)
      game = game_class(doc_game, self)
      self.games.append(game)

  def update_games(self):
    # create all games
    for game in self.games:
      game.update()
      game.doc.leaderboard = game.getLeaderboard()
      game.doc.scorecard = game.getScorecard()
      game.doc.status = game.getStatus()

  def calcCourseHandicap(self, player, tee_name):
    """Course Handicap = Handicap Index * Slope rating / 113."""
    handicap_type = self.dict_options.get('handicap_type', 'USGA')
    course_handicap = None
    slope = None
    if handicap_type == 'simple':
      # Course Handicap = round(handicap)
      course_handicap = round(player.handicap)
    elif handicap_type == 'USGA':
      # Course Handicap = Handicap Index * Slope rating / 113
      # need to get the tee slope rating from the course
      tee_gender = 'mens' if player.gender == 'man' else 'womens'
      for tee in self.course.tees:
        if tee.name == tee_name and tee.gender == tee_gender:
          slope = tee.slope
          break
      else:
        raise Exception('{} tee <{}> not found.'.format(tee_gender, tee_name))
      course_handicap = int(round(player.handicap * slope / 113))
    else:
      raise Exception('handicap type <{}> not supported.'.format(handicap_type))
    print('calcCourseHandicap() handicap_type:{} handicap:{} slope:{} course_handicap:{}'.format(handicap_type, player.handicap, slope, course_handicap))
    return course_handicap

  #def get_completed_holes(self):
    #return max([result.get_completed_holes() for result in self.results])

  def getScorecard(self, ESC=True):
    dct = self.course.getScorecard(ESC=ESC)
    dct['title'] = '{0:*^98}'.format(' '+ self.course.name + ' ' + str(self.date_played) + ' ')
    return dct

  def __str__(self):
    return '{} {:<30} - {}'.format(self.date_played, self.course.name, ','.join([result.player.nick_name for result in self.results]))


