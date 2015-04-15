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
            macx64: {
                files: [{
                    expand: true,
                    cwd: 'distResources/mac/x64/',
                    src: '**',
                    dest: 'dist/mac/x64/',
                }, {
                    expand: true,
                    cwd: 'app/',
                    src: '**',
                    dest: 'dist/mac/x64/Bitbloq.app/Contents/Resources/app/'
                }],
                options: {
                    mode: true
                }
            }
        }
    });
    grunt.loadNpmTasks('grunt-contrib-copy');
    grunt.loadNpmTasks('grunt-contrib-clean');

    grunt.registerTask('build', function(target) {

        if (target) {
            return grunt.task.run([
                'clean',
                'copy:' + target
            ]);
        } else {
            return grunt.task.run([
                'clean',
                'copy:winx86',
                'copy:macx64'
            ]);
        }
    });

    grunt.registerTask('default', function() {
        grunt.log.write('use build or build:<platform> ').ok();
    });
};