# Claster Based High Order Mutatiuon Based Fault Location
# 入口文件
import sys
import datetime
import socket
import json


# 测试环境 test 或 非测试环境
environment = 'test'

# 程序中断是否继续运行
continueread = True

# 版本控制信息
vc_path = './report/CHMBFL/data_codeflaws.xlsx'
sheet = 'single'

# 版本信息文件
doc_info_path = 'report/CHMBFL/mutinfo-single'
doc_info_name = 'Fom_%s_Feature.json'

# 多线程数量
max_workers = 1


def get_host_ip():
    try:
        s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        s.connect(('8.8.8.8',80))
        ip=s.getsockname()[0]
    finally:
        s.close()
    return ip


sys.path.append(r'/home/cyxy/files/access/CHMBFL_Flow')
sys.path.append(r'/home/cyxy/access/CHMBFL_Flow')
from CHMBFL_Flow import main_flow
import mbfl.command as mbfl


if __name__ == '__main__':
    main_flow.main()
    # main_flow.new_main()


