'use strict'
console.log('Starting web2board...');
var app = require('http').createServer(handler)
var io = require('socket.io')(app);
var serialMonitor = require('./modules/serialMonitor');
var compilerUploader = require('./modules/compilerUploader');
app.listen(9999);

function handler(req, res) {
    res.writeHead(200);
    res.end('nope');
}
io.on('connection', function(socket) {
    socket.emit('news', {
        hello: 'world'
    });
    socket.on('compile', function(data) {
        compilerUploader.compile('bt328', '/dev/ttyUSB0', data);
    });
    socket.on('upload', function(data) {
        compilerUploader.upload('bt328', '/dev/ttyUSB0', data);
    });
    socket.on('serialMonitor', function(data) {
        serialMonitor.start('/dev/ttyUSB0');
    });
});