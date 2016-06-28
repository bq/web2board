#!/usr/bin/env python
import inspect
import os
import sys
import unittest

import glob2


def get_module_path():
    frame = inspect.currentframe().f_back
    info = inspect.getframeinfo(frame)
    file_name = info.filename
    return os.path.dirname(os.path.abspath(file_name))


def get_ws_relative_route(file_path):
    relative_path = file_path.split(os.path.join("web2board", "src", ""), 1)[1]  # todo: use generic path
    return relative_path.split(os.sep)


def __get_suites(tests_path):
    path = get_module_path()
    tests_path = os.path.abspath(os.path.join(path, os.path.pardir, tests_path))
    test_files = glob2.glob(tests_path)
    relative_test_files = [get_ws_relative_route(test_file) for test_file in test_files]
    module_strings = [".".join(test_file)[:-3] for test_file in relative_test_files]
    print module_strings
    for t in module_strings:
        try:
            unittest.defaultTestLoader.loadTestsFromName(t)
            print t, 'good'
        except Exception as e:
            print t, str(e)
    return [unittest.defaultTestLoader.loadTestsFromName(test_file) for test_file in module_strings]


def __run_test(suite, report_title="report"):
    from Test.HTMLTestRunner import HTMLTestRunner
    from libs.PathsManager import PathsManager
    report_path = PathsManager.RES_PATH + os.sep + report_title + '.html'
    runner = HTMLTestRunner(stream=file(report_path, 'wb'), title=" Web2Board " + report_title, verbosity=1)
    runner.run(suite)


def run_unit_test():
    suite = unittest.TestSuite(__get_suites('Test/unit/**/test*.py'))
    __run_test(suite)


def run_integration_test():
    suite = unittest.TestSuite(__get_suites('Test/integration/**/test*.py'))
    __run_test(suite)


def run_all_test():
    suite = unittest.TestSuite(__get_suites('Test/**/test*.py'))
    __run_test(suite)


if __name__ == '__main__':
    try:
        if len(sys.argv) <= 1:
            run_unit_test()
        else:
            testing = sys.argv[1]
            if testing == "unit":
                run_unit_test()
            elif testing == "integration":
                run_integration_test()
            elif testing == "all":
                run_all_test()
    except:
        raise
    finally:
        os._exit(0)
