module.exports = function(grunt) {
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        clean: ['dist/'],
        copy: {
            winx86: {
                files: [{
                    expand: true,
                    cwd: 'distResources/windows/x86/',
                    src: '**',
                    dest: 'dist/windows/x86/',
                }, {
                    expand: true,
                    cwd: 'app/',
                    src: ['**', '!appResources/**'],
                    dest: 'dist/windows/x86/resources/app/'
                }]
            },
            macx86: {
                files: [{
                    expand: true,
                    cwd: 'distResources/mac/x86/',
                    src: '**',
                    dest: 'dist/mac/x86/',
                }, {
                    expand: true,
                    cwd: 'app/',
                    src: ['**', '!appResources/**'],
                    dest: 'dist/mac/x86/Bitbloq.app/Contents/Resources/app/'
                }],
                options: {
                    mode: true
                }
            },
            linuxx86: {
                files: [{
                    expand: true,
                    cwd: 'distResources/linux/x86/',
                    src: '**',
                    dest: 'dist/linux/x86/',
                }, {
                    expand: true,
                    cwd: 'app/',
                    src: ['**', '!appResources/**'],
                    dest: 'dist/linux/x86/resources/app/'
                }]
            },
            winx64: {
                files: [{
                    expand: true,
                    cwd: 'distResources/windows/x64/',
                    src: '**',
                    dest: 'dist/windows/x64/',
                }, {
                    expand: true,
                    cwd: 'app/',
                    src: ['**', '!appResources/**'],
                    dest: 'dist/windows/x64/resources/app/'
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
                    src: ['**', '!appResources/**'],
                    dest: 'dist/mac/x64/Bitbloq.app/Contents/Resources/app/'
                }],
                options: {
                    mode: true
                }
            },
            linuxx64: {
                files: [{
                    expand: true,
                    cwd: 'distResources/linux/x64/',
                    src: '**',
                    dest: 'dist/linux/x64/',
                }, {
                    expand: true,
                    cwd: 'app/',
                    src: ['**', '!appResources/**'],
                    dest: 'dist/linux/x64/resources/app/'
                }]
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
                'copy:macx86',
                'copy:linuxx86',
                'copy:winx64',
                'copy:macx64',
                'copy:linuxx64'
            ]);
        }
    });

    grunt.registerTask('default', function() {
        grunt.log.write('use build or build:<platform> ').ok();
    });
};