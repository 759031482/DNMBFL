import sys, os, subprocess, time
from util import Programwork
import sbfl.sbfl_for as sbfl_for
import util


# 根据测试用例执行结果生成4元组信息
def touple(res, cov_all):
    touple_all = {}
    for cov in cov_all:
        if not cov:
            continue
        for line in cov:
            if line not in touple_all:
                touple_all[line] = [0, 0, 0, 0]
            # ef,ep,nf,np

    for i, cov in enumerate(cov_all):
        if not cov:
            continue
        for key in touple_all:
            A = 1 if res[i] else 0
            if not key in cov:
                A += 2
            touple_all[key][A] += 1
    return touple_all


# 对java程序生成元组
def touple_java(cov_info, test_reslut):
    touple_all = {}
    # {package: { class: { line: [ef, ep, nf, np]}}}
    for package_name in cov_info:
        if package_name not in touple_all:
            touple_all[package_name] = {}

        for class_name in cov_info[package_name]:
            if class_name not in touple_all[package_name]:
                touple_all[package_name][class_name] = {}

            for line in cov_info[package_name][class_name]:
                touples = [0, 0, 0, 0]
                # ef ep nf np
                for i, tc in enumerate(test_reslut):
                    if i >= len(cov_info[package_name][class_name][line]):
                        break
                    touple = test_reslut[tc][0]    # f|p 0|1
                    if cov_info[package_name][class_name][line][i] <= 0:
                        touple += 2
                    touples[touple] += 1
                touple_all[package_name][class_name][line] = touples
    return touple_all


def suspicious(touple_all, mainmessage):
    # touple_all 字典 line：touple
    sus = {}
    for line in touple_all:
        sus[line] = mainmessage['sbfl']['sbflform'](touple_all[line])
        mainmessage['sbfl']['touple'][line] = touple_all[line]
    return mainmessage


def execute(cov_all):
    # 使用program的cov_all 生成被执行行列表
    list_cov = []
    for cov in cov_all:
        list_cov += cov
    return list(set(list_cov))


def main(mainmessage):
    programwork = Programwork(mainmessage['type'])
    programwork.program_start(mainmessage['program_path'], mainmessage['testdata_dirpath'])
    if programwork.cov:
        touple_all = touple(programwork.res, programwork.cov_all)
        mainmessage['sbfl']['testres'] = programwork.res
        mainmessage['sbfl']['sus'] = suspicious(touple_all, mainmessage)
        mainmessage['execute'] = execute(programwork.cov_all)
        return mainmessage

    return mainmessage


def java_main(src):
    java = util.Java(src)
    java.program_start()
    return touple_java(java.cov_info, java.test_reulut)


if __name__ == '__main__':
    mainmessage = {
        'program_path': r'E:\programs\access\data\367223.c',
        'testdata_dirpath': r'E:\programs\access\data\testcase',
        'sbflform': sbfl_for.ochiai,

    }
    main(mainmessage)
