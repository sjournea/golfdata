"""doc.py - wrapper classes for mongoengine Documents."""

class Doc(object):
  def __init__(self, doc):
    self.doc = doc
    for name in doc._fields.keys():
      setattr(self, name, getattr(doc, name))
  
  def save(self):
    self.doc.save()