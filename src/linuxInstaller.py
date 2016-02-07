#!/usr/bin/env python
# coding=utf-8
import subprocess
import pwd
import logging

def startLogger(self):
        fileHandler = logging.FileHandler("/opt/web2board/error.log", 'a')
        fileHandler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fileHandler.setFormatter(formatter)
        self.log = logging.getLogger()
        self.log.addHandler(fileHandler)
        self.log.setLevel(logging.DEBUG)

def addAllUsersToDialOut():
    allUsers = [p[0] for p in pwd.getpwall()]
    for user in allUsers:
        subprocess.call(["sudo", "adduser", user, "dialout"])


if __name__ == '__main__':
    startLogger()
    addAllUsersToDialOut()