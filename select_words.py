#coding:utf-8
import re
import urllib
import jieba
import jieba.posseg as pseg
import re
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
import io
from svmutil import *
from svm import *


def getHtml(url):
    page = urllib.urlopen(url)
    html = page.read()
    return html

def getpage():
  head = 'https://www.shiyanlou.com/courses/'
  courselist = [['1', 14, '?category=%E5%90%8E%E7%AB%AF%E5%BC%80%E5%8F%91&course_type=all&fee=all&tag=all&page=', '后端开发']
      ,['2',3,'?category=Linux%E8%BF%90%E7%BB%B4&course_type=all&fee=all&tag=all&page=', 'Linux运维']
      ,['3',5,'?category=%E4%BA%91%E8%AE%A1%E7%AE%97%E4%B8%8E%E5%A4%A7%E6%95%B0%E6%8D%AE&course_type=all&fee=all&tag=all&page=', '云计算与大数据']
      ,['4',0,'?category=%E6%95%B0%E6%8D%AE%E5%BA%93&unfold=0', '数据库']
      ,['5',2,'?category=%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8&course_type=all&fee=all&tag=all&page=', '信息安全']
      ,['6',2,'?category=Web%E5%89%8D%E7%AB%AF&course_type=all&fee=all&tag=all&page=', 'Web前端']
      ,['7',2,'?category=%E8%AE%A1%E7%AE%97%E6%9C%BA%E4%B8%93%E4%B8%9A%E8%AF%BE&course_type=all&fee=all&tag=all&page=', '计算机专业课']
      ,['8',2,'?category=%E5%85%B6%E4%BB%96%E6%8A%80%E6%9C%AF&course_type=all&fee=all&tag=all&page=', '其他技术']]
  result=[]
  for obj in courselist:
      temp1 = []
      temp2 = []
      if obj[1] > 0:
          a = list(range(obj[1]))
          for i in a:
              temp2.append(head + obj[2] + str(i + 1))
      if obj[1] == 0:
          temp2.append(head + obj[2])
      temp1.append(obj[0])
      temp1.append(temp2)
      result.append(temp1)
  return result


def getCourse(url,coursename):
    html = getHtml(url)
    r = re.compile('<h6 class="course-name" data-v-7b4a6760>(.*?)</h6>', re.S)
    CourseNameList = re.findall(r, html)
    for i in CourseNameList:
        coursename.append(i)

def stopwordslist():
    stopwords = [line.strip() for line in io.open('stopwords.txt',encoding='UTF-8').readlines()]
    return stopwords

result = getpage()
#print(result)

course_sort = []
title_num = 1
getclass = {}
for i in result:
    coursename = []
    for j in i[1]:
        getCourse(j,coursename)
    for obj in coursename:
        course_sort.append([i[0], int(title_num), obj])
        getclass[str(title_num)] = i[0]
        title_num += 1

print(course_sort)

stopwords = stopwordslist()

jieba.load_userdict("newdict.txt")

sort_data_attr = []
for i in course_sort:
    cleanstr = i[2].replace(' ', '').replace('&amp;', '')
    seg_list = pseg.cut(cleanstr)
    for t in seg_list:
        pair = str(t).split('/')
        if len(pair) < 2:
            continue
        if pair[0].decode("GBK") not in stopwords:
            sort_data_attr.append([i[0], i[1], pair[0], pair[1]])
#print(len(sort_data_attr))
#print(sort_data_attr)


stop_attr = ['v', 'p', 'c', 'uj', 'r', 'a', 'vn', 'nr', 'q', 'm', 'f', 'u', 'x', 'i',
                 'k', 'nrt']
attr_dict = [[y[0], y[1], y[2]] for y in sort_data_attr if y[3] not in stop_attr]
print(len(attr_dict))
#print(attr_dict)


corpus = []
n = 1
while n <= title_num - 1:
    temp = " "
    for i in attr_dict:
        if i[1] == n:
            temp += (str(i[2]) + " ")
    corpus.append(temp.decode("GBK").encode("utf-8"))
    n += 1

#print(len(corpus))
#print(corpus)

vectorizer = CountVectorizer()#该类会将文本中的词语转换为词频矩阵，矩阵元素a[i][j] 表示j词在i类文本下的词频
transformer = TfidfTransformer()#该类会统计每个词语的tf-idf权值
tfidf=transformer.fit_transform(vectorizer.fit_transform(corpus))#第一个fit_transform是计算tf-idf，第二个fit_transform是将文本转为词频矩阵
word=vectorizer.get_feature_names()#获取词袋模型中的所有词语
weight=tfidf.toarray()#将tf-idf矩阵抽取出来，元素a[i][j]表示j词在i类文本中的tf-idf权重

#print(weight)

#print(range(len(weight)))
print(len(weight))
print(len(weight[1]))

x = []
y = []
for i in range(len(weight)):#打印每类文本的tf-idf词语权重，第一个for遍历所有文本，第二个for便利某一类文本下的词语权重
    #print u"-------这里输出第",i,u"类文本的词语tf-idf权重------"
    x.append(weight[i])
    y.append(float(getclass[str(i+1)]))
    #for j in range(len(word)):
           #print word[j],weight[i][j]

m = 1
train_input = []
train_output = []
test_input = []
test_output = []
while m <= 563:
    if m % 6 == 0:
        test_input.append(x[m-1])
        test_output.append(y[m-1])
    if m % 6 != 0:
        train_input.append(x[m-1])
        train_output.append(y[m-1])
    m += 1

#print(train_value)
#print(test_value)
model = svm_train(train_output,train_input,'-s 0 -c 3 -t 3 -g 20 -e 0.001')   ##模型训练
p_labs, p_acc, p_vals =svm_predict(test_output, test_input, model)
print(p_acc)