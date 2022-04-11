import os

# 清除gcov命令行产生的多余文件
def clear_gcov_file():
    suffixs = ['.gcov', '.exe', '.gcda', '.gcno', '.out']
    for version in os.listdir('./cdata/version'):
        if '.' in version:
            continue
        defect_root = os.path.join('./cdata/version', version, 'test_data/defect_root/source')
        true_root = os.path.join('./cdata/version', version, 'test_data/true_root/source')
        for file in os.listdir(defect_root):
            for suffix in suffixs:
                if suffix in file:
                    removepath = os.path.join(defect_root, file)
                    os.remove(removepath)
                    print(removepath)
        for file in os.listdir(true_root):
            for suffix in suffixs:
                if suffix in file:
                    removepath = os.path.join(true_root, file)
                    os.remove(removepath)
                    print(removepath)

    for file in os.listdir('./mbfl/fom'):
        filepath = os.path.join('./mbfl/fom', file)
        print(filepath)
        os.remove(filepath)

    print('删除完成')



def del_datalack_version():
    src_path = os.path.join(os.getcwd(), r'report/DSA/random')
    for file in os.listdir(src_path):
        filepath = os.path.join(src_path, file)

        havehom = 0

        objects = ijson.parse(open(filepath, 'r'))
        for v in objects:
            # if 'homs' in v[0] and ('end' not in v[1] or 'start' not in v[1]):
            if 'homs' in v[0]:
                havehom += 1
            if havehom > 3:
                break
        if havehom > 3:
            continue
        else:
            print(file, False)
        # break
    return

# 将dsa数据与一阶数据结合
def combin_fomdata():
    oripath = r'/home/cyxy/access/report/DSA/random'
    fompath = r'/home/cyxy/access/report/MBFL'

    for filename in os.listdir(oripath):

        fomfilepath = os.path.join(fompath, filename)
        orifilepath = os.path.join(oripath, filename)
        if not os.path.exists(fomfilepath):
            print('%s %s fom不存在' % (datetime.datetime.now(), filename))
            continue

        try:
            with open(fomfilepath) as f_obj:
                data_fom_json = json.load(f_obj)
            f_obj.close()
        except:
            print('%s ---------------------- %s 读取异常' % (datetime.datetime.now(), fomfilepath))
            continue

        doc = list(data_fom_json.keys())[0]
        fomlist = data_fom_json[doc]['fom_list']
        del data_fom_json

        new_fomlist = []
        while len(fomlist) > 0:
            fom = fomlist.pop(0)
            del fom['claster']
            del fom['spectrum']
            new_fomlist.append(fom)

        try:
            with open(orifilepath) as f_obj:
                data_json = json.load(f_obj)
            f_obj.close()
        except:
            print('%s ---------------------- %s 读取异常' % (datetime.datetime.now(), orifilepath))
            del new_fomlist
            continue

        doc = list(data_json.keys())[0]
        data_json[doc]['fom_list'] = new_fomlist
        del new_fomlist

        with open(orifilepath, 'w') as f_obj:
            json.dump(data_json, f_obj)
        print('%s %s 存储完成' % (datetime.datetime.now(), filename))
    return

# 修改chmbfl的一阶数据
def reset_fomdata():
    oripath = r'/home/cyxy/access/report/CHMBFL/mutinfo'

    for filename in os.listdir(oripath):

        orifilepath = os.path.join(oripath, filename)

        try:
            with open(orifilepath) as f_obj:
                data_json = json.load(f_obj)
            f_obj.close()
        except:
            print('%s ---------------------- %s 读取异常' % (datetime.datetime.now(), orifilepath))
            continue

        doc = list(data_json.keys())[0]
        fomlist = data_json[doc]['fom_list']

        new_fomlist = []
        while len(fomlist) > 0:
            fom = fomlist.pop(0)
            if 'claster' in fom:
                del fom['claster']

            if 'Feature' in fom:
                Feature = fom['Feature']
                del fom['Feature']
                for key, value in Feature.items():
                    fom[key] = value
            new_fomlist.append(fom)


        data_json[doc]['fom_list'] = new_fomlist
        del new_fomlist

        with open(orifilepath, 'w') as f_obj:
            json.dump(data_json, f_obj)
        print('%s %s 存储完成' % (datetime.datetime.now(), filename))
    return

# 将dsa数据与sbfl数据结合
def combin_sbfldata():
    oripath = r'/home/cyxy/access/report/DSA/random'
    sbflpath = r'/home/cyxy/access/report/SBFL'

    for filename in os.listdir(oripath):
        doc = filename[4:-13]

        # sbflfilepath = os.path.join(sbflpath, 'data_%s.json' % doc)
        sbflfilepath = os.path.join(sbflpath, filename)
        orifilepath = os.path.join(oripath, filename)
        if not os.path.exists(sbflfilepath):
            print('%s %s sbfl不存在' % (datetime.datetime.now(), filename))
            continue

        try:
            with open(sbflfilepath) as f_obj:
                data_sbfl_json = json.load(f_obj)
            f_obj.close()
        except:
            print('%s ---------------------- %s 读取异常' % (datetime.datetime.now(), sbflfilepath))
            continue

        doc = list(data_sbfl_json.keys())[0]
        sbfldata = data_sbfl_json[doc]['sbfl']
        del data_sbfl_json

        try:
            with open(orifilepath) as f_obj:
                data_json = json.load(f_obj)
            f_obj.close()
        except:
            print('%s ---------------------- %s 读取异常' % (datetime.datetime.now(), orifilepath))
            continue

        doc = list(data_json.keys())[0]
        data_json[doc]['sbfl'] = sbfldata

        with open(orifilepath, 'w') as f_obj:
            json.dump(data_json, f_obj)
        print('%s %s 存储完成' % (datetime.datetime.now(), filename))
    return

def reset_fhomdata():
    oripath = r'/home/cyxy/access/report/DSA/random'

    for filename in os.listdir(oripath):
        orifilepath = os.path.join(oripath, filename)

        try:
            with open(orifilepath) as f_obj:
                data_json = json.load(f_obj)
        except:
            print('%s ---------------------- %s 读取异常' % (datetime.datetime.now(), orifilepath))
            continue

        doc = list(data_json.keys())[0]
        if 'homs' in data_json[doc] and 'hom_list_all' not in data_json[doc]:
            hom_list_all = data_json[doc]['homs']
            del data_json[doc]['homs']
            for i, hom in enumerate(hom_list_all):
                hom['message'] = eval(hom['message'])
                hom_list_all[i] = hom
            data_json[doc]['hom_list_all'] = hom_list_all

        with open(orifilepath, 'w') as f_obj:
            json.dump(data_json, f_obj)
        print('%s %s 存储完成' % (datetime.datetime.now(), filename))



if __name__ == '__main__':
    clear_gcov_file()
