from __future__ import division 
import sys 
import random
import math 
import numpy as np
from where_mod import *
sys.dont_write_bytecode = True
rand=random.random
# consist of dictionary where the index is 
# 100*xblock+yblock and 
dictionary ={} 
threshold =3         #threshold for number of points to be considered as a prospective solution
ncol=8               #number of columns in the chess board
nrow=8               #number of rows in the chess board
intermaxlimit=20     #Max number of points that can be created by interpolation
extermaxlimit=20     #Max number of points that can be created by extrapolation


#There is something wrong with the lambda expressions need to make sure it wraps around.
convert = lambda x,y: (x*100)+y
rowno = lambda x: int(x/100)
colmno = lambda x: x%10

def gonw(x):
  if(rowno(x)==1 and colmno(x)==1):return convert(nrow,ncol)#in the first coulumn and first row
  elif(rowno(x)==1): return convert(nrow,colmno(x)-1)
  elif(colmno(x)==1): return convert(rowno(x)-1,ncol)#in the first column
  else: return (x-101)

def gow(x):
 if(colmno(x)==1): return convert(rowno(x),ncol)
 else: return (x-1)

def gosw(x):
  if(rowno(x)==nrow and colmno(x)==1): return convert(1,ncol)
  elif(rowno(x)==nrow): return convert(1,colmno(x)-1)
  elif(colmno(x)==1): return convert(rowno(x)+1,ncol)
  else: return (x+99)

def gos(x):
  if(rowno(x)==nrow): return convert(1,colmno(x))
  else: return x+100

def gose(x):
  if(rowno(x)==nrow and colmno(x)==ncol): return convert(1,1)
  elif(rowno(x)==nrow): return convert(1,colmno(x)+1)
  elif(colmno(x)==ncol): return convert(rowno(x)+1,1)
  else: return x+101

def goe(x):
  if(colmno(x)==ncol): return convert(rowno(x),1)
  else: return x+1

def gone(x):
  if(rowno(x)==1 and colmno(x)==ncol): return convert(nrow,1)
  elif(rowno(x)==1): return convert(nrow,colmno(x)+1)
  elif(colmno(x)==ncol): return convert(rowno(x)-1,1)
  else: return x-99

def gon(x):
  if(rowno(x)==1): return convert(nrow,colmno(x))
  else: return x-100 

import collections
compare = lambda x, y: collections.Counter(x) == collections.Counter(y)

def neighbourhood(xblock,yblock):
  temp=[[-1,0,1],[-1,0,1]]
  comb=[]
  import itertools
  for e in itertools.product(*temp):
   comb.append(e)
  neigbour ={}
  def neighr(xblock,yblock):
    index=xblock*100+yblock
    try:
      #only return the neighbours who has threshold number of
      #elements in it.
      if len(dictionary[index]) > threshold:
        neigbour[index]=len(dictionary[index])
      #else:print len(dictionary[index])
    except: pass  
  for i in comb:
    neighr((xblock-i[0])%8,(yblock-i[1])%8)
  return neigbour

def stats(listl):
  from scipy.stats import scoreatpercentile
  q1 = scoreatpercentile(listl,25)
  q3 = scoreatpercentile(listl,75)  
  #print "IQR : %f"%(q3-q1)
  #print "Median: %f"%median(listl)
  return median(listl),(q3-q1)

def energy(xblock,yblock):
  tempIndex=int(100*xblock+yblock)
  #print "energy| xblock: %d yblock: %d"%(xblock,yblock)
  #print "energy| TempIndex: " ,tempIndex
  energy=[]
  try:
    for x in dictionary[tempIndex]:
      energy.append(np.sum(x.obj))      
    median,iqr=stats(energy)
    #print "%d, %f, %f"%(len(dictionary[tempIndex]),median,iqr),
    return median,iqr
  except:
    print "Energy Error"


