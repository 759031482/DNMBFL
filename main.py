import os, sys, re
import util
import sbfl.command as sbfl
import mbfl.command as mbfl
import sbfl.sbfl_for as sbfl_for
import mbfl.mbfl_for as mbfl_for
import time,datetime
from subprocess import Popen, PIPE
import subprocess
import log

log = log.Log()




class Codeflaws:
    def __init__(self):
        self.path = ''  # 被测程序路径
        self.testcase = []  # 测试用例信息
        self.true_out = []  # 真实执行结果
        self.or_list = []  # 原始执行信息
        self.out_list = []  # 执行信息
        self.fom_list = []  # 变异信息
        self.out_dic = {}
        self.Fault_Record = []  # 真实故障


    def mysystem(self, cmd):
        # print(cmd)
        ps = subprocess.Popen(cmd, shell=True, stdout=PIPE, stderr=subprocess.STDOUT)
        ps.wait()
        out, err = ps.communicate()
        # print(out.decode("utf8","ignore"))
        if 'In function' in out.decode("utf8","ignore"):
            return False
        else:
            return True


        # os.system(cmd + r' 2> E:\Prgorams\Python\access\report\c\1.txt')
        #
        # while not os.path.exists(r'E:\Prgorams\Python\access\report\c\1.txt'):
        #     time.sleep(0.1)
        # with open(r'E:\Prgorams\Python\access\report\c\1.txt', 'r', encoding='utf-8') as f:
        #     text = f.read()
        # os.remove(r'E:\Prgorams\Python\access\report\c\1.txt')
        # if 'In function' in text:
        #     return False
        # else:
        #     return True



    def single(self, name, src_path, tests_path, cov=False):
        # cov = False 不获取覆盖信息
        # cov = all 获取全部覆盖信息
        # cov = list 执行失败测试用例覆盖信息
        # cov = i test_path 第i个测试用例

        test_src = []  # 测试用例路径
        true_out = []  # 执行结果
        gcov_path = src_path + '.gcov'
        true_com = util.Command(src_path)

        # 编译文件
        if not self.mysystem(true_com.compile(name)):
            # print('编译错误', src_path)
            return [False]

        if not cov:
            # 执行程序获取输出结果
            for test in os.listdir(tests_path):
                testcase = os.path.join(tests_path, test)
                test_src.append(testcase)
                self.mysystem(true_com.run(testcase))
                true_out.append(util.File().read(true_com.out))
                os.remove(true_com.out)
            return [True, test_src, true_out]

        for i, test in enumerate(os.listdir(tests_path)):
            if type(cov) == list and cov[i]:
                continue
            if type(cov) == int and not i == cov:
                continue
            testcase = os.path.join(tests_path, test)
            self.mysystem(true_com.run(testcase))

        self.mysystem(true_com.report())
        time.sleep(0.3)
        return self.read_gcov(gcov_path)


    def total_sbfl(self):
        return

    def read_gcov(self, path):
        info = []
        try:
            # 读取覆盖信息
            lines = util.File().read_line(path)
            for line in lines:
                line_cov = line.split(':', 2)
                line_cov[0] = line_cov[0].replace(' ', '')
                line_cov[1] = int(line_cov[1].replace(' ', ''))
                if line_cov[1] == 0:
                    continue
                try:
                    if int(line_cov[0]):
                        info.append(line_cov[1])
                except:
                    continue
                # print(line_cov)
            if len(info) == 0:
                # print('输出错误', path)
                return [False, info]
        except:
            # print('输出读取错误', path)
            return [False, info]
        return [True, info]


    def get_list_from_out(self, trueout, nowout):
        nowlist = []
        for i, out in enumerate(trueout):
            if out == nowout[i]:
                nowlist.append(True)
            else:
                nowlist.append(False)
        return nowlist


class Done_file:
    def __init__(self, res_path):
        self.donefile = []
        with open(res_path, 'r') as f:
            text = f.readlines()
        for i, res in enumerate(text):
            if not r'/mnt/hgfs' in res:
                continue
            if '\n' == res[-1:]:
                res = res[:-1]
            self.donefile.append(res)


