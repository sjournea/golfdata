"""dplayer.py - wrapper classes for mongoengine Documents."""
from .doc import Doc

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