def getpoints(index):
  tempL = []
  for x in dictionary[index]:tempL.append(x.dec)
  return tempL
    
  

def wrapperInterpolate(m,xindex,yindex):
  def interpolate(lx,ly,cr=1,fmin=0,fmax=1):
    def lo(m)      : return 0.0
    def hi(m)      : return  1.0
    def trim(x)  : # trim to legal range
      return max(lo(x), x%hi(x))
    assert(len(lx)==len(ly))
    genPoint=[]
    for i in xrange(len(lx)):
      x,y=lx[i],ly[i]
      #print x
      #print y
      rand = random.random()
      if rand < cr:
        probEx = fmin +(fmax-fmin)*random.random()
        new = trim(min(x,y)+probEx*abs(x-y))
      else:
        new = y
      genPoint.append(new)
    return genPoint

  decision=[]
  #print "Number of points in ",xindex," is: ",len(dictionary[xindex])
  #print "Number of points in ",yindex," is: ",len(dictionary[yindex])
  xpoints=getpoints(xindex)
  ypoints=getpoints(yindex)
  import itertools 
  listpoints=list(itertools.product(xpoints,ypoints))
  #print "Length of Listpoints: ",len(listpoints)
  count=0
  for x in listpoints:
    if(count>min(len(xpoints),intermaxlimit)):break
    decision.append(interpolate(x[0],x[1]))
    count+=1
  return decision


def generateSlot(m,decision,x,y):
  newpoint = Slots(changed = True,
            scores=None, 
            xblock=x, #sam
            yblock=y,  #sam
            x=-1,
            y=-1,
            obj = [None] * len(objectives(m)), #[None]*4
            dec = decision)
  scores(m,newpoint)
  #print "Decision: ",newpoint.dec
  #print "Objectives: ",newpoint.obj
  return newpoint


#There are three points and I am trying to extrapolate. Need to pass two cell numbers
def wrapperextrapolate(m,xindex,yindex):
  def extrapolate(lx,ly,lz,cr=1,fmin=0.9,fmax=2):
    def lo(m)      : return 0.0
    def hi(m)      : return  1.0
    def trim(x)  : # trim to legal range
      return max(lo(x), x%hi(x))
    def indexConvert(index):
      return int(index/100),index%10
    assert(len(lx)==len(ly)==len(lz))
    genPoint=[]
    for i in xrange(len(lx)):
      x,y,z = lx[i],ly[i],lz[i]
      rand = random.random()

      if rand < cr: 
        probEx = fmin + (fmax-fmin)*random.random()
        new = trim(x + probEx*(y-z))
      else:
        new = y #Just assign a value for that decision
      genPoint.append(new)
    return genPoint

  decision=[]
  #TODO: need to put an assert saying checking whether extrapolation is actually possible
  xpoints=getpoints(xindex)
  ypoints=getpoints(yindex)
  count=0
  for ij in xpoints:
    if(count>min(len(xpoints),extermaxlimit)):break
    two = ij
    index2,index3=0,0
    while(index2 == index3): #just making sure that the indexes are not the same
      index2=random.randint(0,len(ypoints)-1)
      index3=random.randint(0,len(ypoints)-1)

    three=ypoints[index2]
    four=ypoints[index3]
    temp = extrapolate(two,three,four)
    #decision.append(extrapolate(two,three,four))
    decision.append(temp)
    count+=1
  return decision



"""
def decisions:
if there are enough points then look at the neighbour. Look for the cell which has 
  i.   highest number of points
  ii.  lowest mean energy. energy is a the sum of all the objectives
  iii. lowest variance
else
  if the opposite cells have threshold number of cells interpolate
  else if there are consequtive points which have threshold points then extrapolate
"""

