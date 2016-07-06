import json
from optparse import OptionParser

import sys

from libs.CompilerUploader import CompilerUploader
from libs.PathsManager import PathsManager as pm


def parse_args():
    parser = OptionParser(usage="usage: %prog [options] filename", version="%prog 1.0")
    parser.add_option("--board", default='bt328', type='string', action="store", dest="board",
                      help="hostname (localhost)")
    parser.add_option("--port", default=None, type='string', action="store", dest="port",
                      help="port (9876)")
    parser.add_option("--upload", action="store_true", dest="upload", help="communication through console")
    parser.add_option("--workSpace", default=pm.PLATFORMIO_WORKSPACE_PATH, type='string', action="store",
                      dest="work_space", help="board connected for integration tests")
    return parser.parse_args()


def run():
    options, args = parse_args()
    c = CompilerUploader.construct(options.board)
    result = c.platformio_run(work_space=options.work_space, upload=options.upload,
                              upload_port=options.port)
    sys.stdout.write("###RESULT###")
    sys.stdout.write(json.dumps(result))

if __name__ == '__main__':
    run()