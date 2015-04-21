//----------------------------------------------------------------//
// This file is part of the web2board Project                     //
//                                                                //
// Date: April 2015                                               //
// Author: Irene Sanz Nieto  <irene.sanz@bq.com>                  //
//----------------------------------------------------------------//
(function() {
    function start(port) {
        var serialport = require('serialport'), // include the library
            SerialPort = serialport.SerialPort, // make a local instance of it
            // get port name from the command line:
            portName = port;
        var myPort = new SerialPort(portName, {
            baudRate: 9600,
            // look for return and newline at the end of each data packet:
            parser: serialport.parsers.readline("\r\n")
        });
        myPort.on('open', showPortOpen);
        myPort.on('data', saveLatestData);
        myPort.on('close', showPortClose);
        myPort.on('error', showError);

        function showPortOpen() {
            console.log('port open. Data rate: ' + myPort.options.baudRate);
        }

        function saveLatestData(data) {
            console.log(data);
            console.log(data.toString());
        }

        function showPortClose() {
            console.log('port closed.');
        }

        function showError(error) {
            console.log('Serial port error: ' + error);
        }
    }
    module.exports.start = start;
})();