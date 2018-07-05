"""db_mongo_engine.py"""
from mongoengine import *
from mongoengine.fields import EmailField, StringField, FloatField, IntField, ReferenceField, ListField, EmbeddedDocumentField
from mongoengine.fields import DictField, DateTimeField

class Doc(object):
  def __init__(self, doc):
    self.doc = doc
    for name in doc._fields.keys():
      setattr(self, name, getattr(doc, name))

class DPlayer(Doc):
  def getFullName(self):
    return '{} {}'.format(self.first_name, self.last_name)
  
  def __str__(self):
    return 'email:{:<20} {:<30} - {:<15} {:>5.1f}'.format(self.email, self.getFullName(), self.nick_name, self.handicap)

class Player(Document):
  email = EmailField(required=True, unique=True)
  first_name = StringField(max_length=20)
  last_name = StringField(max_length=20)
  nick_name = StringField(max_length=20)
  handicap = FloatField()
  gender = StringField(required=True, choices=('man', 'woman'))


class Hole(EmbeddedDocument):
  num = IntField(required=True)
  par = IntField(required=True, choices=(3,4,5,6))
  handicap = IntField(required=True, choices=[n+1 for n in range(18)])

  #def validate(self):
    #if self.par not in self.valid_pars:
      #raise Exception('par must be {}'.format(self.valid_pars))
    #if self.handicap not in self.valid_handicaps:
      #raise Exception('handicap must be {}'.format(self.valid_handicaps))

  #def isPar(self, par):
    #return self.par == par
    
  #def __str__(self):
    #return 'par {} handicap {}'.format(self.par, self.handicap)


class Tee(EmbeddedDocument):
  gender = StringField(choices=('mens', 'womens'), default='mens')
  name = StringField(max_length=32, required=True)
  rating = FloatField(required=True)
  slope = IntField(required=True)


class Course(Document):
  name = StringField(max_length=132, unique=True, required=True)  
  holes = ListField(EmbeddedDocumentField(Hole), required=True)
  tees = ListField(EmbeddedDocumentField(Tee), required=True)

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
      for bp in xrange(handicap % 18, 0, -1):
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

class Score(EmbeddedDocument):
  """Player score for a single hole."""
  num = IntField(required=True)
  gross = IntField(required=True)
  putts = IntField()

class Result(EmbeddedDocument):
  """Player score for a round. References Score records."""
  player = ReferenceField(Player, required=True)
  tee = StringField(required=True)
  handicap = FloatField(required=True)
  course_handicap = IntField(required=True)
  scores = ListField(EmbeddedDocumentField(Score))

class DResult(Doc):

  #def get_completed_holes(self):
    #return len(self.scores)

  def __str__(self):
    return 'player:{} tee:{} handicap:{} course_handicap:{} scores{}'.format(self.player.nick_name, self.tee, self.handicap, self.course_handicap, self.scores)

class Game(EmbeddedDocument):
  """Games played in a round."""
  game_type = StringField(max_length=16, required=True)
  dict_data = DictField(default=dict)

  #def CreateGame(self):
    #game_class = SqlGolfGameFactory(self.game_type)
    #self._game_data = self.game_data
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


class Round(Document):
  course = ReferenceField(Course, required=True)
  date_played = DateTimeField(required=True) 
  dict_options = DictField(default=dict)
  results = ListField(EmbeddedDocumentField(Result))
  games = ListField(EmbeddedDocumentField(Game))

class DRound(Doc):

  def __init__(self, doc):
    super().__init__(doc)
    self.course = DCourse(doc.course)

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

  #OPTIONS = {
    #'handicap_type': {'type': 'enum', 'values': ('USGA', 'simple')},
  #}

  #def addScores(self, session, hole, dct_scores):
    #"""Add some scores for this round.

    #Args:
      #session: sqalchemy session.
      #hole : hole number, 1-number of holes on course.
      #dct_scores: dictionary of scare data.
        #lstGross - list of gross scores per player (required)
        #lstPutts - list of putts per player.
    #"""
    #if hole < 1 or hole > len(self.course.holes):
      #raise GolfException('hole number must be in 1-{}'.format(len(self.course.holes)))
    #lstGross = dct_scores['lstGross']
    #lstPutts = dct_scores.get('lstPutts')
    #if len(lstGross) != len(self.results):
      #raise GolfException('gross scores do not match number of players')
    #if lstPutts and len(lstPutts) != len(self.results):
      #raise GolfException('putts do not match number of players')
    ## update scores
    #for n,result in enumerate(self.results):
      #score = Score(num=hole, gross=lstGross[n], result=result)
      #if lstPutts:
        #score.putts = lstPutts[n]
      #session.add(score)
    ##print('dct_scores:{}'.format(dct_scores))
    #options = dct_scores.get('options')
    #if options:
      #for game in self.games:
        #if game.game_type in options:
          #golf_game = session.query(Game).filter(Game.round == self, Game.game_type == game.game_type).one()
          #golf_game.add_hole_dict_data(hole, options[game.game_type])
          #session.commit()

  #def addGame(self, session, game_type, options=None):
      ## Create Game
      #dict_data = {'options': options} 
      #game_class = SqlGolfGameFactory(game_type)
      ## game_instance = game_class(round, )
      #game = Game(round=self, game_type=game_type, dict_data=str(dict_data))
      #session.add(game)

  #def get_completed_holes(self):
    #return max([result.get_completed_holes() for result in self.results])

  def getScorecard(self, ESC=True):
    dct = self.course.getScorecard(ESC=ESC)
    dct['title'] = '{0:*^98}'.format(' '+ self.course.name + ' ' + str(self.date_played) + ' ')
    return dct

  def __str__(self):
    return '{} {:<30} - {}'.format(self.date_played, self.course.name, ','.join([result.player.nick_name for result in self.results]))

class Database(object):
  def __init__(self, url, database):
    self.url = url
    self.database = database
    self.db = None
    if self.database:
      self.connect()

  def connect(self, database=None):
    if database:
      self.database = database
    self.db = connect(self.database)

class DBAdmin(Database):
  """Database wrapper for golf admin objects."""

  def remove(self, database=None):
    """Delete a database."""
    database = database if database else self.database
    self.db.drop_database(database)
