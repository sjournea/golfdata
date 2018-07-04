#!/usr/bin/env python3
"""dbmain.py"""
import logging
import platform
if platform.system() == 'Linux':
  import readline
import threading
import traceback

from util.menu import MenuItem, Menu, InputException, FileInput
from util.tl_logger import TLLog,logOptions

import mongoengine as eng
from db.db_mongoengine import DPlayer, Player
from db.data.test_players import DBGolfPlayers

TLLog.config('logs/dbmain.log', defLogLevel=logging.INFO )

log = TLLog.getLogger('dbmain')

class DBMenu(Menu):
  def __init__(self, **kwargs):
    cmdFile = kwargs.get('cmdFile')
    self.url = kwargs.get('url')
    self.database = kwargs.get('database')
    if self.database:
      self.db = eng.connect(self.database)
    super().__init__(cmdFile)
    # add menu items
    self.addMenuItem( MenuItem( 'dbl', '<database>',        
                                'list databases.', self._dbList) )
    self.addMenuItem( MenuItem( 'dr', '<database>',        
                                'drop database.', self._dbDrop) )
    self.addMenuItem( MenuItem( 'plc', 'email,first_name,last_name,nick_name,handicap,gender',        
                                'create a player.', self._playerCreate) )
    self.addMenuItem( MenuItem( 'plr', '',        
                                'retrieve a player.', self._playerRetrieve) )
    self.addMenuItem( MenuItem( 'plu', 'email,first_name,last_name,nick_name,handicap,gender',        
                                'update a player.', self._playerUpdate) )
    self.addMenuItem( MenuItem( 'pld', 'email',        
                                'detete a player.', self._playerDelete) )
    self.addMenuItem( MenuItem( 'testdata', '<players|courses>',        
                                'insert test data into database.', self._testData) )
    self.updateHeader()

  def updateHeader(self):
    self.header = 'database url:{} - database:{}'.format(self.url, self.database)

  def _dbConnect(self):
    self.database = self.lstCmd[1]
    eng.connect(self.database)

  def _dbDrop(self):
    self.db.drop_database(self.database)

  def _dbList(self):
    pass

  def _playerCreate(self):
    dct = {}
    for arg in self.lstCmd[1:]:
      lst = arg.split('=')
      if len(lst) == 2:
        dct[lst[0]] = lst[1]
    player = Player(**dct)
    player.save()
  
  def _testData(self):
    for dct in DBGolfPlayers:
      player = Player(**dct)
      player.save()
  
  def _playerRetrieve(self):
    for n,doc in enumerate(Player.objects):
      player = DPlayer(doc)
      print('  {:>3} {}'.format(n,player))

  def _playerUpdate(self):
    pass

  def _playerDelete(self):
    pass

def main():
  DEF_LOG_ENABLE = 'dbmain'
  DEF_DATABASE = 'golfdata'
  # build the command line arguments
  from argparse import ArgumentParser
  parser = ArgumentParser()
  parser.add_argument('-d', '--database', default=DEF_DATABASE,
                     help='Set database to use. Default {}'.format(DEF_DATABASE))
  parser.add_argument('--logenable', default=DEF_LOG_ENABLE,
                     help='Comma separated list of log modules to enable, * for all. Default is "%s"' % DEF_LOG_ENABLE)
  parser.add_argument('--showlogs', action="store_true",
                     help='list all log options.' )
  parser.add_argument('-c', '--cmdFile', default=None,
                     help="Run a command file at startup.")

  #  parse the command line and set values
  args = parser.parse_args()

  master = None
  try:
    # set the main thread name
    thrd = threading.currentThread()
    thrd.setName( 'dbmain' )

    log.info(80*"*")
    log.info( 'dbmain - starting' )
    logOptions(args.logenable, args.showlogs, log=log)

    # create menu application 
    menu = DBMenu(database=args.database,cmdFile=args.cmdFile)
    menu.runMenu()

  except Exception as err:
    s = '%s: %s' % (err.__class__.__name__, err)
    log.error(s)
    print(s)

    print('-- traceback --')
    traceback.print_exc()
    print()

  finally:
    log.info( 'dbmain - exiting' )
    TLLog.shutdown()        

if __name__ == '__main__':
  main()

#if __name__ == '__main__':
