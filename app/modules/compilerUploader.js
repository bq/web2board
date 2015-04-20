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
    var commonMakefile = '';
    fs.readFile('app/res/makefile', 'utf8', function(err, data) {
        if (err) {
            return console.log(err);
        }
        commonMakefile = data;
    });
    //Quick hack to resolve the absolute path of the app/ dir
    var appDir = __dirname.substr(0, __dirname.length - 7);
    var arduino_dir = appDir + "res/arduino-1.0.6";
    //Commands to make and make upload the sketch:
    var makeCommand = appDir + 'res/' + 'make';
    var makeUploadCommand = makeCommand + ' upload';

    function getIndicesOf(searchStr, str, caseSensitive) {
        var startIndex = 0,
            searchStrLen = searchStr.length;
        var index, indices = [];
        if (!caseSensitive) {
            str = str.toLowerCase();
            searchStr = searchStr.toLowerCase();
        }
        while ((index = str.indexOf(searchStr, startIndex)) > -1) {
            indices.push(index);
            startIndex = index + searchStrLen;
        }
        return indices;
    }

    function parseLibs(code) {
        var initIndex = getIndicesOf("#include", code, false);
        var dummy = [];
        for (var i in initIndex) {
            var finalIndex = code.indexOf(".h>", initIndex[i]);
            var a = code.substr(initIndex[i], finalIndex - initIndex[i]);
            a = a.substr(a.indexOf("<") + 1, a.length);
            dummy.push(a);
        }
        return dummy.join(' ');
    };

    function createEnvironment(data, callback) {
        //Perform operations on program.code so it compiles correctly
        var libs = parseLibs(data.code);
        var programCode = data.code;
        programCode = programCode.replace(new RegExp('\\n', 'g'), '\r\n', function() {});
        // Create the /tmp folder if it does not exist
        mkdirp('tmp', function(err) {
            if (err) console.error(err)
            else {
                //Once the folder is created, create the sketch file
                fs.writeFile("tmp/tmp.ino", programCode, function(err) {
                    if (err) {
                        return console.log(err);
                    }
                    //Then, create the makeFile
                    var initMakefile = "ARDLIBS = " + libs + "\nMODEL = " + data.board + "\n" + "ARDUINO_DIR = " + arduino_dir + "\n" + "HOME_LIB = " + arduino_dir + "/sketchbook/libraries\n\n";
                    fs.writeFile("tmp/Makefile", initMakefile + commonMakefile, function(err) {
                        if (err) {
                            return console.log(err);
                        }
                        callback();
                    });
                });
            }
        });
    };

    function parseError(error, stdout, stderr) {
        var error = {
            compilation: [],
            uploading: ''
        };
        //Parse errors comming from stderr regarding the compilation:
        // console.log('error:\n', error);
        // console.log('stdout:\n', stdout);
        var compileStderr = stderr.substr(0, stderr.indexOf("make:"));
        compileStderr = compileStderr.split("applet/tmp.cpp:");
        // console.log('compileStderr:\n', compileStderr);
        for (var i in compileStderr) {
            var line, func, err;
            var index = compileStderr[i].indexOf(":");
            if (index > 0) {
                if (!isNaN(parseInt(compileStderr[i].substr(0, index), 10))) {
                    line = parseInt(compileStderr[i].substr(0, index));
                    err = compileStderr[i].substr(compileStderr[i].indexOf("error:") + 6, compileStderr[i].length);
                } else {
                    func = compileStderr[i];
                }
            }
            if (line && func && index) {
                error.compilation.push({
                    line: line,
                    func: func,
                    error: err
                });
                line = undefined;
                err = undefined;
                index = undefined;
                // console.log('line--->', line, '\nerror--->', err, '\nfunc--->', func);
                console.log('---------------------------------------------------');
            }
        }
        //Parse errors comming from stderr regarding the uploading (AVRDUDE):
        var uploadStderr = stderr.split("avrdude:");
        if (uploadStderr[uploadStderr.length - 1].search('bytes of flash written') > 0) {
            console.log('UPLOADED CORRECTLY');
        } else {
            error.uploading = uploadStderr.join('');
        }
        console.log('error', error);
        // if (error.compilation.length === 0) {
        //     console.log('NO ERRORS, COMPILATION SUCCESSFUL');
        // }
        return error;
    }

    function compile(data, socket) {
        createEnvironment(data, function() {
            //Finally, execute the "make" command on the given directory
            exec(makeCommand, {
                cwd: 'tmp',
            }, function(error, stdout, stderr) {
                console.log('compiling...\n');
                // console.log('stderr', stderr);
                // console.log('stdout', stdout);
                // return parseError(error, stdout, stderr);
                socket.emit('compileResponse', {
                    stdout: stdout,
                    stderr: stderr
                });
            });
        });
    };

    function upload(data, socket) {
        createEnvironment(data, function() {
            // //Finally, execute the "make" command on the given directory
            exec(makeUploadCommand, {
                cwd: 'tmp',
            }, function(error, stdout, stderr) {
                console.log('uploading...\n');
                // return parseError(error, stdout, stderr);
                socket.emit('uploadResponse', {
                    stdout: stdout,
                    stderr: stderr
                });
            });
        });
    };
    module.exports.compile = compile;
    module.exports.upload = upload;
})();