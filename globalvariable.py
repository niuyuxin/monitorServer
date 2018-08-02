#/usb/bin/eny python3



class GlobalVal():
    monitorSubDevDict = {} # 所有监视器内的设备
    deviceStateList = {}  # 设备状态列表
    singleCtrlOperation = 0 # 单控运行标志
    singleCtrlSpeed = 0