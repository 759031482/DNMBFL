# Claster Based High Order Mutatiuon Based Fault Location
import os
import sys
import re

import data_codeflaws
import util
import time
import datetime
from subprocess import Popen, PIPE
import subprocess
import numpy as np
import json
import random


import sbfl.command as sbfl
import mbfl.command as mbfl
from codeflaws_version_control import Qr_excel
from concurrent.futures import ThreadPoolExecutor
from data_codeflaws import Codeflaws

# 全局信息
import CHMBFL
# from CHMBFL_Flow.Cluster_Fom import cluster_sameline


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
    print('%s - 获取真实执行输出' % describe)
    singleout = Codeflaws().single('tcas', src_true, src_tests)
    if not singleout[0]:
        print('%s - 获取真实执行输出失败' % doc)
        return data_return
    else:
        # 全体测试用例信息， 正确程序执行输出
        data_return.testcase, data_return.true_out = singleout[1], singleout[2]

    # ----------------------------------------------------------------------------
    # 执行原始程序获取执行结果
    print('%s - 获取原始执行输出' % describe)
    singleout = Codeflaws().single('tcas', src_or, src_tests)
    if not singleout[0]:
        print('%s - 获取原始执行输出失败' % describe)
        return data_return
    else:
        # 原始错误程序输出频谱
        data_return.or_out = singleout[2]
        data_return.or_list = Codeflaws().get_list_from_out(data_return.true_out, singleout[2])

    # ----------------------------------------------------------------------------
    # 获取执行行
    print('%s - 获取执行' % describe)
    singleout = Codeflaws().single('tcas', src_or, src_tests, data_return.or_list)
    if not singleout[0]:
        print('%s - 获取执行失败' % describe)
        # print('生成变异信息失败')
        return data_return
    # print(singleout)

    # ----------------------------------------------------------------------------
    # 生成一阶变异体
    mut_text = mbfl.Fom().fom_data('', src_or, singleout[1])
    muts = list(map(eval, mut_text.strip().split('\n')))

    # ----------------------------------------------------------------------------
    # 使用一阶变异数据进行全随机变异
    # hom_path = r'./report/c/Hom-%s-original.txt' % doc
    # hom_path = mbfl.Mutation().random_hmbfl(fompath, hom_path)

    # pre_del用时
    data_return.time_spend['pre_del'] = (datetime.datetime.now() - pre_del_s).microseconds
    # del用时开始
    del_s = datetime.datetime.now()

    # ----------------------------------------------------------------------------
    # 开始变异
    total_fom = len(muts)
    print('%s - 开始变异 \n fom num:' % describe, total_fom)

    for i, mut in enumerate(muts):
        if i % 10 == 0:
            print('%s -fom %s/%s/%s' % (datetime.datetime.now(), describe, i, total_fom))

        # 生成变异体文件
        src_mut = os.path.join(os.getcwd(), 'report', 'CHMBFL', 'fom', '%s-%s.c' % (doc, i))
        if not mbfl.Fom().mutation_build(src_or, src_mut, mut):
            continue

        # 执行变异体
        st = datetime.datetime.now()
        singleout = Codeflaws().single("%s-%s" % (doc, i), src_mut, src_tests, True)
        if not singleout[0]:
            continue
        et = datetime.datetime.now()

        # 获取输出信息
        out = Codeflaws().get_list_from_out(data_return.true_out, singleout[2])
        kill = Codeflaws().get_list_from_out(data_return.or_out, singleout[2])

        # **********保存数据
        fom = util.Datasave().fom
        fom['message'] = mut
        fom['spectrum'] = singleout[1]
        fom['out_list'] = out
        fom['kill_list'] = kill
        # fom['out_or'] = singleout[2]
        fom['time'] = (et - st).microseconds
        data_return.fom_list.append(fom)

    # del用时结束
    data_return.time_spend['del'] = (datetime.datetime.now() - del_s).microseconds

    data_return.fomnum = len(data_return.fom_list)

    # 可编译
    data_return.compile = True
    print('%s 执行一阶变异完成' % describe)
    return data_return


