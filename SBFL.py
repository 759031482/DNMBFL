import os
import sys
import  re
import util
import time
import  datetime
from subprocess import Popen, PIPE
import subprocess
import numpy as np
import json
# import ijson
import random
from concurrent.futures import ThreadPoolExecutor
import threading

import sbfl.command as sbfl
import mbfl.command as mbfl
import mbfl.mbfl_for as mbfl_for
from codeflaws_version_control import Qr_excel
from data_codeflaws import Codeflaws




def perdef():

    global continueread
    continueread = True

    # 版本控制信息
    global vc_path
    vc_path = './report/data_codeflaws.xlsx'
    global sheet
    # sheet = 'muti'
    sheet = 'single'
    global json_path
    json_path = './report/SBFL'
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
            # 跳过无法编译文件
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
        data_return = single_sbfl(src, doc, Fault_Record, describe)

        resdoc = data_return.doc
        if not data_return.compile:
            continue

        # ----------------------------------------------------------------------------
        # json
        date_json = dict()
        date_json[resdoc] = dict()

        date_json[resdoc]['or_out'] = data_return.or_out
        date_json[resdoc]['sbfl'] = data_return.sbfl



        date_json[resdoc]['Fault_Record'] = Fault_Record
        date_json[resdoc]['compile'] = data_return.compile
        date_json[resdoc]['path'] = data_return.path
        date_json[resdoc]['true_out'] = data_return.true_out
        date_json[resdoc]['or_list'] = data_return.or_list
        date_json[resdoc]['out_dic'] = data_return.out_dic
        date_json[resdoc]['time_spend'] = data_return.time_spend
        date_json[resdoc]['testcase'] = data_return.testcase


        # ********存储数据
        path = os.path.join(json_path, json_name % resdoc)
        with open(path, 'w') as f_obj:
            json.dump(date_json, f_obj)
        print('%s %s 存储完成' % (datetime.datetime.now(), path))

        # ********删除无效数据
        del Fault_Record
        del doc
        del describe
        del data_return
        del resdoc
        del date_json
        del path


def main2():
    # codeflaws
    src = os.path.join(os.getcwd(), 'cdata', 'version')
    print(src)


    # 读取版本控制信息
    date_read = Qr_excel().read_old(vc_path, sheet)

    # 版本控制文件读取标记
    i = -1

    # 开始循环
    while i < len(date_read)-1:
        i += 1

        Fault_Record = eval(date_read[i, 1])
        doc = date_read[i, 0]
        describe = str(doc) + '-' + str(i)

        if not 'Fom_%s_Feature.json' % doc in os.listdir('./report/CHMBFL/mutinfo-single'):
            continue

        if continueread:
            havedoc = False
            for file in os.listdir(json_path):
                if doc in file:
                    havedoc = True
            if havedoc:
                continue
        data_return = single_sbfl(src, doc, Fault_Record, describe)

        resdoc = data_return.doc
        if not data_return.compile:
            continue

        # ----------------------------------------------------------------------------
        # json
        date_json = dict()
        date_json[resdoc] = dict()

        date_json[resdoc]['or_out'] = data_return.or_out
        date_json[resdoc]['sbfl'] = data_return.sbfl



        date_json[resdoc]['Fault_Record'] = Fault_Record
        date_json[resdoc]['compile'] = data_return.compile
        date_json[resdoc]['path'] = data_return.path
        date_json[resdoc]['true_out'] = data_return.true_out
        date_json[resdoc]['or_list'] = data_return.or_list
        date_json[resdoc]['out_dic'] = data_return.out_dic
        date_json[resdoc]['time_spend'] = data_return.time_spend
        date_json[resdoc]['testcase'] = data_return.testcase


        # ********存储数据
        path = os.path.join(json_path, json_name % resdoc)
        with open(path, 'w') as f_obj:
            json.dump(date_json, f_obj)
        print('%s %s 存储完成' % (datetime.datetime.now(), path))

        # ********删除无效数据
        del Fault_Record
        del doc
        del describe
        del data_return
        del resdoc
        del date_json
        del path


