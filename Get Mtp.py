import os

from codeflaws_version_control import Qr_excel


def main():
    dir_path = './report/CHMBFL/susfile-single'
    # dir_path = './report/CHMBFL/susfile'
    method_list = [
        'baseline/Mbfl',
        'HomBaseline/Last2First-1000',
        'HomBaseline/DifferentOperator-1000',
        'HomBaseline/RandomMix-1000',
        'HomBaseline/Random-0_5',
        'DNMbfl/DeltaNsMbfl-1',
    ]
    for method in method_list:
        mtp = 0
        methodpath = os.path.join(dir_path, method, 'max')
        filepath = os.path.join(methodpath, os.listdir(methodpath)[0])
        data_read = Qr_excel().read(filepath, 'exam-average')
        for v_data in data_read:
            version = 'v%s' % v_data['self']['Version'].split('_')[0]
            if 'DNMbfl' in method:
                pnum = v_data['self']['Homnum'] + v_data['self']['Fomnum']
            elif method == 'baseline/Mbfl':
                pnum = v_data['self']['Fomnum']
            else:
                pnum = v_data['self']['Homnum']
            testnum = len(os.listdir(os.path.join('./cdata/version/%s/test_data/inputs' % version)))
            mtp += pnum*testnum
        print(method, mtp)
    return

if __name__ == '__main__':
    main()