def single_hom_part(date_json, describe):
    # 使用的hom列表在文件中对应的key
    # hom_key = "hom_list"
    hom_key = "hom_list_all"

    # 数据预处理
    doc = list(date_json.keys())[0]
    data = date_json[doc]
    src_path = data['path']
    src_tests = data['src_tests']

    hom_list = data[hom_key]

    new_hom_list = []
    hom_out_list = []

    # ----------------------------------------------------------------------------
    # 开始变异
    del_s = datetime.datetime.now()
    total_hom = len(hom_list)
    if total_hom > 30000:
        print('变异体数量过大 跳过')
        return False

    print('%s - 开始变异 \n hom num:' % describe, total_hom)
    for i, mut in enumerate(hom_list):
        if i % 20 == 0:
            print('%s -hom %s/%s/%s' % (datetime.datetime.now(), describe, i, total_hom))

        # 跳过无法变异hom
        src_mut = os.path.join(os.getcwd(), 'report', 'CHMBFL', 'fom', '%s-%s.c' % (doc, i))
        if not mbfl.Fom().mutation_build(src_path, src_mut, mut['message']):
            continue

        # 执行变异体
        st = datetime.datetime.now()
        singleout = Codeflaws().single("%s-%s" % (doc, i), src_mut, src_tests, True)
        if not singleout[0]:
            continue
        et = datetime.datetime.now()

        # 获取输出信息
        out = Codeflaws().get_list_from_out(data['true_out'], singleout[2])
        kill = Codeflaws().get_list_from_out(data['or_out'], singleout[2])


        # **********保存数据
        new_hom_list.append(mut)
        mut['out_list'] = out
        # mut['out_or'] = singleout[2]
        mut['kill_list'] = kill
        mut['time'] = (et - st).microseconds
        hom_out_list.append(mut)

    data["time_spend"]["hom_del"] = (datetime.datetime.now() - del_s).microseconds
    data[hom_key] = new_hom_list
    data['hom_out_list'] = hom_out_list
    data['homnum'] = len(new_hom_list)
    date_json[doc] = data

    print('%s 执行二阶变异完成' % describe)
    return date_json


def single_hom(json_path, src, doc, Fault_Record, describe='undefine'):
    date_json = dict()
    # --------------------------------------------------------------------------------
    # 执行一阶变异体
    fom_Data = single_fom_part(src, doc, Fault_Record, describe)
    if not fom_Data.compile:
        return describe+'False'
    else:
        # 获取执行数据
        linelen = len(util.File().read_line(fom_Data.path))
        date_json[doc] = {}
        for name, value in vars(fom_Data).items():
            date_json[doc][name] = value
        date_json[doc]['linelen'] = linelen
        # 存储一阶执行获得的信息
        with open(json_path, 'w') as f_obj:
            json.dump(date_json, f_obj)
        print('%s 生成完成' % doc)

    # --------------------------------------------------------------------------------
    # 生成二阶变异体全集
    hom_return = mbfl.Mutation().all_hom_random(date_json)
    if not hom_return:
        print('%s-二阶变异体全集生成失败' % doc)
        return describe+'False'
    else:
        date_json = hom_return
        with open(json_path, 'w') as f_obj:
            json.dump(date_json, f_obj)
        print('%s-二阶变异体全集生成完成' % doc)

    # --------------------------------------------------------------------------------
    # 执行二阶变异体
    hom_out_return = single_hom_part(date_json, describe)
    if not hom_out_return:
        return describe+'False'
    if len(hom_out_return[doc]["hom_out_list"]) == 0:
        print('%s-二阶变异体执行失败' % doc)
        return describe+'False'
    else:
        date_json = hom_out_return
        with open(json_path, 'w') as f_obj:
            json.dump(date_json, f_obj)
        print('%s-二阶变异体执行完成' % doc)
    return describe+'True'


def savefile(file):
    saveabel, data_json = DElMutAddFunction(os.path.join(readpath, file))
    if saveabel:
        with open(os.path.join(savepath, file), 'w') as f_obj:
            json.dump(data_json, f_obj)
        print('存储成功 %s %s' % (savepath, file))
    else:
        with open(os.path.join(needaddpath, file), 'w') as f_obj:
            json.dump(data_json, f_obj)
        print('存储成功 %s %s' % (needaddpath, file))

def saveneedfile(file):
    saveabel, data_json = DelNeedAddFunction(os.path.join(readpath, file))
    with open(os.path.join(savepath, file), 'w') as f_obj:
        json.dump(data_json, f_obj)
    print('存储成功 %s %s' % (savepath, file))


