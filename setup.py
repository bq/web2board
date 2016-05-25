from distutils.core import setup

setup(
    name='web2board',
    version='2.1.0',
    packages=['pkg', 'res', 'res.common', 'res.common.Scons', 'res.common.Scons.sconsFiles',
              'res.common.Scons.sconsFiles.SCons', 'res.common.Scons.sconsFiles.SCons.Node',
              'res.common.Scons.sconsFiles.SCons.Tool', 'res.common.Scons.sconsFiles.SCons.Tool.docbook',
              'res.common.Scons.sconsFiles.SCons.Tool.MSCommon', 'res.common.Scons.sconsFiles.SCons.Tool.packaging',
              'res.common.Scons.sconsFiles.SCons.Script', 'res.common.Scons.sconsFiles.SCons.compat',
              'res.common.Scons.sconsFiles.SCons.Options', 'res.common.Scons.sconsFiles.SCons.Scanner',
              'res.common.Scons.sconsFiles.SCons.Platform', 'res.common.Scons.sconsFiles.SCons.Variables',
              'res.common.platformioWorkSpace', 'src', 'src.Test', 'src.Test.unit', 'src.Test.unit.Updaters',
              'src.Test.unit.WSCommunication', 'src.Test.unit.WSCommunication.Hubs', 'src.Test.resources',
              'src.Test.integration', 'src.Test.integration.Updaters', 'src.libs', 'src.libs.base', 'src.libs.Updaters',
              'src.libs.Packagers', 'src.libs.Decorators', 'src.libs.WSCommunication', 'src.libs.WSCommunication.Hubs',
              'src.libs.WSCommunication.Clients', 'src.frames', 'src.Scripts', 'src.platformio', 'src.platformio.ide',
              'src.platformio.builder', 'src.platformio.builder.tools', 'src.platformio.builder.scripts',
              'src.platformio.builder.scripts.frameworks', 'src.platformio.commands', 'src.platformio.platforms',
              'demo._static'],
    url='https://github.com/bq/web2board',
    license='GNU GPL',
    author='bq',
    author_email='support-bitbloq@bq.com',
    description='Native program that connects a web and a board.',
    requires=['wshubsapi', 'click', 'glob2']
)
