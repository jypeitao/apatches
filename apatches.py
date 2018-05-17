#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
import re
import subprocess
import sys
from collections import defaultdict

import openpyxl


def get_all_files(top):
    all_files = []
    for (dirpath, dirnames, filenames) in os.walk(top):
        for file in filenames:
            # all_files.append(os.path.join(dirpath[len(top) + 1:], file))
            all_files.append(os.path.join(dirpath, file))

    all_files.sort()
    return all_files


def write_to_excel(name, patches, prefix=None):
    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet['A1'] = "patch路径"
    sheet['B1'] = "状态"
    sheet['C1'] = "备注"
    sheet.title = "patches info"

    width = 1
    for i in range(len(patches)):
        tmp = patches[i]
        if prefix:
            tmp = tmp[len(prefix):]

        sheet["A%d" % (i + 2)].value = tmp
        if len(tmp) > width:
            width = len(tmp)

    sheet.column_dimensions['A'].width = width + 1
    wb.save(name)


def has_change_id(content, change_id):
    reg = r"Change-Id: (" + change_id + ")"
    m = re.search(reg, content)
    if m:
        return True
    else:
        return False


def has_error(content):
    reg = r"error:"
    m = re.search(reg, content)
    if m:
        return True
    else:
        return False


def get_change_id(patch):
    cid = None
    with open(patch) as f:
        reg = r"Change-Id: ([0-9a-zA-Z]*)"
        m = re.search(reg, f.read())
        if m:
            cid = m.group(1)
        else:
            print("No Change-Id")

    return cid


def gitlog():
    cmd = "git log"
    return shell_exc(cmd)


def shell_exc(cmd):
    sp = subprocess.Popen(cmd,
                          shell=True,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          bufsize=-1)

    result = sp.communicate()
    stdo = result[0].decode('utf-8')
    stde = result[1].decode('utf-8')
    return stdo + stde


def get_git_directory(patch):
    dir_name = os.path.dirname(patch)
    git_directory = os.path.join("LINUX", "android", dir_name)
    return git_directory


def color_string(content, color):
    COLOR = { 
            'black': 30,   # 黑色
            'red': 31,   # 红色
            'green': 32,   # 绿色
            'yellow': 33,   # 黄色
            'blue': 34,   # 蓝色
            'purple': 35,   # 紫红色
            'cyan': 36,   # 青蓝色
            'white': 37,   # 白色
    }
    cstring = "\033[0;" + str(COLOR[color]) + "m" + content + "\033[0m"
    return cstring


def apply_patch(patch):
    cmd = "git am --directory=" + get_git_directory(patch) + " -k " + patch
    print(cmd)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('''Usage: apatches your_patches_folder''')
        exit(-1)

    # make sure the path has a sep
    patches_folder = os.path.join(sys.argv[1], "")
    # old_cwd = os.getcwd()
    # os.chdir("C:\\Users\\admin\\Desktop")


    # use map to record the state of each patch.
    # key is patch name
    # value is a list, list[0] records patch was merged or not.
    # list[1] records why not apply this time.
    patches_info = defaultdict(list)

    # get the change id of every patch
    # and then search in the git log
    # if can be found, it means that this patch has applied before.
    # Add the previously unapplied to the list.
    need_apply_patches = []
    for f in get_all_files(patches_folder):
        change_id = get_change_id(f)
        prefixless = f[len(patches_folder):]
        if not has_change_id(gitlog(), change_id):
            patches_info[prefixless].append('unkown')  # list[0]
            patches_info[prefixless].append('unkown')  # list[1]
            need_apply_patches.append(f)
        else:
            patches_info[prefixless].append('not applied')
            patches_info[prefixless].append('already exist')


    need_apply_patches.sort()
    if not need_apply_patches:
        print(color_string("No patch needs to be applied.", 'green'))
        exit(0)

    # begin to apply patch one by one 
    total_patches = len(need_apply_patches)
    for i in range(1, total_patches + 1):
        patch = need_apply_patches[i - 1]
        print(color_string("Applying: [" + str(i) + "/" + str(total_patches) + "]", 'green') + patch)
        cmd = "git am --directory=" + get_git_directory(patch[len(patches_folder):]) + " -k " + patch
        git_result = shell_exc(cmd)
        #print(git_result)
        #print(cmd)
        if has_error(git_result):
            shell_exc("git am --abort")
            error_info = "Error: Already applied " + str(i - 1) +", " + str(total_patches -i +1) + " left to apply."
            print(color_string("Error: Already applied " + str(i - 1) +", " + str(total_patches -i +1) + " left to apply.", 'red'))
            print(color_string("Please manually execute:" + cmd + " and fix it.", 'red'))
            print(color_string("Then re-execute the command:" + sys.argv[0] + " " + sys.argv[1], 'red'))
            exit(-1)

    # just test
    #patch = need_apply_patches[0]
    #print(patch)
    #cmd = "git am --directory=" + get_git_directory(patch[len(patches_folder):]) + " -k " + patch
    #print(cmd)
    #git_result = shell_exc(cmd)
    #print(git_result)
    #if has_error(git_result):
    #    exit(-1)