def DElMutAddFunction(json_path):
    with open(json_path) as f_obj:
        data_json = json.load(f_obj)
    doc = list(data_json.keys())[0]
    true_out = data_json[doc]['true_out']
    or_out = data_json[doc]['or_out']
    or_list = data_json[doc]['or_list']
    src_or = data_json[doc]['path']
    if '/files' in src_or:
        src_or = src_or[:src_or.index('/files')]+src_or[src_or.index('/files')+6:]
    src_tests = data_json[doc]['src_tests']
    if '/files' in src_tests:
        src_tests = src_tests[:src_tests.index('/files')]+src_tests[src_tests.index('/files')+6:]


    fom_list = data_json[doc]['fom_list']
    hom_list_all = data_json[doc]['hom_list_all']
    hom_out_list = data_json[doc]['hom_out_list']
    if len(hom_out_list) == 0:
        # 高阶信息未执行，暂时不处理
        return False, data_json

    # ----------------------------------------------------------------------------
    # 获取执行行
    print('%s - 获取执行' % doc)
    singleout = Codeflaws().single('tcas', src_or, src_tests, or_list)
    if not singleout[0]:
        print('%s - 获取执行失败' % doc)
        singleout = [True,[]]

    # ----------------------------------------------------------------------------
    # 生成补充的一阶变异体
    mut_text = mbfl.Fom().fom_data('', src_or, singleout[1])
    muts = list(map(eval, mut_text.strip().split('\n')))

    fom_list_simple = list(map(lambda x: x['message'], fom_list))
    hom_all_simple = list(map(lambda x: sorted(x['message'], key=lambda x: x[0]), hom_list_all))
    hom_execute_simple = list(map(lambda x: sorted(x['message'], key=lambda x: x[0]), hom_out_list))

    fom_list_add = []
    for mut_i, mut in enumerate(muts):
        if mut_i%20 == 0:
            print('%s -fom %s/%s/%s' % (datetime.datetime.now(), doc, mut_i, len(muts)))
        if mut in fom_list_simple:
            # print('%s -fom %s/%s/%s ---pass' % (datetime.datetime.now(), doc, mut_i, len(muts)))
            continue
        # 生成变异体文件
        src_mut = os.path.join(os.getcwd(), 'report', 'CHMBFL', 'fom', '%s-%s.c' % (doc, mut_i))
        if not mbfl.Fom().mutation_build(src_or, src_mut, mut):
            continue

            # 执行变异体
        st = datetime.datetime.now()
        singleout = Codeflaws().single("%s-%s" % (doc, mut_i), src_mut, src_tests, True)
        if not singleout[0]:
            continue
        et = datetime.datetime.now()

        # 获取输出信息
        out = Codeflaws().get_list_from_out(true_out, singleout[2])
        kill = Codeflaws().get_list_from_out(or_out, singleout[2])

        # **********保存数据
        fom = util.Datasave().fom
        fom['message'] = mut
        fom['spectrum'] = singleout[1]
        fom['out_list'] = out
        fom['kill_list'] = kill
        fom['time'] = (et - st).microseconds
        fom_list_add.append(fom)
    data_json[doc]['fom_list'] += fom_list_add
    print('补充数量 %s' % len(fom_list_add))
    print('生成补充高阶')
    hom_add = []
    for fom_add in fom_list_add:
        for fom_old in fom_list:
            if not data_codeflaws.MutationRule(fom_add['message'][0], fom_old['message'][0]):
                continue
            som = sorted([fom_add['message'][0], fom_old['message'][0]], key=lambda x: x[0])
            if not som in hom_all_simple:
                hom = util.Datasave().hom
                hom['message'] = som
                hom_list_all.append(som)
            if not som in hom_execute_simple:
                hom_add.append(som)
        fom_list.append(fom_add)

    data_json[doc]['hom_list_all'] = hom_list_all
    if len(hom_add) > 15000:

        print('数量过大跳过')
        return False, data_json

    for i, mut in enumerate(hom_add):
        if i %20 == 0:
            print('%s -hom %s/%s/%s' % (datetime.datetime.now(), doc, i, len(hom_add)))
        # 跳过无法变异hom
        src_mut = os.path.join(os.getcwd(), 'report', 'CHMBFL', 'fom', '%s-%s.c' % (doc, i))
        if not mbfl.Fom().mutation_build(src_or, src_mut, mut):
            continue

        # 执行变异体
        st = datetime.datetime.now()
        singleout = Codeflaws().single("%s-%s" % (doc, i), src_mut, src_tests, True)
        if not singleout[0]:
            continue
        et = datetime.datetime.now()

        # 获取输出信息
        out = Codeflaws().get_list_from_out(true_out, singleout[2])
        kill = Codeflaws().get_list_from_out(or_out, singleout[2])

        # **********保存数据
        hom = util.Datasave().hom
        hom['message'] = mut
        hom['out_list'] = out
        hom['kill_list'] = kill
        hom['time'] = (et - st).microseconds
        hom_out_list.append(hom)

    data_json[doc]['hom_out_list'] = hom_out_list

    return True, data_json

