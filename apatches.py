#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
import re
import subprocess
import sys

import openpyxl


def get_all_files(top):
    all_files = []
    for (dirpath, dirnames, filenames) in os.walk(top):
        for file in filenames:
            # all_files.append(os.path.join(dirpath[len(top) + 1:], file))
            all_files.append(os.path.join(dirpath, file))

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


def apply_patch(patch):
    cmd = "git am --directory=" + get_git_directory(patch) + " -k " + patch
    print(cmd)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('''Usage: apatches your_patches_folder''')
        exit(-1)

    patches_folder = sys.argv[1]
    # old_cwd = os.getcwd()
    # os.chdir("C:\\Users\\admin\\Desktop")


    # 获取将要打的patches
    # 根据change id在git log中查看patch的change id是否已经存在
    # 存在表示之前已经打过该patch，不需要再打
    need_apply_patches = []
    for f in get_all_files(patches_folder):
        change_id = get_change_id(f)
        if not has_change_id(gitlog(), change_id):
            need_apply_patches.append(f)

    need_apply_patches.sort()

    # print(need_apply_patches)
    # for patch in need_apply_patches:
    #     print(get_git_directory(patch[len(patches_folder)]))

    patch = need_apply_patches[0]
    print(patch)
    cmd = "git am --directory=" + get_git_directory(patch[len(patches_folder)]) + " -k " + patch
    print(cmd)
    # shell_exc(cmd)

