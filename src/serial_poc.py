# from libs.utils import SerialMonitor
from libs.utils import Web2board
from time import sleep

if __name__ == "__main__":
	# serialMonitor = SerialMonitor()
	# serialMonitor.setBoard('bt328')
	# serialMonitor.setBoard('uno')
	# serialMonitor.parseBoardSettings('/home/irene-sanz/repos/web2board/res/boards.txt')
	# -------------------------------

	a = Web2board()

	a.setBoard('bt328')
	# sleep(3)
	# a.upload('void setup(){}void loop(){}')
