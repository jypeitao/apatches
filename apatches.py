import os
import re
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


# write_to_excel('io_patches.xlsx', get_all_files('patch'), 'patch\\')
# get_all_files('patch')
# allfiles = get_all_files('patch')
# for f in allfiles:
#     print(search_change_id(f))
#
# str = "I8527abaab1d0fb3affaf27ae42d0b01fc4531d35"
# with open('log') as f:
#     reg = r"Change-Id: (" + str + ")"
#     print(reg)
#     m = re.search(reg, f.read())
#     if m:
#         cid = m.group(1)
#         print(cid)
#     else:
#         print("No Change-Id")

print(__name__)

if __name__ == '__main__':
    print(len(sys.argv))
    if len(sys.argv) < 2:
        print('''Usage: apatches your_patches_folder''')
        exit(-1)

    patches_folder = sys.argv[1]

    print(os.getcwd())
    old_cwd = os.getcwd()
    os.chdir("C:\\Users\\admin\\Desktop")
    print(os.getcwd())

    # 根据change id在git log中查看patch的change id是否已经存在
    # 存在表示之前已经打过该patch，不需要再打，把还需要打的patch放到not_apply_files
    content = "git log"
    not_apply_files = []
    for f in get_all_files(patches_folder):
        change_id = get_change_id(f)
        if not has_change_id(content, change_id):
            not_apply_files.append(f)
            print(f)
