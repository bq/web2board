#!/usr/bin/python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------#
#                                                                       #
# This file is part of the web2board project                            #
#                                                                       #
# Copyright (C) 2015 Mundo Reader S.L.                                  #
#                                                                       #
# Date: April - May 2015                                                #
# Authors: Irene Sanz Nieto <irene.sanz@bq.com>,                        #
#          Sergio Morcuende <sergio.morcuende@bq.com>                   #
#                                                                       #
#-----------------------------------------------------------------------#

import signal, sys, ssl, logging
from libs.SimpleWebSocketServer import WebSocket, SimpleWebSocketServer, SimpleSSLWebSocketServer
from optparse import OptionParser
from libs.CompilerUploader import CompilerUploader
import json
import subprocess

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)

compilerUploader = CompilerUploader()

class messageHandler (WebSocket):
   def sendMessage_(self,message):
      try:
         self.sendMessage(message);
      except Exception as n:
         print n

   def handleMessage(self):
      if self.data is None:
         self.data = ''
      if 'version' in self.data:
         self.sendMessage_('VERSION '+compilerUploader.getVersion())
      elif 'setBoard' in self.data:
         try:
            self.proc.terminate()
         except:
            print 'No SerialMonitor process found'
         message = self.data.replace('setBoard','')
         message = message.replace(' ', '') #remove white spaces that make the command readable
         self.sendMessage_('SETTING BOARD')
         port = compilerUploader.setBoard(str(message))
         if port != None and type(port)!= type([]):
            self.sendMessage_('SETTING PORT -> '+port)
         elif type(port)==type([]):
            self.sendMessage_('SETTING PORT -> '+json.dumps(port))
         else :
            self.sendMessage_('NO PORT FOUND')
         print('setBoard finished', json.dumps(port))
      elif 'setPort' in self.data:
         message = self.data.replace('setPort','').replace(' ','')
         compilerUploader.setPort(message)
         self.sendMessage_('SETTED PORT '+str(compilerUploader.getPort()))
      elif 'compile' in self.data:
         message = str(self.data.replace('compile',''))
         self.sendMessage_('COMPILING')
         report = compilerUploader.compile(message)
         self.sendMessage_('COMPILED -> '+json.dumps(report))
      elif 'upload' in self.data:
         try:
            self.proc.terminate()
         except:
            print 'No SerialMonitor process found'
         print('uploading!')
         message = str(self.data.replace('upload',''))
         self.sendMessage_('UPLOADING')
         report= compilerUploader.upload(message)
         self.sendMessage_('UPLOADED -> '+json.dumps(report))
      elif 'SerialMonitor' in self.data:
         message = str(self.data.replace('SerialMonitor','').replace(' ',''))
         self.proc = subprocess.Popen(['python', sys.path[0]+'/SerialMonitor.py', message], shell=False)
      elif self.data == 'exit':
         sys.exit()

   def handleConnected(self):
      print self.address, 'connected'

   def handleClose(self):
      print self.address, 'closed'


if __name__ == "__main__":

   parser = OptionParser(usage="usage: %prog [options]", version="%prog 1.0")
   parser.add_option("--host", default='', type='string', action="store", dest="host", help="hostname (localhost)")
   parser.add_option("--port", default=9876, type='int', action="store", dest="port", help="port (9876)")
   parser.add_option("--example", default='echo', type='string', action="store", dest="example", help="echo, chat")
   parser.add_option("--ssl", default=0, type='int', action="store", dest="ssl", help="ssl (1: on, 0: off (default))")
   parser.add_option("--cert", default='./cert.pem', type='string', action="store", dest="cert", help="cert (./cert.pem)")
   parser.add_option("--ver", default=ssl.PROTOCOL_TLSv1, type=int, action="store", dest="ver", help="ssl version")
   
   (options, args) = parser.parse_args()

   cls = messageHandler

   if options.ssl == 1:
      server = SimpleSSLWebSocketServer(options.host, options.port, cls, options.cert, options.cert, version=options.ver)
   else:	
      server = SimpleWebSocketServer(options.host, options.port, cls)

   def close_sig_handler(signal, frame):
      server.close()
      sys.exit()

   signal.signal(signal.SIGINT, close_sig_handler)
   server.serveforever()
