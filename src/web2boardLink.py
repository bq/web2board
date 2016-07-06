import logging
import os
import shutil
import time
from Tkinter import *
from threading import Thread
from tkMessageBox import showwarning
from ttk import *
from os.path import join

import libs.utils as utils
from libs.Decorators.Asynchronous import asynchronous
from libs.PathsManager import PathsManager as pm
from libs.AppVersion import AppVersion
from libs.Updaters.Web2boardUpdater import Web2BoardUpdater, UpdaterError
import subprocess


msg_box = None
web2board_path = join(pm.get_external_data_folder(), "web2board" + utils.get_executable_extension())  # default value
log = logging.getLogger(__name__)
WATCHDOG_TIME = 60


def move_paths_manager_to_internal_web2board_path():  # any better name will be appreciated ;)
    if utils.are_we_frozen():
        os.chdir(join(pm.MAIN_PATH, "web2board"))
        pm.set_all_constants()


def get_web2board_dir_path():
    return os.path.dirname(web2board_path)


def start_logger():
    global log
    file_handler = logging.FileHandler(join(get_web2board_dir_path(), os.pardir, ".web2boardLink.log"), 'a')
    file_handler.setLevel(logging.DEBUG)
    file_handler.name = "linkLog"
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)
    log = logging.getLogger(__name__)


def is_factory_reset():
    return len(sys.argv) > 1 and (sys.argv[1].lower() == "factoryreset" or sys.argv[1].lower() == "--factoryreset")


def needs_factory_reset():
    if not os.path.exists(get_web2board_dir_path()):
        return True
    AppVersion.read_version_values()
    installer_version = AppVersion.web2board
    main_to_version_path = os.path.relpath(pm.VERSION_PATH, pm.MAIN_PATH)
    pm.VERSION_PATH = join(get_web2board_dir_path(), main_to_version_path)
    if not os.path.exists(pm.VERSION_PATH):
        return True
    AppVersion.read_version_values()
    current_version = AppVersion.web2board
    if current_version != installer_version:
        return True
    return False

def _create_startup_shortcut():
    import winshell
    from win32com.client import Dispatch
    path = os.path.join(winshell.startup(), "web2boardLink.lnk")

    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(path)
    shortcut.Targetpath = sys._MEIPASS
    shortcut.WorkingDirectory = get_web2board_dir_path()
    shortcut.IconLocation = pm.RES_ICO_PATH
    shortcut.save()


@asynchronous()
def factory_reset_process():
    global msg_box
    try:
        time.sleep(1)
        log_message("deleting web2board in: {}".format(get_web2board_dir_path()))
        if os.path.exists(get_web2board_dir_path()):
            utils.remove_folder(get_web2board_dir_path())
        log_message("Extracting web2board...")
        shutil.copytree(os.getcwd(), get_web2board_dir_path())
        msg_box.end_successful()

        if utils.is_windows():
            _create_startup_shortcut()

    except Exception as e:
        log.exception("Failed performing Factory reset")
        msg_box.end_error(str(e))


def perform_factory_reset_if_needed():
    if is_factory_reset() or needs_factory_reset():
        Web2BoardUpdater().clear_new_versions()
        app = start_dialog()
        factory_reset_process()
        app.mainloop()


def update_if_necessary():
    global msg_box
    w2b_updater = Web2BoardUpdater()

    def handle_result(f):
        try:
            f.result()
            w2b_updater.clear_new_versions()
            msg_box.end_successful()
        except UpdaterError as e:
            msg_box.end_successful(str(e))

    new_version = w2b_updater.get_new_downloaded_version()
    if new_version is not None:
        app = start_dialog()
        time.sleep(1)
        log_message("updating web2board to version: {}".format(new_version))
        future = w2b_updater.update(new_version, get_web2board_dir_path())
        future.add_done_callback(handle_result)
        app.mainloop()


@asynchronous()
def start_watchdog():
    global msg_box
    time_passed = 0
    while not msg_box.taskEnded and time_passed < WATCHDOG_TIME:
        time.sleep(0.3)
        time_passed += 0.3
    if time_passed >= WATCHDOG_TIME:
        msg_box.end_error("watchdog error")


def should_start_app():
    return len(sys.argv) <= 2 or (sys.argv[2].lower() != "nostartapp" and sys.argv[2].lower() != "--nostartapp")


def log_message(message):
    global msg_box
    log.info(message)
    msg_box.set_message(message)


def start_dialog():
    global msg_box

    class Application(Frame):
        MESSAGE_TEMPLATE = """"Web2board is setting up some files.
This can takes a couple of minutes but it will be executed just once.

{}"""
        ERROR_TEMPLATE = """Failed to configure web2board due to:
{}.

please try again later or check log."""

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
                self.message.configure(text=self.MESSAGE_TEMPLATE.format(m))
            self.messages = []

            self.after(100, self.update_message)

        def animate(self):
            icon = pm.RES_ICONS_PATH + os.sep
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
            except TclError:
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
            self.set_message("Web2board successfully configured\nWeb2board will start in a moment")
            self.after(1000, self.close)

        def end_error(self, error):
            self.task_ended = True
            self.set_message(self.ERROR_TEMPLATE.format(error))
            self.close_button.configure(state=NORMAL)
            self.ok_button.configure(text="Try again", command=self.retry, state=NORMAL)

        def retry(self):
            self.task_ended = False
            self.close_button.configure(state=DISABLED)
            self.ok_button.configure(state=DISABLED)
            factory_reset_process()

    root = Tk()
    try:
        root.iconbitmap(pm.RES_ICO_PATH)
    except:
        pass
    msg_box = Application(root)
    start_watchdog()
    return root


def set_w2b_path():
    global web2board_path
    w2b_redirection_path = join(os.getcwd(), os.pardir, "web2board_path.txt")
    if os.path.exists(w2b_redirection_path):
        with open(w2b_redirection_path) as f:
            new_direction_path = f.read().strip().decode('utf-8').encode(sys.getfilesystemencoding())
        if not os.path.isdir(new_direction_path):
            raise RuntimeError("{} not found, using default".format(new_direction_path))
        else:
            web2board_path = join(new_direction_path, "web2board" + utils.get_executable_extension())


def main():
    try:
        move_paths_manager_to_internal_web2board_path()
        log.info("starting")
        try:
            set_w2b_path()
            start_logger()
        except:
            start_logger()  # starting logger in default
            log.exception("Unable to get custom web2board path")

        pm.RES_PATH = join(pm.MAIN_PATH, 'res')
        pm.RES_ICO_PATH = join(pm.RES_PATH, 'Web2board.ico')
        pm.RES_ICONS_PATH = join(pm.RES_PATH, 'icons')

        log.info("web2boardPath: %s", web2board_path)
        utils.kill_process("web2board")

        perform_factory_reset_if_needed()
        update_if_necessary()

        if should_start_app() and (msg_box is None or msg_box.successfully_ended):
            if is_factory_reset():
                sys.argv.pop(1)
            if not utils.is_windows():
                subprocess.call(['chmod', '0777', web2board_path])
            utils.open_file(web2board_path)
    except:
        log.exception("Unable to launch web2board")
        raise


if __name__ == '__main__':
    main()