# 通过tag文件获取真实故障信息
def tag_read_trueerror(tagpath):
    true_error = {}
    with open(tagpath, 'r') as f:
        text_lines = f.readlines()
    true_error['error_num'] = int(text_lines[2])
    true_error['error_lines'] = []
    for i in range(3, 3 + true_error['error_num']):
        true_error['error_lines'].append(text_lines[i].split('<TAG>')[1])
    return true_error, text_lines[0]


def sbfl_topline():
    with open('report/sbfl-sus.txt', 'r') as f:
        sus_sbfl = eval(f.read())
    max_sus = -1
    top_line = []
    for key in sus_sbfl:
        if sus_sbfl[key] > max_sus:
            max_sus = sus_sbfl[key]
            top_line = [key]
        elif sus_sbfl[key] == max_sus:
            top_line.append(key)
    print(top_line)
    return top_line


def sus2txt(respath, sus='', file=False, trueerror=''):
    if not file:
        with open(respath, 'w+') as f:
            f.write('')
    else:
        with open(respath, 'a') as f:
            f.write(str(file) + '\n')
            f.write(str(sus) + '\n')
            f.write(str(trueerror['error_lines']) + '\n\n')


def combin_sus(sbfl_res, mbfl_res):
    max_sus_sbfl = -1
    for key in sbfl_res:
        if sbfl_res[key] > max_sus_sbfl:
            max_sus_sbfl = sbfl_res[key]
    for key in mbfl_res:
        sbfl_res[key] = mbfl_res[key] + max_sus_sbfl
    print(sbfl_res)
    return sbfl_res


def access(mainmessage):
    try:
        mainmessage = sbfl.main(mainmessage)
        print('sbfl', mainmessage['sbfl']['sus'])
        with open('report/sbfl-sus.txt', 'w') as f:
            f.write(str(mainmessage['sbfl']['sus']))

        mainmessage['sbfl']['sbfltopline'] = sbfl_topline()

        mainmessage = mbfl.main(mainmessage)
        print('mbfl', mainmessage['mbfl']['sus'])
        with open('report/mbfl-sus.txt', 'w') as f:
            f.write(str(mainmessage['mbfl']['sus']))

        combin_res = combin_sus(mainmessage['sbfl']['sus'], mainmessage['mbfl']['sus'])
        sus2txt(mainmessage['resname'], combin_res, mainmessage['program_path'], mainmessage['true_error'])
        print('result:\n', str(combin_res) + '\n', str(mainmessage['program_path']) + '\n',
              str(mainmessage['true_error']) + '\n')
        return True
    except:
        return False







