"""db_mongo_engine.py"""
from mongoengine import Document
from mongoengine.fields import EmailField, StringField, FloatField

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


