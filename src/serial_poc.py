from libs.utils import SerialMonitor


if __name__ == "__main__":
	serialMonitor = SerialMonitor()
	# serialMonitor.setBoard('bt328')
	serialMonitor.setBoard('uno')
	# serialMonitor.parseBoardSettings('/home/irene-sanz/repos/web2board/res/boards.txt')