def generateNew(m,xblock,yblock):


  def indexConvert(index):
    return int(index/100),index%10

  def opposite(a,b):
    ax,ay,bx,by=a/100,a%100,b/100,b%100
    if(abs(ax-bx)==2 or abs(ay-by)==2):return True
    else: return False

  def thresholdCheck(index):
    try:
      #print "Threshold Check: ",index
      if(len(dictionary[index])>threshold):return True
      else:return False
    except:
      #print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>except: ",index
      return False

  def interpolateCheck(xblock,yblock):
    if(thresholdCheck(gonw(convert(xblock,yblock))) and thresholdCheck(gose(convert(xblock,yblock))) == True):
      return gonw(convert(xblock,yblock)),gose(convert(xblock,yblock))
    elif(thresholdCheck(gow(convert(xblock,yblock))) and thresholdCheck(goe(convert(xblock,yblock))) == True):
      return gow(convert(xblock,yblock)),goe(convert(xblock,yblock))
    elif(thresholdCheck(gosw(convert(xblock,yblock))) and thresholdCheck(gone(convert(xblock,yblock))) == True):
      return gosw(convert(xblock,yblock)),gone(convert(xblock,yblock))
    elif(thresholdCheck(gon(convert(xblock,yblock))) and thresholdCheck(gos(convert(xblock,yblock))) == True):
      return gon(convert(xblock,yblock)),gos(convert(xblock,yblock))
    return None,None


  def extrapolateCheck(xblock,yblock):
    #TODO: If there are more than one consequetive blocks with threshold number of points how do we handle it?
    #TODO: Need to make this logic more succint

    #go North West
    temp = gonw(convert(xblock,yblock))
    result1 = thresholdCheck(temp)
    if result1 == True:
      result2 = thresholdCheck(gonw(temp))
      if(result1 and result2 == True):
        return temp,gonw(temp)

    #go North 
    temp = gon(convert(xblock,yblock))
    result1 = thresholdCheck(temp)
    if result1 == True:
      result2 = thresholdCheck(gon(temp))
      if(result1 and result2 == True):
        return temp,gon(temp)

    #go North East
    temp = gone(convert(xblock,yblock))
    result1 = thresholdCheck(temp)
    if result1 == True:
      result2 = thresholdCheck(gone(temp))
      if(result1 and result2 == True):
        return temp,gone(temp)

    #go East
    temp = goe(convert(xblock,yblock))
    result1 = thresholdCheck(temp)
    if result1 == True:
      result2 = thresholdCheck(goe(temp))
      if(result1 and result2 == True):
        return temp,goe(temp)

    #go South East
    temp = gose(convert(xblock,yblock))
    result1 = thresholdCheck(temp)
    if result1 == True:
      result2 = thresholdCheck(gose(temp))
      if(result1 and result2 == True):
        return temp,gose(temp)

    #go South
    temp = gos(convert(xblock,yblock))
    result1 = thresholdCheck(temp)
    if result1 == True:
      result2 = thresholdCheck(gos(temp))
      if(result1 and result2 == True):
        return temp,gos(temp)

    #go South West
    temp = gosw(convert(xblock,yblock))
    result1 = thresholdCheck(temp)
    if result1 == True:
      result2 = thresholdCheck(gosw(temp))
      if(result1 and result2 == True):
        return temp,gosw(temp)

    #go West
    temp = gow(convert(xblock,yblock))
    result1 = thresholdCheck(temp)
    if result1 == True:
      result2 = thresholdCheck(gow(temp))
      if(result1 and result2 == True):
        return temp,gow(temp)
    return None,None
  
  newpoints=[]
  #print "generateNew| xblock: %d yblock: %d"%(xblock,yblock)
  #print "generateNew| convert: ",convert(xblock,yblock)
  #print "generateNew|thresholdCheck(convert(xblock,yblock): ",thresholdCheck(convert(xblock,yblock))
  if(thresholdCheck(convert(xblock,yblock))==False):
    #print "generateNew| Cell is relatively sparse: Might need to generate new points"
    xb,yb=interpolateCheck(xblock,yblock)
    if(xb!=None and yb!=None):
      #print thresholdCheck(xb),thresholdCheck(yb)
      decisions = wrapperInterpolate(m,xb,yb)
      if convert(xblock,yblock) in dictionary: pass
      else:
        #print convert(xblock,yblock)
        assert(convert(xblock,yblock)>=101),"Something's wrong!" 
        assert(convert(xblock,yblock)<=808),"Something's wrong!" 
        dictionary[convert(xblock,yblock)]=[]
      old = _checkDictionary()
      for decision in decisions:dictionary[convert(xblock,yblock)].append(generateSlot(m,decision,xblock,yblock))
      #print "generateNew| Interpolation works!"
      new = _checkDictionary()
      #print "generateNew|Interpolation| Number of new points generated: ", (new-old)
      return True
    else:
      #print "generateNew| Interpolation failed!"
      findex,sindex = extrapolateCheck(xblock,yblock)
      if(findex==None and sindex==None):
        print "generateNew|Interpolation and Extrapolation failed|In a tight spot..somewhere in the desert RANDOM JUMP REQUIRED"
        return False
      else:
        decisions = wrapperextrapolate(m,findex,sindex)
        if convert(xblock,yblock) in dictionary: pass
        else: 
          assert(convert(xblock,yblock)>=101),"Something's wrong!" 
          assert(convert(xblock,yblock)<=808),"Something's wrong!" 
          dictionary[convert(xblock,yblock)]=[]
        old = _checkDictionary()
        for decision in decisions: dictionary[convert(xblock,yblock)].append(generateSlot(m,decision,xblock,yblock))
        new = _checkDictionary()
        #print "generateNew|Extrapolation Worked ",len(dictionary[convert(xblock,yblock)])
        #print "generateNew|Extrapolation| Number of new points generated: ", (new-old)
        return True
  else:
    findex,sindex = extrapolateCheck(xblock,yblock)
    if(findex==None and sindex==None):
      print "generateNew| Lot of points but middle of a desert"
      return False #A lot of points but right in the middle of a deseart
    else:
      return True
  """
  print interpolateCheck(xblock,yblock)
  """