def loop():
    # codeflaws
    # w2py = util.W2py()
    stime = datetime.datetime.now()
    src = os.path.join(os.getcwd(), 'cdata', 'version')
    exam = 0
    tops = [0, 0, 0, 0, 0, 0]
    total = 0
    for doc in os.listdir(src):
        if '.' in doc:
            continue

        data_cf = Codeflaws()
        src_doc = os.path.join(src, doc, 'test_data')  # 题目路径
        data_cf.path = src_doc

        # 获取真实故障
        log.pt('获取真实故障 ', doc, '-----------------------------------------')
        # print('\n获取真实故障 ', doc, '-----------------------------------------')
        try:
            with open(os.path.join(data_cf.path, 'defect_root', 'Fault_Record.txt'), 'r') as f:
                text = f.read()
                for items in text.split('Line'):
                    try:
                        data_cf.Fault_Record.append(int(items))
                    except:
                        continue
        except:
            log.pt('读取真实故障失败')
            # print('读取真实故障失败')
            continue

        src_true = os.path.join(data_cf.path, 'true_root', 'source', 'tcas.c')
        src_or = os.path.join(data_cf.path, 'defect_root', 'source', 'tcas.c')
        src_tests = os.path.join(data_cf.path, 'inputs')

        # 执行真实程序获取真实执行结果
        log.pt('获取真实执行输出', '-----------------------------------------')
        # print('\n获取真实执行输出', '-----------------------------------------')
        singleout = Codeflaws().single('tcas', src_true, src_tests)
        if not singleout[0]:
            log.pt('获取真实执行输出失败')
            # print('获取真实执行输出失败')
            continue
        data_cf.testcase, data_cf.true_out = singleout[1], singleout[2]
        log.pt(data_cf.true_out)
        # print(data_cf.true_out)

        
        break


        # 执行原始程序获取执行结果
        log.pt('获取原始执行结果', '-----------------------------------------')
        # print('\n获取原始执行结果', '-----------------------------------------')
        singleout = Codeflaws().single('tcas', src_or, src_tests)
        if not singleout[0]:
            log.pt('获取原始执行输出失败')
            # print('获取原始执行输出失败')
            continue
        or_out = singleout[2]
        data_cf.or_list = Codeflaws().get_list_from_out(data_cf.true_out, or_out)
        log.pt(data_cf.or_list)
        # print(data_cf.or_list)


        # 生成变异信息
        singleout = Codeflaws().single('tcas', src_or, src_tests, data_cf.or_list)
        singleout = Codeflaws().single('tcas', src_or, src_tests, 'all')
        if not singleout[0]:
            log.pt('生成变异信息失败')
            # print('生成变异信息失败')
            continue
        or_out = singleout[1]
        mbfl.Fom().fom_data(src_or, or_out)

        # 开始变异
        log.pt('开始变异', '-----------------------------------------')
        # print('\n开始变异', '-----------------------------------------')
        for i,mut in enumerate(util.File().read_line(r'./report/c/Fom-original.txt')):
            src_mut = os.path.join(os.getcwd(), 'mbfl', 'fom', '%s-%s.c' % (doc, i))
            log.pt(False, src_mut)
            # print('\n', src_mut)
            if not mbfl.Fom().mutation_build(src_or, src_mut, eval(mut)):
                continue
            singleout = Codeflaws().single("%s-%s" % (doc, i), src_mut, src_tests)
            if singleout[0]:
                log.pt(False, singleout[2])
                out = Codeflaws().get_list_from_out(data_cf.true_out, singleout[2])
                if eval(mut)['line'] not in data_cf.out_dic:
                    data_cf.out_dic[eval(mut)['line']] = []

                data_cf.out_dic[eval(mut)['line']].append(out)
                data_cf.out_list.append(out)
                data_cf.fom_list.append(mut)

                log.pt(False, out)


        # 获取怀疑度元组信息
        log.pt('生成怀疑度', '-----------------------------------------')
        # print('\n生成怀疑度', '-----------------------------------------')
        touple = mbfl.get_toule(data_cf.or_list, data_cf.out_dic)
        log.pt(touple)
        # print(touple)
        sus_list = []
        for line in touple['f&p']:
            touple_list = touple['tf'], touple['f&p'][line]['f'], touple['f&p'][line]['p'], touple['f2p'], touple['p2f'],
            sus = mbfl_for.metallaxis(touple_list)
            sus_list.append([line, sus])
        sus_list_sort = sorted(sus_list, key = lambda x: x[1], reverse = True)
        log.pt(sus_list_sort)
        log.pt(False, sus_list_sort)
        # print('\n', sus_list_sort)

        # 计算评价指标
        log.pt('计算评价指标', '-----------------------------------------')
        # print('\n计算评价指标', '-----------------------------------------')
        sus_re = 0
        sus_tie = []
        for i, [line,sus] in enumerate(sus_list_sort):
            for ref in data_cf.Fault_Record:
                if ref == line and sus_re == 0:
                    sus_re = sus
            if sus_tie == []:
                sus_tie.append([sus,1])
            else:
                if sus == sus_tie[-1][0]:
                    sus_tie[-1][1] += 1
                else:
                    sus_tie.append([sus,1])
        ex = 0
        top = 0
        in_list = False
        for i,[sus,tie] in enumerate(sus_tie):
            if sus == sus_re:
                ex += tie/2
                in_list = True
                break
            else:
                top += tie
                ex += tie
        if in_list:
            exam += ex
            total += 1
            if top <= 1:
                tops[0] += 1
            elif top <= 3:
                tops[1] += 1
            elif top <=5:
                tops[2] += 1
            elif top <= 10:
                tops[3] += 1
            else:
                tops[4] += 1
        else:
            tops[5] += 1

        with open(r'./report/c/result.txt', 'a+') as f:
            out = str(datetime.datetime.now()) + ': \n  评估指标：exam = '+str(exam)+'total:'+str(total)+'tops:'+str(tops)+'times:'+str((datetime.datetime.now()- stime).seconds)
            f.write(out)
        log.pt(data_cf.Fault_Record)
        # print('\n', data_cf.Fault_Record)

        log.pt('评估指标：', 'exam = ', exam, 'total:', total, 'tops:', tops, 'times:', (datetime.datetime.now()- stime).seconds)
        # print('评估指标：', 'exam = ', exam, 'total:', total, 'tops:', tops, 'times:', (datetime.datetime.now()- stime).seconds)
        # break
        # util.File().clear(r'./mbfl/fom')





