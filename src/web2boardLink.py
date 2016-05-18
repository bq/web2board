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
from libs.Version import Version
import subprocess


def startLogger():
    fileHandler = logging.FileHandler(PathsManager.get_home_path() + os.sep + "web2boardLink.log", 'a')
    fileHandler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fileHandler.setFormatter(formatter)
    log = logging.getLogger()
    log.addHandler(fileHandler)
    log.setLevel(logging.DEBUG)


if utils.are_we_frozen():
    os.chdir(os.path.join(PathsManager.MAIN_PATH, "web2board"))
    PathsManager.set_all_constants()

msgBox = None
startLogger()
log = logging.getLogger(__name__)
log.info("starting")
web2boardPath = os.path.join(PathsManager.PROGRAM_PATH, "web2board" + utils.get_executable_extension())
WATCHDOG_TIME = 60

PathsManager.RES_PATH = os.path.join(PathsManager.MAIN_PATH, 'res')
PathsManager.RES_ICO_PATH = os.path.join(PathsManager.RES_PATH, 'Web2board.ico')
PathsManager.RES_ICONS_PATH = os.path.join(PathsManager.RES_PATH, 'icons')


@asynchronous()
def factory_reset():
    global msgBox
    try:
        time.sleep(1)
        start_watchdog()
        log_message("deleting web2board in: {}".format(PathsManager.PROGRAM_PATH))
        if os.path.exists(PathsManager.PROGRAM_PATH):
            shutil.rmtree(PathsManager.PROGRAM_PATH)
        log_message("Extracting web2board...")
        shutil.copytree(utils.get_module_path() + os.sep + "web2board", PathsManager.PROGRAM_PATH)
        msgBox.end_successful()
    except Exception as e:
        log.exception("Failed performing Factory reset")
        msgBox.end_error(str(e))


@asynchronous()
def start_watchdog():
    global msgBox
    timePassed = 0
    while not msgBox.taskEnded and timePassed < WATCHDOG_TIME:
        time.sleep(0.3)
        timePassed += 0.3
    if timePassed >= WATCHDOG_TIME:
        msgBox.end_error()


def is_factory_reset():
    return len(sys.argv) > 1 and (sys.argv[1].lower() == "factoryreset" or sys.argv[1].lower() == "--factoryreset")

def should_start_app():
    return len(sys.argv) <= 2 or (sys.argv[2].lower() != "nostartapp" and sys.argv[2].lower() != "--nostartapp")

def needs_factory_reset():
    if not os.path.exists(PathsManager.PROGRAM_PATH):
        return True
    Version.read_version_values()
    installer_version = Version.web2board
    main_to_version_path = os.path.relpath(PathsManager.VERSION_PATH, PathsManager.MAIN_PATH)
    PathsManager.VERSION_PATH = os.path.join(PathsManager.PROGRAM_PATH, main_to_version_path)
    if not os.path.exists(PathsManager.VERSION_PATH):
        return True
    Version.read_version_values()
    current_version = Version.web2board
    if current_version != installer_version:
        return True
    return False

def log_message(message):
    global msgBox
    log.info(message)
    msgBox.set_message(message)

def start_dialog():
    global msgBox

    class Application(Frame):
        MESSAGE_TEMPLATE = "Web2board is configuring some files.\nThis can takes a couple of minutes but it will be executed just once.\n\n{}"

        def __init__(self, parent):
            Frame.__init__(self, parent)
            parent.minsize(width=500, height=0)
            self.frame = Frame(self)
            self.num = 0
            self.parent = parent
            self.gif = Label(self.frame)
            self.ok_button = Button(self, text="OK")
            self.close_button = Button(self, text="Close", command=self.close)
            self.message = Label(self.frame, text=self.MESSAGE_TEMPLATE.format(""))
            self.parent.title("Web2board launcher")
            self.style = Style()
            self.style.theme_use("default")
            root.protocol("WM_DELETE_WINDOW", self.close)
            self.messages = []

            self.task_ended = False
            self.successfully_ended = False

            self.create_widgets()
            self.update_message()

        def create_widgets(self):
            self.frame.pack(fill=BOTH, expand=True)
            self.pack(fill=BOTH, expand=True)
            self.message.pack(side=LEFT, padx=10)
            self.gif.pack(side=RIGHT, padx=5)
            self.close_button.pack(side=RIGHT, padx=5, pady=5)
            self.ok_button.pack(side=RIGHT)

            Thread(target=self.animate).start()

        def set_message(self, message):
            self.messages.append(message)

        def update_message(self):
            for m in self.messages:
                self.message.configure(text=m)
            self.messages = []

            self.after(100, self.update_message)

        def animate(self):
            icon = PathsManager.RES_ICONS_PATH + os.sep
            try:
                if not self.task_ended:
                    icon += "loading.gif"
                    img = PhotoImage(file=icon, format="gif - {}".format(self.num))
                elif self.successfully_ended:
                    icon += "success.png"
                    img = PhotoImage(file=icon)
                else:
                    icon += "error.png"
                    img = PhotoImage(file=icon)

                self.gif.config(image=img)
                self.gif.image = img
                self.num += 1
            except TclError as e:
                self.num = 0
            except Exception as e:
                print e
            finally:
                self.after(70, self.animate)

        def close(self):
            if self.task_ended:
                self.parent.destroy()
                return
            quit_msg = "It is not possible to quit while configuring files\nThis task can take up to {} seconds"
            showwarning('Warning!', quit_msg.format(WATCHDOG_TIME))

        def end_successful(self):
            self.task_ended = True
            # self.ui.close.setEnabled(True)
            self.successfully_ended = True
            self.close_button.configure(state=DISABLED)
            self.ok_button.configure(text="Start Web2Board", command=self.close, state=NORMAL)
            self.set_message("Web2board successfully configured")
            self.after(100, self.close)

        def end_error(self, error):
            self.task_ended = True
            self.set_message(
                "Failed to configure web2board due to:\n{}.\n\nplease try again later or check log.".format(error))
            self.close_button.configure(state=NORMAL)
            self.ok_button.configure(text="Try again", command=self.retry, state=NORMAL)

        def retry(self):
            self.task_ended = False
            self.close_button.configure(state=DISABLED)
            self.ok_button.configure(state=DISABLED)
            factory_reset()

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
        utils.kill_process("web2board")
        if is_factory_reset() or needs_factory_reset():
            app = start_dialog()
            factory_reset()
            app.mainloop()

        if should_start_app() and (msgBox is None or msgBox.successfully_ended):
            if is_factory_reset():
                sys.argv.pop(1)
            if not utils.is_windows():
                subprocess.call(['chmod', '0777', web2boardPath])
            utils.open_file(web2boardPath)
    except:
        log.exception("Unable to launch web2board")
        raise
