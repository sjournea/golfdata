""" menu.py """
import pdb, traceback, os
import datetime,time

from .tl_logger import TLLog
log = TLLog.getLogger( 'menu' )

class InputException(Exception):
  pass

class FileInput(object):
  def __init__(self, filename):
    self.filename = filename
    self._lstLines = open( self.filename, 'r').readlines()
    self._index = 0

  def getNextLine(self):
    curLine = None
    if self._index < len(self._lstLines):
      curLine = self._lstLines[ self._index ]
      self._index += 1
    return curLine

class MenuItem(object):
  lstCmds = []
  def __init__(self, cmd, command, desc, func=None):
    self.cmd = cmd
    self.command = command
    self.desc = desc
    self.func = func
    if self.cmd != '':
      assert self.cmd not in MenuItem.lstCmds, 'cmd "%s %s"  already defined' % (self.cmd,self.command)
      MenuItem.lstCmds.append( self.cmd )

class Menu(object):
  def __init__(self,cmd_file=None, menuSize=50):
    self.lstMenuItems = []
    self.header = '****'
    self.showCmds = True
    self.bRepeatCommand = False
    self.dctQuerys = {}
    self._pause_ignore = False
    self._pause_enabled = True
    self._cmd_file = None
    self._cmd_files = []
    self._cmd_stack = []
    if cmd_file is not None:
      self._cmd_file = FileInput( cmd_file )
      
    self._lstBuiltInMenuItems = [
            MenuItem( '?',  '',                        'show help'),
            MenuItem( 'x',  '',                        'exit program'),
            MenuItem( 'os', '',                        'Run OS command'),
            MenuItem( '<',  '<script file>',           'read commands from a file'),
            MenuItem( 's',  'sleep <delay>',           'sleep for delay (sec)'),
            MenuItem( '',   '<any command> --repeat',  'Adding --repeat will cause this command to be repeated'),
            MenuItem( '',   '',                        '  once a second until a key is pressrd.'),
        ]

    self._menuSize = menuSize

  def addMenuItem(self, mi):
    self.lstMenuItems.append( mi )

  def updateHeader(self):
    pass

  def preCommand(self):
    pass

  def postCommand(self):
    pass

  def shutdown(self):
    pass

  def pushCommands(self, lst_commands):
    self._cmd_stack.extend(lst_commands)

  def runMenu(self):
    while True:
      try:
        if self.showCmds: 
          self.updateHeader()
          print('\nCommands available:\t%s' % (self.header))
          lstMI = self.lstMenuItems + self._lstBuiltInMenuItems
          for mn in lstMI:
            if mn.cmd == '' and mn.command == '':
              s = self._menuSize*' '
            else:
              cnt = self._menuSize - len(mn.command)
              s   = cnt*'.'
            print('  %-3s %s  %s  %s' % (mn.cmd, mn.command, s,mn.desc))
          self.showCmds = False
          print()

        if self.bRepeatCommand:
          if kbhit():
            ch = getch()
            self.bRepeatCommand = False
          else:
            # delay one second
            time.sleep(1)
            curTime = datetime.datetime.now()
            print(curTime.strftime( '%H:%M:%S' ))

        if not self.bRepeatCommand:
          if self._cmd_stack:
            cmd = self._cmd_stack.pop(0)
          elif self._cmd_file:
            cmd = self._cmd_file.getNextLine()
            if cmd is None:
              if self._cmd_files:
                self._cmd_file = self._cmd_files.pop()
              else:
                self._cmd_file = None 
              continue
            else:
              print('Command: < %s' % cmd)
          else:    
            cmd = input( "Command: ")
          # Add support for double quotes in responses
          lst = cmd.split('"')
          if len(lst) > 1:
            # we have a double quote
            # len must be odd
            if len(lst) % 2 == 0:
              raise Exception( 'Illegal command -- mismatched double quotes')
            self.lstCmd = []
            for n,c in enumerate(lst):
              if n % 2 == 0:
                self.lstCmd.extend( lst[n].split() )
              else:
                self.lstCmd.append( lst[n] )
          else:
            self.lstCmd = cmd.split()

        if len(self.lstCmd) == 0:
          continue

        # Comments begin with '#'
        if self.lstCmd[0][0] == '#':
          continue

        # pause
        if self.lstCmd[0] == 'pause':
          if len(self.lstCmd) > 1 and self.lstCmd[1] == 'ignore':
            if self.lstCmd[2] == 'on':
              self._pause_ignore = True
            elif self.lstCmd[2] == 'off':
              self._pause_ignore = False
            continue
          if self._pause_ignore:
            continue
          if len(self.lstCmd) > 1 and self.lstCmd[1] == 'enable':
            self._pause_enabled = True
          if self._pause_enabled:
            x = input('Continue ? ')
            if x == 'x':
              self.shutdown()
              break
            if x == 'g':
              self._pause_enabled = False
          continue
            
        # exit the program                 
        if self.lstCmd[0] == 'x':
          self.shutdown()
          break

        # load commands from a file
        if self.lstCmd[0] == '<':
          # if open command file then stack
          if self._cmd_file:
            self._cmd_files.append(self._cmd_file)
          self._cmd_file = FileInput( self.lstCmd[1] )
          continue

        # OS commands
        if self.lstCmd[0] == 'os':
          # if open command file then stack
          command = ' '.join(self.lstCmd[1:])
          os.system(command)
          continue

        # show help
        if self.lstCmd[0] == '?':
          self.showCmds = True

        # sleep            
        if self.lstCmd[0] == 's':
          delay = 1.0
          if len(self.lstCmd) > 1:
            delay = float(self.lstCmd[1])
          print('Sleeping for %f sec ...' % delay)
          time.sleep(delay)
          continue

        # Check for repeat command
        if self.lstCmd[-1] == '--repeat':
          self.bRepeatCommand = True
          self.lstCmd = self.lstCmd[0:-1]

        self.preCommand()

        for mn in self.lstMenuItems:
          if self.lstCmd[0] == mn.command or self.lstCmd[0] == mn.cmd:
            mn.func()
            break
        else:
          raise InputException('Unknown command "%s"' % self.lstCmd[0])

        self.postCommand()

      except InputException as err:
        print('InputException:%s' % err)
        self.showCmds = True
        self.bRepeatCommand = False
        if self._cmd_file:
          self._cmd_file = None
        if self._cmd_files:
          self._cmd_files = []
  
      except Exception as err:
        s = '%s: %s' % (err.__class__.__name__, err)
        log.error(s)
        print(s)
        print('-- traceback --')
        traceback.print_exc()
        print()
        self.bRepeatCommand = False
        if self._cmd_file:
          self._cmd_file = None
        if self._cmd_files:
          self._cmd_files = []