def loop2(mainmessage):
    # oj
    w2py = util.W2py()
    src = os.path.join(os.getcwd(), './data/data')
    for doc in os.listdir(src):  # 数据集路径
        src_doc = os.path.join(src, doc)  # 题目路径
        src_wa = os.path.join(src, doc, 'WA_c')  # 题目故障程序路径

        if len(os.listdir(os.path.join(src_doc, 'TEST_DATA_TCG1'))) > 10:
            # 判断测试用例数量是否大于10
            mainmessage['testdata_dirpath'] = os.path.join(src_doc, 'TEST_DATA_TCG1')
        else:
            if len(os.listdir(os.path.join(src_doc, 'TEST_DATA'))) > 10:
                mainmessage['testdata_dirpath'] = os.path.join(src_doc, 'TEST_DATA')
            else:
                continue

        for er_num in os.listdir(src_wa):
            src_ernum = os.path.join(src_wa, er_num)  # 故障数量分类路径
            for file in os.listdir(src_ernum):
                src_file = os.path.join(src_ernum, file)  # 文件路径
                if '.txt' not in file:
                    continue
                if len(w2py.dic) >= 200:  # 仅执行200个程序
                    return 0

                true_error, programname = tag_read_trueerror(src_file)
                # 真实故障行，程序名
                mainmessage['program_path'] = os.path.join(src_ernum, programname[:-1])
                mainmessage['true_error'] = true_error
                if programname in w2py.dic:
                    continue
                try:
                    head = {
                        'sbfl': {},
                        'mbfl': {},
                    }
                    mainmessage = sbfl.main(mainmessage)
                    head['sbfl'] = mainmessage['sbfl']['touple']

                    mainmessage = mbfl.main(mainmessage)
                    head['mbfl'] = mainmessage['mbfl']['touple']

                    w2py.dic[programname[:-1]] = head
                    w2py.write()  # 写入mbfl执行结果
                except:
                    continue


if not __name__ == '__main__':
    # oj
    mainmessage = {
        'program_path': '',  # 被执行程序路径
        'testdata_dirpath': '',  # 测试用例路径
        'true_error': '',  # 真实故障 list
        'resname': '',
        'execute': '',  # 被执行行 list
        # sbfl数据
        'sbfl': {
            'sbflform': sbfl_for.ochiai,  # sbfl公式
            'sbfltopline': [],  # sbfl最可以行 list
            'testres': [],
            'sus': '',  # sbfl怀疑度列表
            'touple': {},  # sbfl行元组信息
        },
        'mbfl': {
            'mbflform': mbfl_for.metallaxis,  # mbfl公式
            'fomdata': False,  # 是否已经生成变异信息
            'sus': '',  # mbfl怀疑度列表
            'touple': {},  # mbfl行元组信息
        },

    }
    loop2(mainmessage)
    # w2py = util.W2py()

if __name__ == '__main__':
    try:
        loop()
    except Exception as e:
        log.error(e)