"""
Return a list of neighbours:
"""
def listofneighbours(m,xblock,yblock):
  index=convert(xblock,yblock)
  #print "listofneighbours| Index passed: ",index
  listL=[]
  listL.append(goe(index))
  listL.append(gose(index))
  listL.append(gos(index))
  listL.append(gosw(index))
  listL.append(gow(index))
  listL.append(gonw(index))
  listL.append(gon(index))
  listL.append(gone(index))
  return listL

def printNormal():

  def thresholdCheck(index):
    try:
      if(len(dictionary[index])>threshold):return len(dictionary[index])
      else:return False
    except:
      return False

  for i in xrange(1,9):
    for j in xrange(1,9):
      #print '[%s]' % ', '.join(map(str, mylist))
      print "%d|%d  |"%((convert(i,j)),thresholdCheck(convert(i,j))),
      temp = energy(i,j)
      print "%2.3f,%2.3f"%(temp[0],temp[1]),
      print "    ",
    print
"""
Generate random cell number pass it to generateNew() and if the point is in between a deseart then jump to a random cell
look at the neighbourhood and see which is the most promising cell to move to

"""
def searcher(m):
  def randomC(): 
    return int(1+random.random()*7)
  def randomcell(): 
    return [randomC() for _ in xrange(2)]

  tries=0
  bmean,biqr=1e6,1e6
  bsoln=[-1,-1]
  while(tries<40):
    print "---------------------------Tries: %d---------------------------------------"%tries
    soln = randomcell()
    tries+=1
    repeat=0
    while(repeat<32):
      print "Solution being tried: %d %d "%(soln[0],soln[1])
      result = generateNew(m,soln[0],soln[1])
      if(result == False): 
        print
        break
      else:
        #print "Searcher| Solution being tried: %d %d "%(soln[0],soln[1])
        mean,iqr = energy(soln[0],soln[1])
        btsoln=[]
        neighbours = listofneighbours(m,soln[0],soln[1])
        print neighbours
        btmean,btiqr=1e6,1e6
        for neighbour in neighbours:
          #print "Searcher| neighbour: ",neighbour
          result = generateNew(m,int(neighbour/100),neighbour%10)
          if(result == True):
            tmean,tiqr = energy(int(neighbour/100),neighbour%10)
            if((tmean<btmean and tmean<mean) or (tmean==mean and tiqr < iqr and tmean<=btmean and tiqr<=btiqr)):
              #print "Searcher| tmean: %f mean: %f"%(tmean,mean)
              #print "Searcher| tiqr: %f iqr: %f"%(tiqr,iqr)
              btsoln = [int(neighbour/100),neighbour%10]
              #print "Searcher|btsoln: ",btsoln
              btmean=tmean
              btiqr=tiqr

            #print "Searcher|Temp Mean:%f IQR: %f"%(mean,iqr)
            if(tmean<bmean or (tmean == bmean and tiqr<biqr)):
              print "Searcher| Better than best found!!"
              #print "Searcher| Good Mean:%f IQR: %f"%(mean,iqr)
              bmean = tmean
              biqr = tiqr
              bsoln = [int(neighbour/100),neighbour%10]
              #print "Searcher| SOLUTION: ",bsoln
          else:
            #print "Searcher|NAAAAAAAAAAAAH"
            pass

        #print "++++++++++++++++++++++soln: ",soln
        #print "++++++++++++++++++++++bsoln: ",bsoln
        if(compare(btsoln,soln)!=True and len(btsoln)!=0):
          #print "##################Found old solution!!: ",bsoln
          #print "##################Found new solution!!: ",soln
          soln=btsoln
          print "Searcher| Mean: %f IQR: %f "%(tmean,tiqr)
        else:
          repeat+=1
          break


  print ">>>>>>>>>>>>>>WOW Mean:%f IQR: %f"%(bmean,biqr)
  print ">>>>>>>>>>>>>>WOW Soultion: ",bsoln


