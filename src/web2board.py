import signal, sys, ssl, logging
from libs.SimpleWebSocketServer import WebSocket, SimpleWebSocketServer, SimpleSSLWebSocketServer
from optparse import OptionParser
from libs.utils import Web2board
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)

web2board = Web2board()

class messageHandler (WebSocket):
   # def __init__(self):
   #    print 'aaa'

   def sendMessage_(self,message):
      try:
         self.sendMessage(message);
      except Exception as n:
         print n

   def handleMessage(self):
      if self.data is None:
         self.data = ''

      # print 'self.data.find(self.data, 0,len(self.data))',self.data.find('write', 0,len(self.data))
      if self.data.find('setBoard', 0,len(self.data))>=0:
         message = self.data.replace('setBoard','')
         message = message.replace(' ', '') #remove white spaces that make the command readable
         self.sendMessage_('SETTING BOARD')
         port = web2board.setBoard(str(message))
         if port != None:
            self.sendMessage_('SETTING PORT : '+port)
         else :
            self.sendMessage_('NO PORT FOUND')
      if self.data == 'open':
         self.sendMessage_('OPENNING PORT')
         web2board.openSerialPort()
      if self.data == 'close':
         self.sendMessage_('CLOSING PORT')
         web2board.closeSerialPort()
      if self.data.find('write', 0,len(self.data))>=0: #self.data == 'write':
         message = self.data.replace('write','')
         print 'serial Writting :', message
         web2board.writeSerialPort(message)
      if self.data == 'read':
         self.sendMessage_(web2board.readSerialPort())
      if self.data.find('compile', 0,len(self.data))>=0:
         message = self.data.replace('compile','')
         message = message.replace(' ', '') #remove white spaces that make the command readable
         self.sendMessage_('COMPILING ...')
         web2board.compile(message)

   def handleConnected(self):
      print self.address, 'connected'

   def handleClose(self):
      print self.address, 'closed'


if __name__ == "__main__":

   parser = OptionParser(usage="usage: %prog [options]", version="%prog 1.0")
   parser.add_option("--host", default='', type='string', action="store", dest="host", help="hostname (localhost)")
   parser.add_option("--port", default=8000, type='int', action="store", dest="port", help="port (8000)")
   parser.add_option("--example", default='echo', type='string', action="store", dest="example", help="echo, chat")
   parser.add_option("--ssl", default=0, type='int', action="store", dest="ssl", help="ssl (1: on, 0: off (default))")
   parser.add_option("--cert", default='./cert.pem', type='string', action="store", dest="cert", help="cert (./cert.pem)")
   parser.add_option("--ver", default=ssl.PROTOCOL_TLSv1, type=int, action="store", dest="ver", help="ssl version")
   
   (options, args) = parser.parse_args()

   cls = messageHandler
   # if options.example == 'chat':
   #    cls = SimpleChat	

   if options.ssl == 1:
      server = SimpleSSLWebSocketServer(options.host, options.port, cls, options.cert, options.cert, version=options.ver)
   else:	
      server = SimpleWebSocketServer(options.host, options.port, cls)

   def close_sig_handler(signal, frame):
      server.close()
      sys.exit()

   signal.signal(signal.SIGINT, close_sig_handler)

   server.serveforever()
