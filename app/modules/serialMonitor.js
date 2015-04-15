//----------------------------------------------------------------//
// This file is part of the web2board Project                     //
//                                                                //
// Date: April 2015                                               //
// Author: Irene Sanz Nieto  <irene.sanz@bq.com>                  //
//----------------------------------------------------------------//
(function() {
    function start(port) {
        var SerialPort = require("serialport").SerialPort;
        var serialport = new SerialPort(port);
        serialport.on('open', function() {
            console.log('Serial Port Opend');
            serialport.on('data', function(data) {
                console.log(data[0]);
            });
        });
    }
    module.exports.start = start;
})();