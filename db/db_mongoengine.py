"""db_mongo_engine.py"""
from mongoengine import *
from mongoengine.fields import EmailField, StringField, FloatField, IntField, ReferenceField, ListField, EmbeddedDocumentField
from mongoengine.fields import DictField, DateTimeField

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

class Game(EmbeddedDocument):
  """Games played in a round."""
  game_type = StringField(max_length=16, required=True)
  options = DictField(default=dict)
  hole_data = DictField(default=dict)
  leaderboard = DictField(default=dict)
  scorecard = DictField(default=dict)
  status = DictField(default=dict)

class Round(Document):
  course = ReferenceField(Course, required=True)
  date_played = DateTimeField(required=True) 
  dict_options = DictField(default=dict)
  results = ListField(EmbeddedDocumentField(Result))
  games = ListField(EmbeddedDocumentField(Game))

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
