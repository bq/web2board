module.exports = function(grunt) {
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        clean: ['dist/'],
        copy: {
            winx86: {
                files: [{
                    expand: true,
                    src: 'app.js',
                    dest: 'dist/windows/x86/'
                }, {
                    expand: true,
                    cwd: 'distResources/windows/x86/',
                    src: '*',
                    dest: 'dist/windows/x86/'
                }]
            },
            macx86: {
                files: [{
                    expand: true,
                    src: 'app.js',
                    dest: 'dist/mac/x86/'
                }, {
                    expand: true,
                    cwd: 'distResources/mac/x86/',
                    src: 'node',
                    dest: 'dist/mac/x86/',
                }],
                options: {
                    mode: 0755
                }

            }
        }
    });
    grunt.loadNpmTasks('grunt-contrib-copy');
    grunt.loadNpmTasks('grunt-contrib-clean');

    grunt.registerTask('build', [
        'clean',
        'copy:winx86'
    ]);

    grunt.registerTask('mac', [
        'clean',
        'copy:macx86'
    ]);

    grunt.registerTask('default', function() {
        grunt.log.write('use build ').ok();
    });
};