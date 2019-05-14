#coding:utf-8
import re
import urllib
import jieba
import jieba.posseg as pseg
import re

def getHtml(url):
    page = urllib.urlopen(url)
    html = page.read()
    return html

def getpage():
  a = list(range(2))
  print a
  result=[]
  for i in a:
      result.append("https://www.shiyanlou.com/courses/?category=计算机专业课&course_type=all&fee=all&tag=all&page=" + str(i+1) )
  return result

def getCourse(url,coursename):
    html = getHtml(url)
    r = re.compile('<div class="course-name">(.*?)</div>', re.S)
    CourseNameList = re.findall(r, html)
    for i in CourseNameList:
        coursename.append(i)
    return coursename

def outputSwf(list):
    fo = open("loopname.txt", "w")  #open file
    for i in list:
        fo.write(i + "\n")
    # close file
    fo.close()

coursename = []
result = getpage()
for i in result:
    getCourse(i,coursename)
outputSwf(list(set(coursename)))

fileneedCut='loopname.txt'
fn=open(fileneedCut,"r")
for line in fn.readlines():
    #print(line)
    cleanstr = line.replace(' ','').replace('&amp;','')
    seg_list = jieba.cut(cleanstr, cut_all=False, HMM=True)
    print("Default Mode: " + "/ ".join(seg_list))

fn.close()