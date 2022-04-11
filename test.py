import json
import math
import os

data_dirpath = '/home/cyxy/sir_result'

def version_path():
        passlist = [
            ['printtokens', 'two_faults', 'v2'],
            ['printtokens', 'two_faults', 'v3'],
            ['printtokens', 'two_faults', 'v4'],
            ['printtokens', 'two_faults', 'v5'],
            ['printtokens', 'four_faults', 'v2'],
            ['printtokens', 'four_faults', 'v3'],
            ['printtokens', 'five_faults', 'v2'],
            ['printtokens', 'five_faults', 'v3'],

            ['printtokens2', 'two_faults', 'v5'],
            ['printtokens2', 'four_faults', 'v5'],
            ['printtokens2', 'five_faults', 'v4'],
            ['printtokens2', 'five_faults', 'v5'],

            # ['printtokens', 'three_faults', 'v1'],
        ]

        pathlist = []
        for project in os.listdir(data_dirpath):
            if '.' in project:
                continue
            project_path = os.path.join(data_dirpath, project)
            for faultnum in os.listdir(project_path):
                if '.' in faultnum:
                    continue
                faultnum_path = os.path.join(data_dirpath, project, faultnum)
                for version in os.listdir(faultnum_path):
                    if '.' in version:
                        continue
                    addpath = [project, faultnum, version]
                    if addpath in passlist:
                        continue
                    pathlist.append([project, faultnum, version])
                    # print([project, faultnum, version])
        # return
        return pathlist



def test():

    def comparerule(path):
        filelist = [
            os.path.join(path, 'output', 'res_cov_matrix.in'),
            os.path.join(path, 'defect_root', 'Fault_Record.txt'),
            os.path.join(path, 'output', 'all_execute_mutant.txt'),
            os.path.join(path, 'output', 'res_original_version.in'),
            os.path.join(path, 'output', 'res_fault_version.in'),
            os.path.join(path, '_entire_randomization_higher_order_mutant_set', 'all_execute_mutant.txt'),
            os.path.join(path, '_entire_randomization_higher_order_mutant_set', 'res_original_version.in'),
            os.path.join(path, '_entire_randomization_higher_order_mutant_set', 'res_fault_version.in'),
            os.path.join(path, 'output', 'res_vector.in'),
        ]
        lack = False
        for file in filelist:
            if not os.path.exists(file):
                print(path, 'file lack', file)
                lack = True
        if lack:
            return False

        for file in os.listdir(os.path.join(path, 'defect_root', 'source')):
            if '.c' not in file:
                continue
            filelist.append(os.path.join(path, 'defect_root', 'source', file))

        cov = []
        with open(os.path.join(path, 'output', 'res_cov_matrix.in'), 'r') as f:
            for test_cov in f.readlines():
                cov_t = []
                try:
                    for line, covres in enumerate(map(lambda x:int(x), test_cov.strip())):
                        if covres == 1:
                            cov_t.append(line+1)
                    cov.append(cov_t)
                except:
                    continue

        # Fault_Record
        with open(os.path.join(path, 'defect_root', 'Fault_Record.txt'), 'r') as f:
            Fault_Record = list(map(lambda x: int(x.split(':')[0].split(' ')[1]), f.readlines()))

        # All First Order Mutant
        fom_list = []
        with open(os.path.join(path, 'output', 'all_execute_mutant.txt'), 'r') as f:
            fommessagelist = f.readlines()
        with open(os.path.join(path, 'output', 'res_original_version.in'), 'r') as f:
            fomoutlist = f.readlines()
        with open(os.path.join(path, 'output', 'res_fault_version.in'), 'r') as f:
            fomkilllist = f.readlines()
        if not len(fommessagelist) == len(fomoutlist) or not len(fomoutlist) == len(fomkilllist):
            print(path, 'fom', 'num error')
            return False


        # All Second Order Mutant
        hom_out_list = []
        with open(os.path.join(path, '_entire_randomization_higher_order_mutant_set', 'all_execute_mutant.txt'), 'r') as f:
            fommessagelist = f.readlines()
        with open(os.path.join(path, '_entire_randomization_higher_order_mutant_set', 'res_original_version.in'), 'r') as f:
            fomoutlist = f.readlines()
        with open(os.path.join(path, '_entire_randomization_higher_order_mutant_set', 'res_fault_version.in'), 'r') as f:
            fomkilllist = f.readlines()
        if not len(fommessagelist) == len(fomoutlist) or not len(fomoutlist) == len(fomkilllist):
            print(path, 'hom', 'num error')
            return False

        # or_list
        with open(os.path.join(path, 'output', 'res_vector.in'), 'r') as f:
            or_list = list(map(lambda x:int(x), f.readlines()[0].strip()))

        # line_len
        line_len = -1
        for file in os.listdir(os.path.join(path, 'defect_root', 'source')):
            if '.c' not in file:
                continue
            with open(os.path.join(path, 'defect_root', 'source', file), 'r') as f:
                line_len = len(f.readlines())
        if line_len == -1:
            print(path, 'line_len error')
            return False

        # print('%s 读取完成 %s' % (datetime.datetime.now(), path))

        return True

    for file_i, [project, faultnum, version] in enumerate(version_path()):
        path = os.path.join(data_dirpath, project, faultnum, version)

        # print(path)
        comparerule(path)
    print('end')


if __name__ == '__main__':
    # test()
    akf, akp, anf, anp = 27, 0, 10, 14
    print(akf/math.sqrt((akf+anf)*(akf+akp)))
        if(!(count>2 ||(lcount>=2 && count>=2)))

