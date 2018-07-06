#!/usr/bin/env python3
"""dbmain.py"""
import datetime
import logging
import platform
if platform.system() == 'Linux':
  import readline
import threading
import traceback

from util.menu import MenuItem, Menu, InputException, FileInput
from util.tl_logger import TLLog,logOptions

from mongoengine import *
from db.db_mongoengine import Player, Course, Tee, Hole, Round, Result, Game, Score
from db.wrap import DPlayer, DCourse, DRound, DResult
from db.db_mongoengine import Database, DBAdmin
from db.data.test_players import DBGolfPlayers
from db.data.test_courses import DBGolfCourses
from db.game_factory import GolfGameFactory

TLLog.config('logs/dbmain.log', defLogLevel=logging.INFO )

log = TLLog.getLogger('dbmain')

class DBMenu(Menu):
  def __init__(self, **kwargs):
    cmdFile = kwargs.get('cmdFile')
    url = kwargs.get('url')
    database = kwargs.get('database')
    self.db = DBAdmin(url, database)
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
    #self.addMenuItem( MenuItem( 'coc', 'email,first_name,last_name,nick_name,handicap,gender',        
                                #'create a course.', self._courseCreate) )
    self.addMenuItem( MenuItem( 'cor', '',        
                                'retrieve a course.', self._courseRetrieve) )
    self.addMenuItem( MenuItem( 'cos', '<name>',        
                                'return a course scorecard.', self._courseGetScorecard) )
    #self.addMenuItem( MenuItem( 'cou', 'email,first_name,last_name,nick_name,handicap,gender',        
                                #'update a course.', self._courseUpdate) )
    self.addMenuItem( MenuItem( 'cod', 'email',        
                                'detete a course.', self._courseDelete) )
    self.addMenuItem( MenuItem( 'ror', '',        
                                'retrieve rounds.', self._roundRetrieve) )
    self.addMenuItem( MenuItem( 'testdata', '<players|courses>',        
                                'insert test data into database.', self._testData) )
    self.addMenuItem( MenuItem( 'gcr', '<course> <YYYY-MM-DD> [option=value,...]',
                                'Create a Round of Golf',      self._roundCreate))
    self.addMenuItem( MenuItem( 'gad', '<email> <tee>',
                                'Add player to Round of Golf', self._roundAddPlayer))
    self.addMenuItem( MenuItem( 'gag', '<game> <players>',
                                'Add game to Round of Golf',   self._roundAddGame))
    self.addMenuItem( MenuItem( 'gst', '',
                                'Start Round of Golf',         self._roundStart))
    self.addMenuItem( MenuItem( 'gas', '<hole> gross=<gross..> <pause=enable>',
                                'Add Scores',                 self._roundScore))
    self.updateHeader()

  def updateHeader(self):
    self.header = 'database url:{} database:{}'.format(self.db.url, self.db.database)

  def _dbConnect(self):
    self.database = self.lstCmd[1]
    connect(self.database)

  def _dbDrop(self):
    database = self.lstCmd[1] if len(self.lstCmd) > 1 else None
    self.db.remove(database)

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
    if self.lstCmd[1] == 'players':
      for dct in DBGolfPlayers:
        player = Player(**dct)
        player.save()
    elif self.lstCmd[1] == 'courses':
      for dct in DBGolfCourses:
        holes = [Hole(par=gh['par'], handicap=gh['handicap'], num=n+1) for n,gh in enumerate(dct['holes'])]
        tees = [Tee(gender=gt['gender'], name=gt['name'], rating=gt['rating'], slope=gt['slope']) for n,gt in enumerate(dct['tees'])]
        course = Course(name=dct['name'], holes=holes, tees=tees)
        course.save()
    else:
      raise InputException('only players or courses supported.')
  
  def _playerRetrieve(self):
    for n,doc in enumerate(Player.objects):
      player = DPlayer(doc)
      print('  {:>3} {}'.format(n,player))

  def _playerUpdate(self):
    pass

  def _playerDelete(self):
    pass

  def _courseRetrieve(self):
    for n,doc in enumerate(Course.objects):
      course = DCourse(doc)
      print('  {:>3} {}'.format(n,course))

  def _courseDelete(self):
    pass

  def _courseGetScorecard(self):
    if len(self.lstCmd) < 2:
      raise InputException('Not enough arguments for {} command'.format(self.lstCmd[0]))
    name = self.lstCmd[1]
    courses = Course.objects(name__contains=name)
    for doc in courses:
      course = DCourse(doc)
      dct = course.getScorecard()
      print(course.name)
      print(dct['hdr'])
      print(dct['par'])
      print(dct['hdcp'])

  def _roundCreate(self):
    # gcr <course> <YYYY-MM-DD> [option=value,...]
    if len(self.lstCmd) < 3:
      raise InputException( 'Not enough arguments for %s command' % self.lstCmd[0] )
    course_name = self.lstCmd[1]
    dtPlay = datetime.datetime.strptime(self.lstCmd[2], "%Y-%m-%d")
    # get options
    options = {}
    for option in self.lstCmd[3:]:
      lst = option.split('=')
      options[lst[0]] = lst[1]

    courses = Course.objects(name__contains=course_name)
    if not courses:
      raise InputException('Course name <{}> not matched.'.format(course_name))
    elif len(courses) > 1:
      raise InputException('Course name <{}> not unique. Matches {}'.format(course_name, len( courses)))
    course = courses[0]

    golf_round = Round(course=course, date_played=dtPlay, dict_options=options)
    golf_round.save()
    self._round_id = golf_round.id
    print('new round id = {}'.format(self._round_id))

  def _roundAddPlayer(self):
    # gap <email match> <tee>
    if self._round_id is None:
      raise InputException( 'Golf round not created')
    if len(self.lstCmd) < 3:
      raise InputException( 'Not enough arguments for %s command' % self.lstCmd[0] )
    email = self.lstCmd[1]
    tee_name = self.lstCmd[2]

    # get round
    doc_round = Round.objects(id=self._round_id).first()
    golf_round = DRound(doc_round)
    # find player
    players = Player.objects(email__contains=email)
    if not players:
      raise InputException('Player email <{}> not matched.'.format(email))
    elif len(players) > 1:
      raise InputException('Player email <{}> not unique. Matches {}'.format(email, len(players)))
    doc_player = players[0]
    player = DPlayer(doc_player)
    # Create Result
    course_handicap = golf_round.calcCourseHandicap(player, tee_name)
    doc_result = Result(player=doc_player, tee=tee_name, handicap=doc_player.handicap, course_handicap=course_handicap)
    doc_round.results.append(doc_result)
    doc_round.save()

    result = DResult(doc_result)
    print('Round:{}'.format(golf_round))
    print('Player:{}'.format(player))
    print('Result:{}'.format(result))

  def _roundAddGame(self):
    if self._round_id is None:
      raise InputException( 'Golf round not created')
    if len(self.lstCmd) < 2:
      raise InputException( 'Not enough arguments for %s command' % self.lstCmd[0] )
    game_type = self.lstCmd[1]

    dct = {}
    for arg in self.lstCmd[2:]:
      lst = arg.split('=')
      if len(lst) == 2:
        dct[lst[0]] = lst[1]

    # get round
    doc_round = Round.objects(id=self._round_id).first()
    golf_round = DRound(doc_round)
    doc_game = Game(game_type=game_type, options=dct)
    doc_round.games.append(doc_game)
    doc_round.save()

  def _roundStart(self):
    if self._round_id is None:
      raise InputException( 'Golf round not created')
    # get round
    doc_round = Round.objects(id=self._round_id).first()
    golf_round = DRound(doc_round)
    golf_round.update_games()
    self._roundDump(golf_round)

  def _roundDump(self, golf_round=None):
    """ dump scorecard, leaderboard, status."""
    # get round
    if not golf_round:
      doc_round = Round.objects(id=self._round_id).first()
      golf_round = DRound(doc_round)
    # dumps
    self._roundScorecard(golf_round)
    self._roundLeaderboard(golf_round)
    self._roundStatus(golf_round)

  def _roundScorecard(self, golf_round):
    dct = golf_round.getScorecard(ESC=True)
    print(dct['title'])
    print(dct['hdr'])
    print(dct['par'])
    print(dct['hdcp'])
    for game in golf_round.games:
      #dct = game.getScorecard()
      dct = game.doc.scorecard
      print(dct['header'])
      for player in dct['players']:
        print(player['line'])

  def _roundLeaderboard(self, golf_round, **kwargs):
    length = 22
    lstLines = [None for _ in range(10)]
    def update_line(index, msg):
      if lstLines[index] is None:
        lstLines[index] = '{:<22}'.format(msg)
      else:
        lstLines[index] += ' {:<22}'.format(msg)

    header = '{0:-^22}' if kwargs.get('sort_type') == 'money' else '{0:*^22}'
    for game in golf_round.games:
      dctLeaderboard = game.doc.leaderboard
      update_line(0, header.format(' '+ game.short_description+ ' '))
      update_line(1, dctLeaderboard['hdr'])
      for i,dct in enumerate(dctLeaderboard['leaderboard']):
        update_line(i+2, dct['line'])
    for line in [line for line in lstLines if line is not None]:
      print(line)

  def _roundStatus(self, golf_round):
    for game in golf_round.games:
      dctStatus = game.doc.status
      print('{:<15} - {}'.format(game.short_description, dctStatus['line']))

  def _roundScore(self):
    """ gas <hole> gross=<list> [pause=enable]"""
    
    def addScore(gr):
      if hole < 1 or hole > len(gr.course.holes):
        raise GolfException('hole number must be in 1-{}'.format(len(gr.course.holes)))
      if len(lstGross) != len(gr.results):
        raise GolfException('gross scores do not match number of players')
      if lstPutts and len(lstPutts) != len(gr.results):
        raise GolfException('putts do not match number of players')
      # update scores
      for n,result in enumerate(gr.results):
        score = Score(num=hole, gross=lstGross[n])
        if lstPutts:
          score = Score(num=hole, gross=lstGross[n], putts=lstPutts[n])
        else:
          score = Score(num=hole, gross=lstGross[n])
        result.scores.append(score)
        result.save()
      #print('dct_scores:{}'.format(dct_scores))
      if options:
        for game in gr.games:
          if game.game_type in options:
            game.hole_data[hole] = options[game.game_type]

     # start here    
    if self._round_id is None:
      raise InputException( 'Golf round not created')
    if len(self.lstCmd) < 3:
      raise InputException( 'Not enough arguments for %s command' % self.lstCmd[0] )
    hole = int(self.lstCmd[1])
    pause_command = 'pause'
    lstGross, lstPutts = None, None
    options = {}
    for arg in self.lstCmd[2:]:
      lst = arg.split('=')
      if lst[0] == 'gross':
        lstGross = eval(lst[1])
      elif lst[0] == 'putts':
        lstPutts = eval(lst[1])
      elif lst[0] in ('greenie','snake'):
        options[lst[0]] = eval(lst[1])
      elif lst[0] == 'pause':
        pause_command += ' '+ lst[1]
      else:
        raise InputException('Unknown argument {}'.format(arg))
    if lstGross is None:
      raise InputException('gross must be set with gas command.')
    #
    # get round
    doc_round = Round.objects(id=self._round_id).first()
    addScore(doc_round)

    golf_round = DRound(doc_round)
    golf_round.update_games()
    golf_round.save()
    #lst_game_more_info_needed = []
    #golf_round = session.query(Round).filter(Round.round_id == self._round_id).one()
    #for game in golf_round.games:
      #try:
        #game.CreateGame()
      #except GolfGameException as ex:
        #print('{} Game - {} - {}'.format(ex.dct['game'].short_description, ex.dct['msg'], ','.join([pl.nick_name for pl in ex.dct['players']])))
        #lst_game_more_info_needed.append(ex)
      
    #if lst_game_more_info_needed:
      #for ex in lst_game_more_info_needed:
        #prompt = '{} Game - {} - {} : '.format(ex.dct['game'].short_description, ex.dct['msg'], ','.join(['{} : {}'.format(n, pl.nick_name) for n,pl in enumerate(ex.dct['players'])]))
        
        #i = raw_input(prompt)
        #if i == 'x':
          #raise Exception('Abort by user')
        #i = int(i)
        #game = session.query(Game).filter(Game.game_id == ex.dct['game'].game.game_id).one()
        #game.add_hole_dict_data(ex.dct['hole_num'], {ex.dct['key'] : ex.dct['players'][i].nick_name})
        #session.commit()

    self._roundDump(golf_round)
    self.pushCommands([pause_command])

  def _roundRetrieve(self):
    for n,doc in enumerate(Round.objects):
      ro = DRound(doc)
      print('  {:>3} {}'.format(n,ro))

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
