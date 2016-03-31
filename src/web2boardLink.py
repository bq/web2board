import logging
import os
import shutil
import time
from Tkinter import *
from threading import Thread
from tkMessageBox import showwarning
from ttk import *

import libs.utils as utils
from libs.Decorators.Asynchronous import asynchronous
from libs.PathsManager import PathsManager


def startLogger():
    fileHandler = logging.FileHandler(PathsManager.getHomePath() + os.sep + "web2boardLink.log", 'a')
    fileHandler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fileHandler.setFormatter(formatter)
    log = logging.getLogger()
    log.addHandler(fileHandler)
    log.setLevel(logging.DEBUG)

if utils.areWeFrozen():
    os.chdir(os.path.join(PathsManager.MAIN_PATH, "web2board"))
    PathsManager.setAllConstants()

msgBox = None
startLogger()
log = logging.getLogger(__name__)
log.info("starting")
web2boardPath = os.path.join(PathsManager.PROGRAM_PATH, "web2board" + utils.getOsExecutableExtension())
WATCHDOG_TIME = 60

PathsManager.RES_PATH = os.path.join(PathsManager.MAIN_PATH, 'res')
PathsManager.RES_ICO_PATH = os.path.join(PathsManager.RES_PATH, 'Web2board.ico')
PathsManager.RES_ICONS_PATH = os.path.join(PathsManager.RES_PATH, 'icons')

@asynchronous()
def factoryReset():
    global msgBox
    try:
        time.sleep(1)
        startWatchdog()
        logMessage("deleting web2board in: {}".format(PathsManager.PROGRAM_PATH))
        if os.path.exists(PathsManager.PROGRAM_PATH):
            shutil.rmtree(PathsManager.PROGRAM_PATH)
        logMessage("Extracting web2board...")
        shutil.copytree(utils.getModulePath() + os.sep + "web2board", PathsManager.PROGRAM_PATH)
        msgBox.endSuccessful()
    except Exception as e:
        log.exception("Failed performing Factory reset")
        msgBox.endError(str(e))


@asynchronous()
def startWatchdog():
    global msgBox
    timePassed = 0
    while not msgBox.taskEnded and timePassed < WATCHDOG_TIME:
        time.sleep(0.3)
        timePassed += 0.3
    if timePassed >= WATCHDOG_TIME:
        msgBox.endError()


def isFactoryReset():
    return len(sys.argv) > 1 and (sys.argv[1].lower() == "factoryreset" or sys.argv[1].lower() == "--factoryreset")


def logMessage(message):
    global msgBox
    log.info(message)
    msgBox.setMessage(message)


def startDialog():
    global msgBox
    class Application(Frame):
        MESSAGE_TEMPLATE = "Web2board is configuring some files.\nThis can takes a couple of minutes but it will be done just once.\n\n{}"
        def __init__(self, parent):
            Frame.__init__(self,parent)
            parent.minsize(width=500, height=0)
            self.frame = Frame(self)
            self.num = 0
            self.parent = parent
            self.gif = Label(self.frame)
            self.okButton = Button(self, text="OK")
            self.closeButton = Button(self, text="Close", command=self.close)
            self.message = Label(self.frame, text=self.MESSAGE_TEMPLATE.format(""))
            self.parent.title("Web2board launcher")
            self.style = Style()
            self.style.theme_use("default")
            root.protocol("WM_DELETE_WINDOW", self.close)
            self.messages = []

            self.taskEnded=False
            self.successfullyEnded = False

            self.create_widgets()
            self.updateMessage()

        def create_widgets(self):
            self.frame.pack(fill=BOTH, expand=True)
            self.pack(fill=BOTH, expand=True)
            self.message.pack(side=LEFT, padx=10)
            self.gif.pack(side=RIGHT, padx=5)
            self.closeButton.pack(side=RIGHT, padx=5, pady=5)
            self.okButton.pack(side=RIGHT)

            Thread(target=self.animate).start()

        def setMessage(self, message):
            self.messages.append(message)

        def updateMessage(self):
            for m in self.messages:
                self.message.configure(text=m)
            self.messages = []

            self.after(100, self.updateMessage)

        def animate(self):
            icon = PathsManager.RES_ICONS_PATH + os.sep
            try:
                if not self.taskEnded:
                    icon += "loading.gif"
                    img = PhotoImage(file=icon, format="gif - {}".format(self.num))
                elif self.successfullyEnded:
                    icon += "success.png"
                    img = PhotoImage(file=icon)
                else:
                    icon += "error.png"
                    img = PhotoImage(file=icon)

                self.gif.config(image=img)
                self.gif.image=img
                self.num += 1
            except TclError as e:
                self.num = 0
            except Exception as e:
                print e
            finally:
                self.after(70, self.animate)


        def close(self):
            if self.taskEnded:
                self.parent.destroy()
                return
            quit_msg = "It is not possible to quit while configuring files\nThis task can take up to {} seconds"
            showwarning('Warning!', quit_msg.format(WATCHDOG_TIME))

        def endSuccessful(self):
            self.taskEnded = True
            # self.ui.close.setEnabled(True)
            self.successfullyEnded = True
            self.closeButton.configure(state=DISABLED)
            self.okButton.configure(text="Start Web2Board", command=self.close, state=NORMAL)
            self.setMessage("Web2board successfully configured")

        def endError(self, error):
            self.taskEnded = True
            self.setMessage("Failed to configure web2board due to:\n{}.\n\nplease try again later or check log.".format(error))
            self.closeButton.configure(state=NORMAL)
            self.okButton.configure(text="Try again", command=self.retry, state=NORMAL)

        def retry(self):
            self.taskEnded = False
            self.closeButton.configure(state=DISABLED)
            self.okButton.configure(state=DISABLED)
            factoryReset()


    root = Tk()
    try:
        root.iconbitmap(PathsManager.RES_ICO_PATH)
    except:
        pass
    msgBox = Application(root)
    return root

if __name__ == '__main__':
    global msgBox
    try:
        log.info("web2boardPath: {}".format(web2boardPath))
        utils.killProcess("web2board")
        if isFactoryReset() or not os.path.exists(PathsManager.PROGRAM_PATH):
            app = startDialog()
            task = factoryReset()
            app.mainloop()

        if msgBox is None or msgBox.successfullyEnded:
            utils.openFile(web2boardPath)
    except:
        log.exception("Unable to launch web2board")
        raise
