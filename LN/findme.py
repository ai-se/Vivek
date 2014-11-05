from __future__ import division
import sys,math
sys.dont_write_bytecode=True
from collections import defaultdict

def say(x):
  sys.stdout.write(str(x)); sys.stdout.flush()

def processing(lines):
  returnLines =[]
  def beforestemming(line):
    temp=[]
    from nltk import word_tokenize
    from nltk.corpus import stopwords
    import string
    stop = stopwords.words('english')+list(string.punctuation)
    for i in word_tokenize(line.lower()):
      for p in string.punctuation: i=i.replace(p,"")
      if i.isalpha() == False: continue
      if i not in stop and len(i)>2:
        temp.append(i)
    return ' '.join(temp)

  def stemming(line):
    from nltk.stem import PorterStemmer
    lmtzr = PorterStemmer()
    words=[]
    for word in line.split(' '):
      words.append(lmtzr.stem(word))
    line = ' '.join(words)
    return line
  
  file = open('newfile','w')
  count=0
  for count,line in enumerate(lines):
   #say(count)
   #say(" ")
   #say(len(line))
   line = beforestemming(line)
   #say(" ")
   #say(len(line))
   #say(" afterbeforestemming ")
   line = stemming(line)
   #say(" afterstemming ")
   returnLines.append(line)
   file.write("%d: %s \n"%(count,line))
  file.close()
  return returnLines    

def filldict(dictL,lines):
  for i,line in enumerate(lines):
    for word in line.split(' '):
      dictL[word].append(i)
  return dictL
      
def findme(src="data/R-intro.txt"):
  def top(rawdict):
    import heapq
    return heapq.nlargest(100,rawdict,key=rawdict.get)

  raw = open(src).read()
  lines = raw.split('.\n\n')
  print "Number of lines: " + str(len(lines))
  lines = processing(lines)
  d = defaultdict(list)
  d =filldict(d,lines)
  scoredict = tfidf(d,raw)
  print len(scoredict.keys())
  print scoredict['work']
  temp = top(scoredict)
  for t in temp:
    print "Word: ",t,", Score: ",scoredict[t],", List: ",len(set(d[t])),", Reps: ",len(d[t])

def tfidf(d,raw):
  scoredict={}
  def occur(list,number):
    return list.count(number)
  def nowords(raw,paraNo):
    return len(raw.split('.\n\n')[paraNo])
  def evaluate(word,words,para,paras):
    return (word/words)*(math.log(paras/para))
  paras = len(raw.split('.\n\n'))
  uwords = d.keys()
  print "TFIFD: Number of Unique words: ",len(uwords)
  count=0
  for uword in uwords:
    para = len(set(d[uword]))
    sumv=0 
    count+=1
    if(count%10 == 0): say('.'),
    for i in d[uword]:
      words = nowords(raw,i)
      word = occur(d[uword],i)
      sumv+= evaluate(word,words,para,paras)
    scoredict[uword]=sumv/para
  return scoredict

def _findme():
  findme()
  
if __name__ == '__main__': _findme()
