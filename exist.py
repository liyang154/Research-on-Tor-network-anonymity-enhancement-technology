#计算每个中继的信誉值,
#一直恶意

from __future__ import division
import xlrd
import pandas as pd
import openpyxl
from openpyxl import Workbook

import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.path as mpath




mu = 2.0                    #好中继
nu = 1.0                    #恶意中继


class excel_read:
    def __init__(self, excel_path ,encoding='utf-8',index=0):
      
      self.data=xlrd.open_workbook(excel_path)  ##获取文本对象
      self.table=self.data.sheets()[index]     ###根据index获取某个sheet
      self.rows=self.table.nrows   ##3获取当前sheet页面的总行数,把每一行数据作为list放到 list
      self.cols = self.table.ncols
      self.finger = []

    def get_total_data(self):
        #获取当前扫描的数据信息，将指纹存储到finger内，所有信息存储到result内
        result=[]
        for i in range(self.rows):
            col=self.table.row_values(i)  ##获取每一列数据
            #print(col)
            result.append(col)
            self.finger.append(col[0])
        #print(result)
        return result

#计算每个中继的信誉
def eval(total_result):
    xi = 0.0                    #累计偏差
    col_result = []		#保留中继每一次的计算结果
    col_result.append(1.0)          #初始值为1.0，代表为好中继
    scan_time = 0
    total_time = 0
    for i in range(3,int(total_result[1]) + 3):
        total_time = total_time + 1
        #print(total_result[1][i])
        item = total_result[i]
        p = 1.0                             #扫描为好结果的概率
        if item != 0:
            scan_time = scan_time + 1      
        p = round(scan_time / total_time, 5)
        #求delta
        if item >= col_result[-1]:
            delta = round((item - col_result[-1])/mu, 5)
        elif item < col_result[-1]:
            delta = round((col_result[-1] - item)/nu, 5)
        else:
            delta = 0.0

        #求xi
        xi = xi + delta
        #print(p, xi)
        alpha = 0
        #求alpha
        if xi != 0.0:
            alpha = round(0.5 * delta/ (1 + xi), 5) * p
        #print(delta)
        #print(alpha * item * p, (1 - alpha) * col_result[-1] * p)
        r = round(alpha * item  +  (1 - alpha) * col_result[-1] , 5)
        #print((1-alpha) * item, alpha * col_result[-1] * p)
        col_result.append(r)
    return col_result
     
if __name__ == '__main__':

    #获取总的扫描信息
    total_excel = excel_read(r'./total.xls')
    total_result = total_excel.get_total_data()
    
    finger_result = []      #保留所有中继的计算结果
    for i in range(1, len(total_result)):
        finger_result.append(eval(total_result[i]))
    
    plt.plot(finger_result[272] ,"r", markersize=1)

    plt.title('exit malicious rely reputation')
    plt.xlabel("time") #xlabel、ylabel：分别设置X、Y轴的标题文字。
    plt.ylabel("score")
    
    #plt .show()
    plt.savefig('存在恶意.png',dpi = 120,bbox_inches='tight') 