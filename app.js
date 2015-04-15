'use strict'

console.log('Starting web2board...');

var app = require('http').createServer(handler)
var io = require('socket.io')(app);
var ffmpegTransforms = require('./ffmpegTransforms');

app.listen(9999);

function handler(req, res) {
    res.writeHead(200);
    res.end('nope');
}

io.on('connection', function(socket) {
    socket.emit('news', {
        hello: 'world'
    });
    socket.on('my other event', function(data) {
        console.log(data);
    });
});

ffmpegTransforms.convert('aloha', 'aloha2', function(err, data) {
    console.log('err');
    console.log(err);
    console.log('data');
    console.log(data);

});