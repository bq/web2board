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

import signal, sys, ssl, logging, os, platform
from libs.SimpleWebSocketServer import WebSocket, SimpleWebSocketServer, SimpleSSLWebSocketServer
from optparse import OptionParser
from libs.CompilerUploader import CompilerUploader
import json
import subprocess
from os.path import expanduser
from distutils.dir_util import mkpath
import zipfile


logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)

compilerUploader = CompilerUploader()

def getBitbloqLibsVersion():
      # Get bitbloqLibs version from config file
   pathToMain = sys.path[0]
   if platform.system() == 'Darwin':
      if os.environ.get('PYTHONPATH') != None:
         pathToMain = os.environ.get('PYTHONPATH')

   with open(pathToMain+'/res/config.json') as json_data_file:
      data = json.load(json_data_file)
      version = str(data['bitbloqLibsVersion'])
      # print version
   return version

def setBitbloqLibsVersion(newVersion):
   pathToMain = sys.path[0]
   if platform.system() == 'Darwin':
      if os.environ.get('PYTHONPATH') != None:
         pathToMain = os.environ.get('PYTHONPATH')

   jsonFile = open(pathToMain+'/res/config.json', "r")
   data = json.load(jsonFile)
   jsonFile.close()

   data["bitbloqLibsVersion"] = newVersion

   jsonFile = open(pathToMain+'/res/config.json', "w+")
   jsonFile.write(json.dumps(data))
   jsonFile.close()

from urllib2 import urlopen, URLError, HTTPError


def dlfile(url, path='.'):
    # Open the url
    try:
        f = urlopen(url)
        print "downloading " + url

        # Open our local file for writing
        print os.path.basename(url),expanduser("~")
        with open(expanduser("~")+'/'+os.path.basename(url), "wb") as local_file:
            local_file.write(f.read())

    #handle errors
    except HTTPError, e:
        print "HTTP Error:", e.code, url
    except URLError, e:
        print "URL Error:", e.reason, url

def downloadLibs ():

      # Select Sketchbook folder depending on OS
   if platform.system() == 'Linux':
      pathToSketchbook = expanduser("~").decode('latin1')+'/Arduino/libraries'
   elif platform.system() == 'Windows' or platform.system() == 'Darwin':
      pathToSketchbook = expanduser("~").decode('latin1')+'/Documents/Arduino/libraries'

   # If there is something inside bitbloqLibs
   if  os.path.exists(pathToSketchbook+'/bitbloqLibs')  and os.listdir(pathToSketchbook+'/bitbloqLibs'):
      import shutil
      shutil.rmtree(pathToSketchbook+'/bitbloqLibs')

   version = getBitbloqLibsVersion()
   print ('Downloading new libs, version', version)

   # Download bitbloqLibs
   url = ('https://github.com/bq/bitbloqLibs/archive/v'+version+'.zip')
   dlfile(url)

   # Extract it to the correct dir
   with zipfile.ZipFile(expanduser("~")+'/'+'v'+version+'.zip', "r") as z:
       z.extractall(pathToSketchbook)
   # Rename folder 
   os.rename(pathToSketchbook+'/bitbloqLibs-'+version, pathToSketchbook+'/bitbloqLibs')
   # Remove .zip
   try:
       os.remove(expanduser("~")+'/'+'v'+version+'.zip')
   except OSError:
       pass



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
         self.sendMessage_('VERSION -> '+compilerUploader.getVersion())
      elif 'setBoard' in self.data:
         try:
            self.proc.terminate()
         except:
            print 'No SerialMonitor process found'
         message = self.data.replace('setBoard','')
         message = message.replace(' ', '') #remove white spaces that make the command readable
         if message == 'undefined':
            self.sendMessage_('BOARD UNDEFINED')
         else:
            self.sendMessage_('SETTING BOARD')
            port = compilerUploader.setBoard(str(message))
            if len(port)>0:
               self.sendMessage_('SETTING PORT -> '+json.dumps(port))
            else :
               self.sendMessage_('NO PORT FOUND')
      elif 'setPort' in self.data:
         message = self.data.replace('setPort','').replace(' ','')
         compilerUploader.setPort(message)
         self.sendMessage_('SETTED PORT '+str(compilerUploader.getPort()))
      elif 'compile' in self.data:
         message = str(self.data.replace('compile',''))
         self.sendMessage_('COMPILING')
         report = compilerUploader.compile(message)
         self.sendMessage_('COMPILED -> '+json.dumps(report))
      elif 'setBitbloqLibsVersion' in self.data:
         message = str(self.data.replace('setBitbloqLibsVersion','').replace(' ',''))
         print getBitbloqLibsVersion() != message, getBitbloqLibsVersion() , message
         if getBitbloqLibsVersion() != message:
            setBitbloqLibsVersion(message)
            self.sendMessage_('SETTED VERSION -> '+ getBitbloqLibsVersion())
            downloadLibs()
         #update bitbloqLibs if version is different!!
      elif 'getBitbloqLibsVersion' in self.data:
         self.sendMessage_(getBitbloqLibsVersion())
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
         try:
            if platform.system() == 'Darwin':
               self.proc = subprocess.Popen(['/Applications/SerialMonitor.app/Contents/MacOS/SerialMonitor', message], shell=False)
            else:
               path = sys.path[0]
               self.proc = subprocess.Popen(['python', path + '/SerialMonitor.py', message], shell=False)
            
         except:
            print "caught this"
         self.sendMessage_('SERIALMONITOROPENED')
      elif self.data == 'exit':
         sys.exit()

   def handleConnected(self):
      print self.address, 'connected'

   def handleClose(self):
      print self.address, 'closed'



if __name__ == "__main__":

   # Check if the sketchbook folder exists
   # Select Sketchbook folder depending on OS
   if platform.system() == 'Linux':
      pathToSketchbook = expanduser("~").decode('latin1')+'/Arduino/libraries'
   elif platform.system() == 'Windows' or platform.system() == 'Darwin':
      pathToSketchbook = expanduser("~").decode('latin1')+'/Documents/Arduino/libraries'

   # If there is no bitbloqLibs folder or it is empty
   if not os.path.exists(pathToSketchbook+'/bitbloqLibs') or not os.listdir(pathToSketchbook+'/bitbloqLibs'):
      mkpath(pathToSketchbook)
      downloadLibs()

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
