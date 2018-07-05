"""db_mongo_engine.py"""
from mongoengine import *
#from mongoengine.fields import EmailField, StringField, FloatField, IntField, ReferenceField, ListField, EmbeddedDocumentField

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

