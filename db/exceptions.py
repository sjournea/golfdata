"""exceptions.py - All golf exceptions defined here."""

class GolfException(Exception):
  """Base Golf app exception, all inherit from here."""
  pass

class GolfDBException(GolfException):
  """Golf database exception."""
  pass

class GolfGameException(GolfException):
  """Raised when a golf game need more information to resolve score."""
  def __init__(self, dct):
    self.dct = dct

  