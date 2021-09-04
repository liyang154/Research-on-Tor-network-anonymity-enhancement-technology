#模拟现有Tor结点消亡

import scipy.integrate as spi
import numpy as np
#import pylab as pl
import matplotlib.pyplot as pl


alpha=0.00001           #中继恶意概率
beta=0.0011286          #恶意中继被剔除概率
#beta=0.2
TS=1.0 #观察间隔
ND=1000 #观察结束日期
S0=1500 #初始中继个数
I0=1 #初始恶意中继
INPUT = (S0, I0, 0.0)
def diff_eqs(INP,t):
    '''The main set of equations'''
    Y=np.zeros((3))
    V = INP
    Y[0] = - alpha * V[0] * V[1]
    Y[1] = alpha * V[0] * V[1] - beta * V[1]
    Y[2] = beta * V[1]
    return Y
t_start = 0.0
t_end = ND
t_inc = TS
t_range = np.arange(t_start, t_end+t_inc, t_inc) #生成日期范围
RES = spi.odeint(diff_eqs,INPUT,t_range)
print(RES)

pl.subplot(111)
pl.plot(RES[:,0] + RES[:,1], '-g', label='Available')
#pl.plot(RES[:,1], '-r', label='Bad')
pl.plot(RES[:,2], '-k', label='Remove')
pl.legend(loc=0)
pl.title('tor simulation with SIR')
pl.xlabel('Time')
pl.ylabel('Numbers')
#pl.show()
pl.savefig('sir.png')

