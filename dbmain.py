#!/usr/bin/env python3
"""dbmain.py"""
import logging
import threading

from util.menu import MenuItem, Menu, InputException, FileInput
from util.tl_logger import TLLog,logOption

from mongoengine import connect

TLLog.config('logs/dbmain.log', defLogLevel=logging.INFO )

log = TLLog.getLogger('dbmain')

def main():
  DEF_LOG_ENABLE = 'dbmain'
  DEF_DATABASE = 'golfdata'
  # build the command line arguments
  from argparse import ArgumentParser
  parser = ArgumentParser()
  parser.add_option( "-m",  "--logEnable", dest="lstLogEnable", default=DEF_LOG_ENABLE,
                     help='Comma separated list of log modules to enable, * for all. Default is "%s"' % DEF_LOG_ENABLE)
  parser.add_option( "-g",  "--showLogs", action="store_true", dest="showLogs", default=False,
                     help='list all log options.' )
  parser.add_option( "-y",  "--runCmdFile", dest="cmdFile", default=None,
                     help="Run a command file at startup.")

  #  parse the command line and set values
  (options, args) = parser.parse_args()

  master = None
  try:
    # set the main thread name
    thrd = threading.currentThread()
    thrd.setName( 'dbmain' )

    log.info(80*"*")
    log.info( 'dbmain - starting' )
    logOptions(options.lstLogEnable, options.showLogs, log=log)

    # create menu application 
    #menu = SQLMenu(url=options.url, cmdFile=options.cmdFile)
    #menu.runMenu()

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
#  connect('golfdata')