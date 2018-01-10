# -*- coding: utf-8 -*-
import os
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from PIL import Image
import pytesseract
import requests  #https://www.baidu.com/s?wd=
import urllib
import re

"""这个程序作用是获取西瓜视频的百万英雄类的答题，
    先通过adb获得截图，通过ocr技术获得文字，再通过爬虫获得答案，再通过adb模拟点击"""


def pull_screenshot():
    """主要通过adb 命令来从手机获取截图到本电脑中"""
    os.system('adb shell screencap -p /sdcard/autoshot.png')
    os.system('adb pull /sdcard/autoshot.png .')



def cut_fig(*args):
    """通过PIL库把截图分割成问题和答案"""
    im = Image.open("autoshot.png")#记得修改
    # 图片的宽度和高度
    img_size = im.size
    #print("图片宽度和高度分别是{}".format(img_size))
    '''
	裁剪：传入一个元组作为参数
	元组里的元素分别是：（距离图片左边界距离x， 距离图片上边界距离y，距离图片左边界距离+裁剪框宽度x+w，距离图片上边界距离+裁剪框高度y+h）
	'''
    #切割出问题
    x = 50
    y = 250
    w = 950
    h = 350
    question = im.crop((x, y, x+w, y+h))
    question.save("./cut_autoshot.png")

    #切割出选项
    aws_1 = im.crop((140, 660, 900, 800))
    aws_1.save("./cut_autoshot_aws1.png")

    #切割出选项
    aws_2 = im.crop((140, 850, 900, 1000))
    aws_2.save("./cut_autoshot_aws2.png")

    #切割出选项
    aws_3 = im.crop((140, 1040, 900, 1200))
    aws_3.save("./cut_autoshot_aws3.png")







def ocr_fig(fig_name):
    """通过pytesseract来操控Tesseract把分割好的截图中的文字识别出来"""
    index=Image.open(fig_name + '.png')
    text = pytesseract.image_to_string(index, lang='chi_sim')#调用pytesseract识别图片
    t1=text.replace(' ', '')#消除识别的结果中的空格
    text = t1.replace('\n', '')
    return text


def spider_ans(text_raw):
    """通过urllib库，把识别出来的问题作为关键字来爬取百度知道"""
    text=urllib.parse.quote(text_raw)
    headers = {'content-type': 'application/json','User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}
    #print(r.status_code)    # 获取返回状态
    url='http://zhidao.baidu.com/search?word='+text
    r = urllib.request.Request(url='http://zhidao.baidu.com/search?word='+text,headers=headers)   #带参数的GET请求
    response = urllib.request.urlopen(r)
    the_page = response.read().decode("gbk")
    #print("正在爬取答案......"+url)#打印解码后的返回数据
    return the_page

def press_aws(num):
    """通过adb命令来对相应位置进行模拟点击"""
    press_time = 50
    cmd1 = 'adb shell input swipe 320 730 325 735 ' + str(press_time)#答案1的按键
    cmd2 = 'adb shell input swipe 320 920 325 925 ' + str(press_time)#答案1的按键
    cmd3 = 'adb shell input swipe 320 1120 325 1125 ' + str(press_time)#答案1的按键
    #//在屏幕上做划屏操作，前四个数为坐标点，后面是滑动的时间（单位毫秒）
	#adb shell input swipe 50 250 250 250 500 
	#//在屏幕上点击坐标点x=50  y=250的位置。
	#adb shell input tap 50 250
	#//输入字符abc
	#adb shell input text abc
    if num==1:
        print(cmd1)
        os.system(cmd1)
    else:
        if num==2:
            print(cmd2)
            os.system(cmd2)
        else:
            print(cmd3)
            os.system(cmd3)


def compare_string(key, aws_str1, aws_str2, aws_str3, aws_str4="预留选项"):
    """通过比对爬虫获取的答案和选项进行比对，获取正确选项"""
    r=[]
    r1 = re.findall(aws_str1,key)
    r.append(r1)
    r2 = re.findall(aws_str2,key)
    r.append(r2)
    r3 = re.findall(aws_str3,key)
    r.append(r3)
    i=0
    ind=0
#    for i in range(3):
#        if r[i] !=[]:
#            ind = i
#    print("预测答案是第%s个答案"%(ind+1))
#    return ind+1

    counts = []
    choices= []
    choices.append(aws_str1)
    choices.append(aws_str2)
    choices.append(aws_str3)
    #print('Question: '+question)
    for i in range(len(choices)):
        counts.append(key.count(choices[i]))
        #print(choices[i] + " : " + str(counts[i]))
    print('Recommend Choose : ' + choices[counts.index(max(counts))])

def is_press(num):
    #y_n = input("请问是否由脚本自动执行0:y,123:ABC：:::")
    y_n='0'
    if y_n=="0":
        time.sleep(4)
        press_aws(num)
    else:
        print("你输入了第%s个答案"%y_n)
        press_aws(int(y_n))


def updatefig(*args):
    y_n = input("请问题目是否更新1:y,2:N:::::")
    if y_n=="1":
        start_time = time.clock()
        pull_screenshot()
        cut_fig()#切割截图
        question_text=ocr_fig(cut_autoshot)#ocr获取问题文本
        aws_1 = ocr_fig(cut_autoshot_aws1)
        aws_2 = ocr_fig(cut_autoshot_aws2)
        aws_3 = ocr_fig(cut_autoshot_aws3)
        print("问题是："+question_text)
        print("答案1："+aws_1)
        print("答案2："+aws_2)
        print("答案3："+aws_3)

        reponse = spider_ans(question_text)

        key_press = compare_string(reponse, aws_1,aws_2,aws_3)
        is_press(key_press)
        end_time = time.clock()
        print("time:"+str(end_time-start_time))
        #time.sleep(5)
    else:
        print("请稍等...")


    
cut_autoshot='cut_autoshot'
cut_autoshot_aws1='cut_autoshot_aws1'
cut_autoshot_aws2='cut_autoshot_aws2'
cut_autoshot_aws3='cut_autoshot_aws3'




if __name__ == '__main__':
    while(True):
        updatefig()#更新截图
        
    
	