def single_sbfl(src, doc, Fault_Record, describe):
    # ----------------------------------------------------------------------------
    # 初始化数据
    data_return = util.Datasave()


    src_doc = os.path.join(src, doc, 'test_data')  # 题目路径
    src_true = os.path.join(src_doc, 'true_root', 'source', 'tcas.c')  # 正确程序路径
    src_or = os.path.join(src_doc, 'defect_root', 'source', 'tcas.c')  # 故障程序路径
    src_tests = os.path.join(src_doc, 'inputs')  # 测试用例路径

    data_return.path = src_or
    data_return.doc = doc
    data_return.Fault_Record = Fault_Record
    pre_del_s = datetime.datetime.now()


    date = util.Datasave().mbfl

    # ----------------------------------------------------------------------------
    # 执行真实程序获取真实执行结果
    print('%s - 获取真实执行输出' % describe)
    singleout = Codeflaws().single('tcas', src_true, src_tests)
    if not singleout[0]:
        print('%s - 获取真实执行输出失败' % doc)
        return data_return
    data_return.testcase, data_return.true_out = singleout[1], singleout[2]

    # ----------------------------------------------------------------------------
    # 执行原始程序获取执行结果及频谱信息
    print('%s - 获取原始执行输出及频谱信息' % describe)
    singleout = Codeflaws().single_cov('tcas', src_or, src_tests)
    if not singleout[0]:
        print('%s - 获取原始执行输出及频谱信息失败' % describe)
        return data_return

    or_out = singleout[1]

    data_return.or_out = or_out
    data_return.sbfl['cov'] = singleout[2]
    data_return.sbfl['time'] = singleout[4]
    data_return.or_list = Codeflaws().get_list_from_out(data_return.true_out, or_out)
    # ***********处理json数据
    date['sorce'] = data_return.or_list

    data_return.compile = True
    print('%s 完成' % describe)
    return data_return


def data_mix(main_json_docpath, sbfl_json_docpath):

    for file in os.listdir(main_json_docpath):
        main_json_path = os.path.join(main_json_docpath, file)
        sbfl_json_path = os.path.join(sbfl_json_docpath, file)

        print('执行 %s' % main_json_path)
        try:
            with open(main_json_path) as f_obj:
                data_json = json.load(f_obj)
            doc = list(data_json.keys())[0]
        except:
            print('读取错误 %s ' % main_json_path)
            continue

        if os.path.exists(sbfl_json_path):
            with open(sbfl_json_path) as f_obj:
                data_json_sbfl = json.load(f_obj)
            sbfl = data_json_sbfl[doc]['sbfl']
            del data_json_sbfl
            if 'sbfl' not in data_json[doc]:
                data_json[doc]['sbfl'] = sbfl

        if 'realfault' in data_json[doc]:
            Fault_Record = data_json[doc]['realfault']
            del data_json[doc]['realfault']
            data_json[doc]['Fault_Record'] = Fault_Record

        with open(main_json_path, 'w') as f_obj:
            json.dump(data_json, f_obj)
        print('存储完成 %s' % main_json_path)



def fix_realfault(main_json_docpath):

    date_read = Qr_excel().read(vc_path, sheet)
    for i in range(len(date_read)):
        file = 'data_%s.json' % date_read[i, 0]
        main_json_path = os.path.join(main_json_docpath, file)
        if not os.path.exists(main_json_path):
            print('不存在 %s '% main_json_path)
            continue
        Fault_Record = eval(date_read[i, 1])
        print('读取 %s' % main_json_path, end='')
        try:
            with open(main_json_path) as f_obj:
                data_json = json.load(f_obj)
        except:
            continue
        doc = list(data_json.keys())[0]

        data_json[doc]['Fault_Record'] = Fault_Record
        with open(main_json_path, 'w') as f_obj:
            json.dump(data_json, f_obj)
        print('\r 存储完毕 %s' % main_json_path, end='')
        print('\n %s %s' % (file, Fault_Record))





if __name__ == '__main__':
    perdef()
    # main()
    main2()
    # data_mix(r'report/DSA/random', r'report/SBFL')
    # fix_realfault(r'report/DSA/random')
    print('end')