def _checkdirection(x):
  print "North: ",gon(x)
  print "North West: ",gonw(x)
  print "North East: ",gone(x)
  print "East: ",goe(x)
  print "South East: ",gose(x)
  print "South: ",gos(x)
  print "South West: ",gosw(x)
  print "West: ",gow(x)
  print "-------------------------------"

def _wrappercheckdirection():
  _checkdirection(101)
  _checkdirection(801)
  _checkdirection(808)
  _checkdirection(108)


def _checkDictionary():
  sum=0
  for i in dictionary.keys():
    sum+=len(dictionary[i])
  return sum

def main():
  m='model'
  random.seed(3)
  chessBoard = whereMain()
  x= int(8*random.random())
  y= int(8*random.random()) 
  #print x,y
  for i in range(1,9):
      for j in range(1,9):
          temp=[]
          for x in chessBoard:
              if x.xblock==i and x.yblock==j:
                  temp.append(x)
          if(len(temp)!=0):
            #print "tempList",
            #print temp[0].xblock,temp[0].yblock,len(temp)
            index=temp[0].xblock*100+temp[0].yblock
            dictionary[index] = temp
            assert(len(temp)==len(dictionary[index])),"something"
            #print dictionary[index][0].xblock
  #print (dictionary.keys())
  #print "Elements: %d"%len(dictionary[506])
  #print neighbourhood(5,6)
  #generateNew(m,3,6)
  #_checkDictionary()
  #wrapperextrapolate(m,405,607)
  searcher(m)
  printNormal()
  print "Total number of points in the grid: ",_checkDictionary()


if __name__ == '__main__':
  #_wrappercheckdirection()
 # _interpolate()
  main()
  #_extrapolate()
  #_neighbourhood()
