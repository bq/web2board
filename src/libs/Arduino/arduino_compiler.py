#!/usr/bin/env python
#-*- coding: utf-8 -*-

# 1. Copyright
# 2. Lisence
# 3. Author

"""
Documents
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import os
import threading
import subprocess
import re
import time

from . import base
from . import arduino_src


class Project(base.abs_file.Dir):
    def __init__(self, path):
        super(Project, self).__init__(path)
        primary_file_name = self.name + '.ino'
        primary_file_path = os.path.join(self.path, primary_file_name)
        self.primary_file = base.abs_file.File(primary_file_path)

    def list_ino_files(self):
        files = self.list_files_of_extensions(arduino_src.INO_EXTS)
        if files and self.primary_file.is_file():
            files = [f for f in files if f.name.lower() !=
                     self.primary_file.name.lower()]
            files.insert(0, self.primary_file)
        return files

    def list_cpp_files(self, is_big_project=False):
        if is_big_project:
            cpp_files = self.recursive_list_files(arduino_src.CPP_EXTS)
        else:
            cpp_files = self.list_files_of_extensions(arduino_src.CPP_EXTS)

        primary_file_path = self.primary_file.get_path()
        for cpp_file in cpp_files:
            cpp_file_path = cpp_file.get_path()
            if cpp_file_path.startswith(primary_file_path):
                cpp_files.remove(cpp_file)
                break
        return cpp_files

    def list_h_files(self, is_big_project=False):
        if is_big_project:
            files = files = self.recursive_list_files(arduino_src.H_EXTS)
        else:
            files = self.list_files_of_extensions(arduino_src.H_EXTS)
        return files


class Compiler(object):
    def __init__(self, path, libraries, core_path, ide_path, build_f_cpu, target_board_mcu):
        self.libraries = libraries
        self.need_to_build = True
        self.params = {}

        self.core_path = core_path
        self.ide_path = ide_path
        # self.working_dir = ide_path
        self.build_f_cpu = build_f_cpu
        self.target_board_mcu = target_board_mcu

        self.project = Project(path)
        project_name = self.project.get_name()

        build_path = get_build_path()
        build_path = os.path.join(build_path, project_name)
        self.set_build_path(build_path)

        self.error_occured = False
        self.stderr = ''
        self.settings = base.settings.get_arduino_settings()
        self.bare_gcc = self.settings.get('bare_gcc', False)
        self.is_big_project = self.settings.get('big_project', False)

    def set_build_path(self, build_path):
        self.build_path = build_path
        if not os.path.isdir(self.build_path):
            os.makedirs(self.build_path)

    def build(self):
        start_time = time.time()
        self.prepare_project_src_files()
        if self.need_to_build:
            print('[Stino - Start building]\\n')
            self.prepare_core_src_files()
            self.prepare_params()
            self.prepare_cmds()
            self.exec_build_cmds()
            if not self.error_occured:
                end_time = time.time()
                diff_time = end_time - start_time
                diff_time = '%.1f' % diff_time
                print('[Stino - Done building in '+ diff_time+'s.]\\n')
        else:
            self.error_occured = True
        return self.stderr

    def prepare_project_src_files(self):
        self.project_src_changed = False
        self.project_cpp_obj_pairs = []
        self.project_obj_paths = []

        ino_files = self.project.list_ino_files()
        if ino_files and not self.bare_gcc:
            combined_file_name = self.project.get_name() + '.ino.cpp'
            combined_file_path = os.path.join(
                self.build_path, combined_file_name)
            combined_file = base.abs_file.File(combined_file_path)
            combined_obj_path = combined_file_path + '.o'
            self.project_obj_paths.append(combined_obj_path)

            ino_changed = check_ino_change(ino_files, combined_file)
            # if self.is_new_build or ino_changed:
            core_path = self.params.get('build.core.path', '')
            main_cxx_path = os.path.join(core_path, 'main.cxx')
            if os.path.isfile(main_cxx_path):
                main_cxx_file = base.abs_file.File(main_cxx_path)
                ino_files.append(main_cxx_file)
            combined_src = arduino_src.combine_ino_files(
                core_path, ino_files)
            combined_file.write(combined_src)
            cpp_obj_pair = (combined_file_path, combined_obj_path)

            self.project_cpp_obj_pairs.append(cpp_obj_pair)

        sub_dir_name = self.project.get_name()
        cpp_files = self.project.list_cpp_files(self.is_big_project)
        self.project_obj_paths += gen_obj_paths(
            self.project.get_path(), self.build_path, sub_dir_name, cpp_files)
        cpp_obj_pairs = gen_cpp_obj_pairs(self.project.get_path(),
                                          self.build_path, sub_dir_name,
                                          cpp_files)
        self.project_cpp_obj_pairs += cpp_obj_pairs

        if self.project_cpp_obj_pairs:
            self.project_src_changed = True
        self.need_to_build = bool(self.project_obj_paths)

    def prepare_lib_src_files(self):
        ino_files = []
        if not self.bare_gcc:
            ino_files = self.project.list_ino_files()
        cpp_files = self.project.list_cpp_files(self.is_big_project)
        h_files = self.project.list_h_files(self.is_big_project)
        src_files = ino_files + cpp_files + h_files
        last_build_path = os.path.join(self.build_path, 'last_build.txt')
        last_build_file = base.settings.Settings(last_build_path)
        last_lib_paths = last_build_file.get('lib_paths', [])
        lib_paths = [lib.get_path() for lib in self.libraries]
        last_build_file.set('lib_paths', lib_paths)

    def prepare_core_src_files(self):
        self.core_obj_paths = []
        self.core_cpp_obj_pairs = []
        self.core_src_changed = False

        # target_arch = TODO_target_arch
        self.core_paths = []
        if not self.bare_gcc:
            # core_path = TODO_core_path
            cores_path = os.path.dirname(self.core_path)

            common_core_path = os.path.join(cores_path, 'Common')
            build_hardware = self.params.get('build.hardware', '')
            core_paths = [self.core_path, common_core_path]
            if build_hardware:
                platform_path = self.params.get('runtime.platform.path', '')
                hardware_path = os.path.join(platform_path, build_hardware)
                core_paths.append(hardware_path)

            core_paths = [p for p in core_paths if os.path.isdir(p)]
            for core_path in core_paths:
                if core_path not in self.core_paths:
                    self.core_paths.append(core_path)

            for core_path in self.core_paths:
                core_obj_paths, core_cpp_obj_pairs = gen_core_objs(
                    core_path, 'core_', self.build_path)
                self.core_obj_paths += core_obj_paths
                self.core_cpp_obj_pairs += core_cpp_obj_pairs

        if self.core_cpp_obj_pairs:
            self.core_src_changed = True

####################################################################
    def gen_replaced_text_list(self, text):
        pattern_text = r'\{\S+?}'
        pattern = re.compile(pattern_text)
        replaced_text_list = pattern.findall(text)
        return replaced_text_list

    def replace_param_value(self, value, params):
        replaced_text_list = self.gen_replaced_text_list(value)
        for text in replaced_text_list:
            key = text[1:-1]
            if key in params:
                param_value = params[key]
                param_value = self.replace_param_value(param_value, params)
                value = value.replace(text, param_value)
        return value


    def replace_param_values(self, params):
        new_params = {}
        for key in params:
            value = params.get(key)
            if '{' in value:
                value = self.replace_param_value(value, params)
            new_params[key] = value
        return new_params
####################################################################

    def prepare_params(self):
        self.archive_file_name = 'core.a'
        self.params['build.path'] = self.build_path
        self.params['build.project_name'] = self.project.get_name()
        self.params['archive_file'] = self.archive_file_name

        extra_flag = ' ' + self.settings.get('extra_flag', '')
        c_flags = self.params.get('compiler.c.flags', '') + extra_flag
        cpp_flags = self.params.get('compiler.cpp.flags', '') + extra_flag
        S_flags = self.params.get('compiler.S.flags', '') + extra_flag
        self.params['compiler.c.flags'] = c_flags
        self.params['compiler.cpp.flags'] = cpp_flags
        self.params['compiler.S.flags'] = S_flags

        project_path = self.project.get_path()
        include_paths = [project_path] + self.core_paths

        includes = ['-I "%s"' % path for path in include_paths]
        self.params['includes'] = ' '.join(includes)

        ide_path = self.ide_path
        if not 'compiler.path' in self.params:
            compiler_path = '{runtime.ide.path}/hardware/tools/avr/bin/'
            self.params['compiler.path'] = compiler_path
        compiler_path = self.params.get('compiler.path')
        compiler_path = compiler_path.replace('{runtime.ide.path}', ide_path)
        if not os.path.isdir(compiler_path):
            self.params['compiler.path'] = ''


        #my intervention!
        compiler_c_cmd='avr-gcc'
        compiler_S_cmd='avr-gcc'
        compiler_c_flags='-c -g -Os -w -ffunction-sections -fdata-sections -MMD'
        compiler_c_elf_flags='-Os -Wl,--gc-sections'
        compiler_c_elf_cmd='avr-gcc'
        compiler_S_flags='-c -g -assembler-with-cpp'
        compiler_cpp_cmd='avr-g++'
        compiler_cpp_flags='-c -g -Os -w -fno-exceptions -ffunction-sections -fdata-sections -MMD'
        compiler_ar_cmd='avr-ar'
        compiler_ar_flags='rcs'
        compiler_objcopy_cmd='avr-objcopy'
        compiler_objcopy_eep_flags='-O ihex -j .eeprom --set-section-flags=.eeprom=alloc,load --no-change-warnings --change-section-lma .eeprom=0'
        compiler_elf2hex_flags='-O ihex -R .eeprom'
        compiler_elf2hex_cmd='avr-objcopy'

        self.params['build.mcu'] = self.target_board_mcu
        self.params['build.f_cpu'] = self.build_f_cpu

        self.params['includes']+= self.libraries
        self.params['recipe.c.o.pattern'] = '"'+compiler_path+ compiler_c_cmd + '"'+'  '+ compiler_c_flags +' -mmcu='+self.params['build.mcu']+' -DF_CPU='+self.params['build.f_cpu']+' '+self.params['includes'] +' "{source_file}" -o "{object_file}"'
        self.params['recipe.cpp.o.pattern'] = '"'+compiler_path+compiler_cpp_cmd+'"'+' '+ compiler_cpp_flags + ' -mmcu='+self.params['build.mcu']+' -DF_CPU='+self.params['build.f_cpu']+' '+ self.params['includes'] +' "{source_file}" -o "{object_file}"'
        self.params['recipe.S.o.pattern'] = '"'+compiler_path+ compiler_S_cmd+'"'+' '+ compiler_S_flags + ' -mmcu='+self.params['build.mcu']+' -DF_CPU='+self.params['build.f_cpu']+ ' '+self.params['includes'] +' "{source_file}" -o "{object_file}"'
        self.params['recipe.ar.pattern'] = '"'+compiler_path+ compiler_ar_cmd+'"'+' '+ compiler_ar_flags + ' "'+ self.params['build.path']+'/{archive_file}" "{object_file}"'
        self.params['recipe.c.combine.pattern'] = '"'+compiler_path+ compiler_c_elf_cmd+'"'+' '+compiler_c_elf_flags + ' -mmcu='+self.params['build.mcu']+' -o '+'"'+self.params['build.path']+'/'+self.params['build.project_name']+'.elf" "{object_files}" '+' "'+self.params['build.path']+'/{archive_file}" -L"'+self.params['build.path']+'" -lm'
        self.params['recipe.objcopy.eep.pattern'] = '"'+compiler_path+ compiler_objcopy_cmd+'"'+' '+ compiler_objcopy_eep_flags + ' '+ self.params['build.path']+'/'+self.params['build.project_name']+'.elf '+self.params['build.path']+'/'+self.params['build.project_name']+'.eep'
        self.params['recipe.objcopy.hex.pattern'] = '"'+compiler_path+compiler_elf2hex_cmd+'"'+' '+ compiler_elf2hex_flags + ' '+ self.params['build.path']+'/'+self.params['build.project_name']+'.elf '+self.params['build.path']+'/'+self.params['build.project_name']+'.hex'
        self.params = self.replace_param_values(self.params)

    def prepare_cmds(self):
        compile_c_cmd = self.params.get('recipe.c.o.pattern', '')
        compile_cpp_cmd = self.params.get('recipe.cpp.o.pattern', '')
        compile_asm_cmd = self.params.get('recipe.S.o.pattern', '')
        ar_cmd = self.params.get('recipe.ar.pattern', '')
        combine_cmd = self.params.get('recipe.c.combine.pattern', '')
        eep_cmd = self.params.get('recipe.objcopy.eep.pattern', '')
        hex_cmd = self.params.get('recipe.objcopy.hex.pattern', '')

        self.build_files = []
        self.file_cmds_dict = {}
        for cpp_path, obj_path in (self.project_cpp_obj_pairs +
                                   self.core_cpp_obj_pairs):
            cmd = compile_cpp_cmd
            ext = os.path.splitext(cpp_path)[1]
            if ext == '.c':
                cmd = compile_c_cmd
            elif ext == '.S':
                cmd = compile_asm_cmd
            cmd = cmd.replace('{source_file}', cpp_path)
            cmd = cmd.replace('{object_file}', obj_path)
            self.build_files.append(obj_path)
            self.file_cmds_dict[obj_path] = [cmd]

        core_changed = False
        core_archive_path = os.path.join(self.build_path,
                                         self.archive_file_name)
        if not os.path.isfile(core_archive_path):
            core_changed = True
            cmds = []
            for obj_path in self.core_obj_paths:
                cmd = ar_cmd.replace('{object_file}', obj_path)
                cmds.append(cmd)
            self.build_files.append(core_archive_path)
            self.file_cmds_dict[core_archive_path] = cmds


        project_file_base_path = os.path.join(self.build_path,
                                              self.project.get_name())
        elf_file_path = project_file_base_path + '.elf'
        if self.project_src_changed or core_changed:
            if os.path.isfile(elf_file_path):
                os.remove(elf_file_path)

        if not os.path.isfile(elf_file_path):
            obj_paths = ' '.join(['"%s"' % p for p in self.project_obj_paths])
            cmd = combine_cmd.replace('{object_files}', obj_paths)
            if not self.core_obj_paths:
                core_archive_path = \
                    self.build_path + '/' + self.archive_file_name
                text = '"' + core_archive_path + '"'
                cmd = cmd.replace(text, '')
            self.build_files.append(elf_file_path)
            self.file_cmds_dict[elf_file_path] = [cmd]

            if eep_cmd:
                eep_file_path = project_file_base_path + '.eep'
                self.build_files.append(eep_file_path)
                self.file_cmds_dict[eep_file_path] = [eep_cmd]

            if hex_cmd:
                ext = '.bin'
                if '.hex' in hex_cmd:
                    ext = '.hex'
                hex_file_path = project_file_base_path + ext
                self.build_files.append(hex_file_path)
                self.file_cmds_dict[hex_file_path] = [hex_cmd]

    def exec_build_cmds(self):
        show_compilation_output = self.settings.get('build_verbose', False)
        error_occured = False

        total_file_number = len(self.build_files)
        #print('enumerate(self.build_files)',self.build_files)
        for index, build_file in enumerate(self.build_files):
            percent = str(int(100 * (index + 1) / total_file_number )).rjust(3)
            print('['+percent+'%] \\n')
            cmds = self.file_cmds_dict.get(build_file)
            result = exec_cmds(self.ide_path, cmds, show_compilation_output)
            if (result == -1):
                break
            self.stderr += result
    def has_error(self):
        print("error")
        return self.error_occured



def get_build_path():
    settings = base.settings.get_arduino_settings()
    build_path = settings.get('build_path', '')
    if not build_path:
        tmp_path = base.sys_path.get_tmp_path()
        build_path = os.path.join(tmp_path, 'Stino_build')
    if not os.path.isdir(build_path):
        os.makedirs(build_path)
    return build_path


def check_ino_change(ino_files, combined_file):
    ino_changed = False
    combined_file_path = combined_file.get_path()
    obj_path = combined_file_path + '.o'
    obj_file = base.abs_file.File(obj_path)
    for ino_file in ino_files:
        if ino_file.get_mtime() > obj_file.get_mtime():
            ino_changed = True
            break
    return ino_changed


def gen_cpp_obj_pairs(src_path, build_path, sub_dir,
                      cpp_files, new_build=False):
    obj_paths = gen_obj_paths(src_path, build_path, sub_dir, cpp_files)
    obj_files = [base.abs_file.File(path) for path in obj_paths]

    path_pairs = []
    for cpp_file, obj_file in zip(cpp_files, obj_files):
        if new_build or cpp_file.get_mtime() > obj_file.get_mtime():
            path_pair = (cpp_file.get_path(), obj_file.get_path())
            path_pairs.append(path_pair)
    return path_pairs


def gen_obj_paths(src_path, build_path, sub_dir, cpp_files):
    obj_paths = []
    build_path = os.path.join(build_path, sub_dir)
    for cpp_file in cpp_files:
        cpp_file_path = cpp_file.get_path()
        sub_path = cpp_file_path.replace(src_path, '')[1:] + '.o'
        obj_path = os.path.join(build_path, sub_path)
        obj_paths.append(obj_path)

        obj_dir_name = os.path.dirname(obj_path)
        if not os.path.exists(obj_dir_name):
            os.makedirs(obj_dir_name)
    return obj_paths


def exec_cmds(working_dir, cmds, is_verbose=False):
    error_occured = False
    for cmd in cmds:
        return_code, stdout, stderr = exec_cmd(working_dir, cmd)
        print(cmd)
        # if is_verbose:
        #     # message_queue.put(cmd + '\n')
        #     if stdout:
        #         # message_queue.put(stdout + '\n')
        #         print(stdout + '\n')
        # if stderr:
        #     print(stderr + '\n')
        if return_code != 0:
            print('[Stino - Exit with error code '+str(return_code)+'.]\\n'+stderr)
            error_occured = True
            return -1
    return stderr


def exec_cmd(working_dir, cmd):
    os.environ['CYGWIN'] = 'nodosfilewarning'
    if cmd:
        # print ("exec_cmd -->", cmd)
        os.chdir(working_dir)
        compile_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        result = compile_proc.communicate()
        return_code = compile_proc.returncode
        stdout = result[0].decode(base.sys_info.get_sys_encoding())
        stderr = result[1].decode(base.sys_info.get_sys_encoding())
    else:
        return_code = 0
        stdout = ''
        stderr = ''
    return (return_code, stdout, stderr)


def formatCommand(cmd):
    if '::' in cmd:
        cmd = cmd.replace('::', ' ')
    cmd = cmd.replace('\\', '/')
    os_name = base.sys_info.get_os_name()
    python_version = base.sys_info.get_python_version()
    if python_version < 3 and os_name == 'windows':
        cmd = '"%s"' % cmd
    return cmd


def regular_numner(num):
    txt = str(num)
    regular_num = ''
    for index, char in enumerate(txt[::-1]):
        regular_num += char
        if (index + 1) % 3 == 0 and index + 1 != len(txt):
            regular_num += ','
    regular_num = regular_num[::-1]
    return regular_num


def gen_core_objs(core_path, folder_prefix, build_path, is_new_build = True):
    core_dir = base.abs_file.Dir(core_path)
    core_cpp_files = core_dir.recursive_list_files(
        arduino_src.CPP_EXTS, ['libraries'])
    sub_dir_name = folder_prefix + core_dir.get_name()

    core_obj_paths = gen_obj_paths(core_path, build_path,
                                   sub_dir_name, core_cpp_files)
    core_cpp_obj_pairs = gen_cpp_obj_pairs(
        core_path, build_path, sub_dir_name, core_cpp_files, is_new_build)
    return (core_obj_paths, core_cpp_obj_pairs)
