
#生成数据，然后进行模拟Tor，带有信誉机制

from __future__ import division
import xlrd
import pandas as pd
import openpyxl
from openpyxl import Workbook
import os

import time
import numpy as np
import matplotlib.pyplot as plt
import random



alpha = 100000
mu = 2.0                    #好中继
nu = 1.0                    #恶意中继
xi = 0.0                    #累计偏差

#计算每个中继的信誉
def eval(total_result):
    xi = 0.0                    #累计偏差
    col_result = []     #保留中继每一次的计算结果
    col_result.append(1.0)          #初始值为1.0，代表为好中继
    
    for i in range(0, len(total_result), 10):
        
        #print(total_result[1][i])
        item = total_result[i]    

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
            alpha = round(0.5 * delta/ (1 + xi), 5) 
        #print(delta)
        #print(alpha * item * p, (1 - alpha) * col_result[-1] * p)
        r = round(alpha * item  +  (1 - alpha) * col_result[-1] , 5)
        #print((1-alpha) * item, alpha * col_result[-1] * p)
        col_result.append(r)
    return col_result

def data():
    total_result = []      #保留所有中继的计算结果
    for j in range(1500):
        row = [1]
        for i in range(10000):
            tmp = random.randint(0,alpha)
            if tmp ==  1:
                row.append(-row[-1])
            else:
                row.append(row[-1])
        total_result.append(row)
    return total_result
     
if __name__ == '__main__':

    total_result = data()      #保留所有中继的计算结果
    
    print("end create data")
    #计算信誉值
    finger_result = []      #保留所有中继的信誉计算结果
    for i in range(len(total_result)):
        finger_result.append(eval(total_result[i]))
    print("end calculate reputation")

    #开始模拟，当信誉低于-0.2时将结点剔除
    res1 = []                    #存储tor中继个数
    res2 = []                    #存储有状态变化的结点个数
    res3 = []                    #存储剔除的结点的个数

    row = len(finger_result)
    col = len(finger_result[0])
    res1.append(row)
    res2.append(0)
    res3.append(0)

    #按列进行扫描
    for j in range(len(finger_result[0])):
        tmp = 0                                 #存储良好的结点个数
        tmp1 = 0                                #存储有状态变化的结点个数
        tmp2 = 0                                #存储剔除的结点的个数
        for i in range(row-1, -1, -1):
            if finger_result[i][j] <= 0.3:
                finger_result.pop(i)
                tmp2 = tmp1 + 1
                row = row - 1
        res3.append(tmp2 + res3[-1])
        res1.append(len(finger_result))
    plt.subplot(111)
    plt.plot(res1,'-g', label='Available')
    #plt.plot(res2,color='g', linestyle='-')
    plt.plot(res3,'-k', label='Remove')
    plt.legend(loc=0)

    plt.title('reputation simulation')
    plt.xlabel("time") #xlabel、ylabel：分别设置X、Y轴的标题文字。
    plt.ylabel("rely numbers")
    #plt.show()
    plt.savefig('reputation_model.png',dpi = 120,bbox_inches='tight') 

    '''
    wb = openpyxl.Workbook()
    ws = wb.active
    for r in range(len(finger_result)):
        for c in range(len(finger_result[0])):
            ws.cell(r + 1, c + 1).value = finger_result[r][c]
            # excel中的行和列是从1开始计数的，所以需要+1
    wb.save("./repution.xls")  # 注意，写入后一定要保存
    '''
    '''
    x = []
    for i in range(len(col_result)):
        x.append(i + 2)
    plt.plot(x, col_result,color='r', linestyle='-')

    plt.xlabel("time") #xlabel、ylabel：分别设置X、Y轴的标题文字。
    plt.ylabel("score")
    plt.savefig('交替恶意.png',dpi=120,bbox_inches='tight') 

    '''
