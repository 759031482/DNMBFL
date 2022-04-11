import os
import sys
import re
import util
import time
import datetime
from subprocess import Popen, PIPE
import subprocess
import numpy as np
import json
import random
from concurrent.futures import ThreadPoolExecutor
import threading
# from memory_profiler import profile

import sbfl.command as sbfl
import mbfl.command as mbfl
import mbfl.mbfl_for as mbfl_for
from codeflaws_version_control import Qr_excel
from data_codeflaws import Codeflaws

# log信息
# import log as LG
# global log
# log = LG.Log()

def perdef():

    global continueread
    continueread = True

    # 版本控制信息
    global vc_path
    vc_path = './report/data_codeflaws.xlsx'
    global sheet
    sheet = 'muti'
    global json_path
    json_path = './report/MBFL'
    global json_name
    json_name = 'data_%s.json'

    global max_workers
    max_workers = 1



def main():
    # codeflaws
    src = os.path.join(os.getcwd(), 'cdata', 'version')
    print(src)


    # 读取版本控制信息
    date_read = Qr_excel().read(vc_path, sheet)

    # 版本控制文件读取标记
    i = -1

    # 开始循环
    while i < len(date_read)-1:
        i += 1

        # if date_read[i, 4] == 0:
            # 跳过不需要的文件
            # continue

        Fault_Record = eval(date_read[i, 1])
        doc = date_read[i, 0]
        describe = str(doc) + '-' + str(i)


        if continueread:
            havedoc = False
            for file in os.listdir(json_path):
                if doc in file:
                    havedoc = True
            if havedoc:
                continue

        data_return = single_fom_part(src, doc, Fault_Record, describe)


        if not data_return.compile:
            continue

        # ----------------------------------------------------------------------------
        # json
        date_json = dict()
        date_json[doc] = dict()

        date_json[doc]['path'] = data_return.path
        date_json[doc]['src_tests'] = data_return.src_tests
        date_json[doc]['testcase'] = data_return.testcase
        date_json[doc]['Fault_Record'] = Fault_Record

        date_json[doc]['true_out'] = data_return.true_out
        date_json[doc]['or_out'] = data_return.or_out
        date_json[doc]['or_list'] = data_return.or_list

        date_json[doc]['time_spend'] = data_return.time_spend
        date_json[doc]['out_dic'] = data_return.out_dic
        date_json[doc]['fom_list'] = data_return.fom_list
        date_json[doc]['fomnum'] = data_return.fomnum



        # ********存储数据
        path = os.path.join(json_path, json_name % doc)
        with open(path, 'w') as f_obj:
            json.dump(date_json, f_obj)
        print('%s %s 存储完成' % (datetime.datetime.now(), doc))

        # ********删除无效数据
        del Fault_Record
        del doc
        del describe
        del havedoc
        del data_return
        del date_json
        del path


def single_fom_part(src, doc, Fault_Record, describe):
    # ----------------------------------------------------------------------------
    # 初始化数据
    data_return = util.Datasave()

    src_doc = os.path.join(src, doc, 'test_data')  # 题目大版本路径
    src_true = os.path.join(src_doc, 'true_root', 'source', 'tcas.c')  # 正确程序路径
    src_or = os.path.join(src_doc, 'defect_root', 'source', 'tcas.c')  # 故障程序路径
    src_tests = os.path.join(src_doc, 'inputs')  # 测试用例路径

    data_return.doc = doc
    data_return.path = src_or
    data_return.src_tests = src_tests
    data_return.Fault_Record = Fault_Record
    pre_del_s = datetime.datetime.now()

    # ----------------------------------------------------------------------------
    # 执行真实程序获取真实执行结果
    print('%s %s - 获取真实执行输出' % (datetime.datetime.now(), describe), end='')
    singleout = Codeflaws().single('tcas', src_true, src_tests)
    if not singleout[0]:
        print('\r %s %s - 获取真实执行输出失败' % (datetime.datetime.now(), describe))
        return data_return
    else:
        # 全体测试用例信息， 正确程序执行输出
        data_return.testcase, data_return.true_out = singleout[1], singleout[2]

    # ----------------------------------------------------------------------------
    # 执行原始程序获取执行结果
    print('\r %s %s - 获取原始执行输出' % (datetime.datetime.now(), describe), end='')
    singleout = Codeflaws().single('tcas', src_or, src_tests)
    if not singleout[0]:
        print('\r %s %s - 获取原始执行输出失败' % (datetime.datetime.now(), describe))
        return data_return
    else:
        # 原始错误程序输出频谱
        data_return.or_out = singleout[2]
        data_return.or_list = Codeflaws().get_list_from_out(data_return.true_out, singleout[2])

    # ----------------------------------------------------------------------------
    # 获取执行行
    print('\r %s %s - 获取执行' % (datetime.datetime.now(), describe), end='')
    singleout = Codeflaws().single('tcas', src_or, src_tests, data_return.or_list)
    if not singleout[0]:
        print('\r %s %s - 获取执行失败' % (datetime.datetime.now(), describe))
        # print('生成变异信息失败')
        return data_return
    # print(singleout)

    # ----------------------------------------------------------------------------
    # 生成一阶变异体
    mut_text = mbfl.Fom().fom_data('', src_or, singleout[1])
    muts = list(map(eval, mut_text.strip().split('\n')))


    # pre_del用时
    data_return.time_spend['pre_del'] = (datetime.datetime.now() - pre_del_s).microseconds
    # del用时开始
    del_s = datetime.datetime.now()

    # ----------------------------------------------------------------------------
    # 开始变异
    total_fom = len(muts)
    print('\r %s %s - 开始变异 fom num:' % (datetime.datetime.now(), describe), total_fom, end='')

    ltime = datetime.datetime.now()
    for i, mut in enumerate(muts):
        # if i % 10 == 0:
        #     print('%s %s/%s/%s' % (datetime.datetime.now(), describe, i, total_fom))
        print('\r %s %s/%s/%s  %s' % (datetime.datetime.now(), describe, i, total_fom, datetime.datetime.now()-ltime), end='')
        ltime = datetime.datetime.now()

        # 生成变异体文件
        src_mut = os.path.join(os.getcwd(), 'report', 'CHMBFL', 'fom', '%s-%s.c' % (doc, i))
        if not mbfl.Fom().mutation_build(src_or, src_mut, mut):
            continue

        # 执行变异体
        st = datetime.datetime.now()
        singleout = Codeflaws().single("%s-%s" % (doc, i), src_mut, src_tests)
        if not singleout[0]:
            continue
        et = datetime.datetime.now()

        # 获取输出信息
        for mes in mut:
            if mes[0] not in data_return.out_dic:
                data_return.out_dic[mes[0]] = []
            data_return.out_dic[mes[0]].append(singleout[2])
        out = Codeflaws().get_list_from_out(data_return.true_out, singleout[2])

        # **********保存数据
        fom = util.Datasave().fom
        fom['message'] = mut
        fom['out_list'] = out
        fom['out_or'] = singleout[2]
        fom['time'] = (et - st).microseconds
        data_return.fom_list.append(fom)

    # del用时结束
    data_return.time_spend['del'] = (datetime.datetime.now() - del_s).microseconds

    data_return.fomnum = len(data_return.fom_list)

    # 可编译
    data_return.compile = True
    print('\r %s %s 执行一阶变异完成' % (datetime.datetime.now(), describe), end='')
    return data_return



if __name__ == '__main__':
    perdef()
    main()
