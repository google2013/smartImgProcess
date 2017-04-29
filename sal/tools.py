# -*- coding: utf-8 -*-
from __future__ import unicode_literals


import sys
#py3
pyv = sys.version_info.major
py3 = pyv == 3
if py3:
    __listRange__ = range
    range = lambda *x:list(__listRange__(*x))
    __rawOpen__ = open
    open = lambda *l:__rawOpen__(l[0],'r',-1,'utf8') if len(l) == 1 else __rawOpen__(l[0],l[1],-1,'utf8')

    
from os import listdir
import os
import pickle
import time
from time import time as t

import numpy as np 
import scipy as sp 
import matplotlib.pyplot as plt  
import matplotlib as mpl

import skimage as sk
import skimage.io as io
from skimage import data as da
from skimage.feature import local_binary_pattern
from skimage.segmentation import slic,mark_boundaries

from hpelm import ELM

# random((m, n), max) => m*n matrix
# random(n, max) => n*n matrix
random = lambda shape,maxx:(np.random.random(
shape if (isinstance(shape,tuple) or isinstance(shape,list)
)else (shape,shape))*maxx).astype(int)

normalizing = lambda a:(a.astype(float)-a.min())/(a.max() - a.min())
floatToUint8 = lambda img:(normalizing(img)*255.999999).astype(np.uint8)



PERFORMANCE = 0
def performance(f):
    '''
    性能测试装饰器
    '''
    def fn(*args, **kw):
        t1 = time.time()
        r = f(*args, **kw)
        t2 = time.time()
        if PERFORMANCE:
            print 'call %s() in %fs' % (f.__name__, (t2 - t1))
        return r
    return fn

def doFiles(COARSE_DIR):
    import os
    files = filter(lambda x: 'MY.png' in x,os.listdir(COARSE_DIR))
    map(lambda x: os.rename(COARSE_DIR+x,COARSE_DIR+x.replace('MY.png',"MY1.png")),files)


def saveData(data, name='Python_pickle'):  #保存进度
    '''
    保存二进制数据
    '''
    f = open(name, "wb")
    pickle.dump(data,f)
    f.close()

def loadData(name='Python_pickle'):  #载入数据
    if not os.path.isfile(name):
        print '在',os.path.abspath('.'),'目录下,“'+name+'”文件不存在，操作失败！'
        return
    f = open(name,"rb")
    data = pickle.load(f)
    f.close()
    return data


def mapp(f, matrix, need_i_j=False):
    '''
    for each it of a matrix
    return a new matrix consist of f:f(it) or f(it, i, j)
    '''
    m, n = matrix.shape[:2]
    listt = [[None]*n for i in range(m)]
    for i in range(m):
        for j in range(n):
            it = matrix[i][j]
            listt[i][j] = f(it,i,j) if need_i_j else f(it)
    return np.array(listt)

def loga(array):
    if isinstance(array,list):
        array = np.array(array)
    if isinstance(array,str) or isinstance(array,unicode):
        print 'info and histogram of',array
        l=[]
        eval('l.append('+array+')')
        array = l[0]
    print 'shape:%s ,max: %s, min: %s'%(str(array.shape),str(array.max()),str(array.min()))
    
    unique = np.unique(array)
    if len(unique)<10:
        dic=dict([(i*1,0) for i in unique])
        for i in array.ravel():
            dic[i] += 1
        listt = dic.items()
        listt.sort(key=lambda x:x[0])
        data,x=[v for k,v in listt],np.array([k for k,v in listt]).astype(float)
        width = (x[0]-x[1])*0.7
        x -=  (x[0]-x[1])*0.35
    else:
        data, x = np.histogram(array.ravel(),8)
        x=x[1:]
        width = (x[0]-x[1])
    plt.plot(x, data, color = 'orange')
    plt.bar(x, data,width = width, alpha = 0.5, color = 'b')
    plt.show()
    return 
    f= lambda a : map(lambda x:(str(x)+' '*8)[:6],a)
    if len(unique)<8:
        dic=dict([(i*1,0) for i in unique])
        for i in array.ravel():
            dic[i] += 1
        for k in dic:
            print k,':',dic[k],', ',
        return
    print 'distribut:'+' |'.join(f(up))
    print ' _'.join(f(down))
