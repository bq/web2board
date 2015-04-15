(function() {
    var exec = require('child_process').exec;

    function convert(filePath, baseFilePath, callback) {
        console.log('hola');
        exec('ffmpeg -i ' + baseFilePath + ' ' + filePath, callback);
    }

    module.exports.convert = convert;
})();