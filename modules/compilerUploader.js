//----------------------------------------------------------------//
// This file is part of the web2board Project                     //
//                                                                //
// Date: April 2015                                               //
// Author: Irene Sanz Nieto  <irene.sanz@bq.com>                  //
//----------------------------------------------------------------//
(function() {
    var exec = require('child_process').exec;
    var mkdirp = require('mkdirp');
    var fs = require('fs');

    function createEnvironment(board, port, program, callback) {
        //Create the folder if it does not exist
        mkdirp('/tmp/web2board', function(err) {
            if (err) console.error(err)
            else {
                //Once the folder is created, create the sketch file
                fs.writeFile("/tmp/web2board/sketch.ino", program.code, function(err) {
                    if (err) {
                        return console.log(err);
                    }
                    console.log("The file was saved!");
                });
                //Then, create the makeFile
                var makefileContent = "BOARD_TAG = " + board + "\n" + "ARDUINO_LIBS = \n" + "ARDUINO_PORT = " + port + "\n" + "include /usr/share/arduino/Arduino.mk";
                fs.writeFile("/tmp/web2board/Makefile", makefileContent, function(err) {
                    if (err) {
                        return console.log(err);
                    }
                    console.log("The file was saved!");
                });
                callback();
            }
        });
    };

    function compile(board, port, program) {
        createEnvironment(board, port, program, function() {
            //Finally, execute the "make" command on the given directory
            exec('make', {
                cwd: '/tmp/web2board',
            }, function(error, stdout, stderr) {
                console.log('compiling...\n');
                console.log('error:\n', error);
                console.log('stdout:\n', stdout);
                console.log('stderr:\n', stderr);
            });
        });
    };

    function upload(board, port, program) {
        createEnvironment(board, port, program, function() {
            //Finally, execute the "make" command on the given directory
            exec('make upload', {
                cwd: '/tmp/web2board',
            }, function(error, stdout, stderr) {
                console.log('uploading...\n');
                console.log('error:\n', error);
                console.log('stdout:\n', stdout);
                console.log('stderr:\n', stderr);
            });
        });
    };
    module.exports.compile = compile;
    module.exports.upload = upload;
})();
// class Compiler:
//  def __init__(self, board='bt328',port='/dev/ttyUSB0', baudRate=19200):
//      self.board = board
//      self.port = port
//      self.baudRate = baudRate
//      self.pathToMain = os.path.dirname(os.path.realpath("main.py"))
//      self.createMakefile()
//  def createMakefile(self):
//  def compile(self):
//      os.chdir("tmp")
//      call(["make"])
//  def upload(self):
//      os.chdir("tmp")
//      call(["make", "upload"])
//      self.removeTmp()
//  def removeTmp(self):
//      print 'path:', self.pathToMain
//      call(["cd", self.pathToMain+"/"])
//      call(["ls"])
//      call(["rm", "-rf", "tmp"])