def show(l,lab=False):
    '''
    do io.imshow to a list of imgs or one img
    lab,means if img`color is lab
    '''
    if isinstance(l,dict):
        l = l.values()
    if not isinstance(l,list) and (not isinstance(l,tuple) ) :
        l = [l]
    n = len(l)
    if n > 3:
        show(l[:3],lab)
        show(l[3:],lab)
        return 
    fig, axes = plt.subplots(ncols=n)
    count = 0
    axes = [axes] if n==1 else axes 
    for img in l:
        axes[count].imshow(
        sk.color.lab2rgb(img) if len(img.shape)==3 
        and lab else img,
        cmap='gray')
        count += 1
    plt.show()
    
def valueToLabelMap(labelMap,labelValue):
    '''
    assign labelValue to each label,return new img
    '''
    m,n = labelMap.shape[:2]
    labelValue = np.array(labelValue)
    if labelValue.ndim == 1:
        imgg = np.zeros((m,n)).astype(labelValue.dtype)
    else:
        shape = tuple((m,n)+labelValue.shape[1:])
        imgg = np.zeros(shape).astype(labelValue.dtype)
    for label,value in enumerate(labelValue):
        imgg[labelMap==label] = value
    return imgg

def getDatabaseName(imgDir=None):
    if not imgDir:
        return 'UnknowDatabase'
    path = imgDir 
    if path[-1] in ['/','\\']:
        path = path[:-1]
#    path = os.path.dirname(path)
    path = os.path.dirname(path)
    dirName = os.path.split(path)[1]
    return dirName
def getPoltName(methods,imgDir=None):
    name = getDatabaseName(imgDir)
    l = methods[:]
    l.sort()
    name = name+'_'+'_'.join(l)
    return name



def getElm(data,label,
           classification='c', 
           w=None,
           nn=10,
           func="sigm"):
    
    elm = ELM(len(data[0]), len(label[0]),classification,w)
    elm.add_neurons(10, func)
    elm.add_neurons(10,"rbf_l1")
    elm.add_neurons(10,"rbf_l2")
    elm.train(data, np.array(label))
    return elm    


def getSlic(img, n_segments=200 ,compactness=50):
    label = slic(img,n_segments,enforce_connectivity=True)
    #show(mark_boundaries(img, label))
    return label
    

def getEdge(labelMap,width=0.0):
    '''
    width(float):how width of edge
    return a list of label: edge of labelMap
    '''
    width = int(min(*labelMap.shape)*width)
    u,d,l,r = (labelMap[0:width+1].ravel(),labelMap[-1-width:].ravel(),
                labelMap[:,0:width+1].ravel(),labelMap[:,-1-width:].ravel())
    edge=np.unique(np.c_[[u],[d],[l],[r]])
    return edge

   

def getNeighborMatrix(labelMap): 
    '''
    return a (maxLabel*maxLabel) matrix of int mean graph of neighbor 
    -1 in the matrix mean i,j are not neighbor
    '''
    maxLabel = labelMap.max()+1    
    neighbor = np.zeros((maxLabel,maxLabel)).astype(int)-1
    m, n = labelMap.shape    
    ma1 = labelMap[[0]+range(m-1),:]
    ma2 = labelMap[:,[0]+range(n-1)]
    boundMask1,boundMask2 = (ma1!=labelMap),(ma2!=labelMap)
    lines = zip(list(labelMap[boundMask1])+list(labelMap[boundMask2]),
                list(ma1[boundMask1])+list(ma2[boundMask2]))
    for sp1,sp2 in lines:
        assert sp1 != sp2
        neighbor[sp1,sp2] = sp2
        neighbor[sp2,sp1] = sp1
#    labelImg = np.zeros((m,n))
#    for i in range(maxLabel):
#        labelImg[labelMap==i]=neighbor[i].sum()
#    show(labelImg)
    return neighbor
    

    
def getNeighbor(label,labelMap,neighborMatrix,levels=1):
    '''
    return a dict(k:label,v:level):mean top level of label's neighbors
    '''
    labels = [label]
    tag = {label:0}
    rawLabel = label
    for level in range(1,levels+1):
        neighbors = []
        for label in labels:
            neighbors += list(np.unique(neighborMatrix[label])[1:])
        neighbors = filter(lambda x: x not in tag,neighbors)
        labels = neighbors
        for neighbor in neighbors:
            tag[neighbor] = level
    tag.pop(rawLabel)
    return tag
    

def get4channls(img,olnyTwoDim=False):
    return [img.sum(2) if olnyTwoDim else img, img[...,0], img[...,1], img[...,2]]
    
def log(x):
    print x
    return x

def getBinaryImg(img):
    binary = img > sk.filters.threshold_li(img)
    return binary
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    