def DelNeedAddFunction(json_path):
    with open(json_path) as f_obj:
        data_json = json.load(f_obj)
    doc = list(data_json.keys())[0]
    true_out = data_json[doc]['true_out']
    or_out = data_json[doc]['or_out']
    or_list = data_json[doc]['or_list']
    src_or = data_json[doc]['path']
    if '/files' in src_or:
        src_or = src_or[:src_or.index('/files')]+src_or[src_or.index('/files')+6:]
    src_tests = data_json[doc]['src_tests']
    if '/files' in src_tests:
        src_tests = src_tests[:src_tests.index('/files')]+src_tests[src_tests.index('/files')+6:]


    fom_list = data_json[doc]['fom_list']
    hom_list_all = data_json[doc]['hom_list_all']
    hom_out_list = data_json[doc]['hom_out_list']
    if len(hom_out_list) == 0:
        print('数据缺失')
        # 高阶信息未执行，暂时不处理
        return False, data_json

    # ----------------------------------------------------------------------------
    hom_all_simple = list(map(lambda x: sorted(x['message'], key=lambda x: x[0]), hom_list_all))
    hom_execute_simple = list(map(lambda x: sorted(x['message'], key=lambda x: x[0]), hom_out_list))


    print('生成补充高阶')
    hom_add = []
    for i1, fom_1 in enumerate(fom_list):
        for i2, fom_2 in enumerate(fom_list):
            if i1 <= i2:
                continue
            if not data_codeflaws.MutationRule(fom_1['message'][0], fom_2['message'][0]):
                continue
            som = sorted([fom_1['message'][0], fom_2['message'][0]], key=lambda x: x[0])
            if not som in hom_all_simple:
                hom = util.Datasave().hom
                hom['message'] = som
                hom_list_all.append(som)
            if not som in hom_execute_simple:
                hom_add.append(som)


    data_json[doc]['hom_list_all'] = hom_list_all

    addnum = 0
    for i, mut in enumerate(hom_add):
        if i %20 == 0:
            print('%s -hom %s/%s/%s' % (datetime.datetime.now(), doc, i, len(hom_add)))
        # 跳过无法变异hom
        src_mut = os.path.join(os.getcwd(), 'report', 'CHMBFL', 'fom', '%s-%s.c' % (doc, i))
        if not mbfl.Fom().mutation_build(src_or, src_mut, mut):
            continue

        # 执行变异体
        st = datetime.datetime.now()
        singleout = Codeflaws().single("%s-%s" % (doc, i), src_mut, src_tests, True)
        if not singleout[0]:
            continue
        et = datetime.datetime.now()

        # 获取输出信息
        out = Codeflaws().get_list_from_out(true_out, singleout[2])
        kill = Codeflaws().get_list_from_out(or_out, singleout[2])

        # **********保存数据
        hom = util.Datasave().hom
        hom['message'] = mut
        hom['out_list'] = out
        hom['kill_list'] = kill
        hom['time'] = (et - st).microseconds
        hom_out_list.append(hom)
        addnum += 1

    data_json[doc]['hom_out_list'] = hom_out_list
    print('%s添加：%s' % (doc, addnum))
    return True, data_json









readpath = 'report/CHMBFL/mutinfo'
savepath = 'report/CHMBFL/mutinfo-new'
needaddpath = 'report/CHMBFL/mutinfo-needadd'
def main():
    # 创建线程池
    executor = ThreadPoolExecutor(max_workers=CHMBFL.max_workers)
    task = []

    for file in os.listdir(needaddpath):
        if file in os.listdir(savepath):
            continue
        # t = executor.submit(savefile, file)
        t = executor.submit(saveneedfile, file)
        while not t.done():
            time.sleep(3)


if __name__ == '__main__':
    main()