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
  energy=[]
  try:
    for x in dictionary[tempIndex]:
      energy.append(np.sum(x.obj))      
    median,iqr=stats(energy)
    #print "%d, %f, %f"%(len(dictionary[tempIndex]),median,iqr),
    return median,iqr
  except:
    print "Error"


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
  xpoints=getpoints(xindex)
  ypoints=getpoints(yindex)
  import itertools 
  listpoints=list(itertools.product(xpoints,ypoints))
  for x in listpoints:
    decision.append(interpolate(x[0],x[1]))
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
    print genPoint
    return genPoint

  decision=[]
  #TODO: need to put an assert saying checking whether extrapolation is actually possible
  xpoints=getpoints(xindex)
  ypoints=getpoints(yindex)
  for ij in xpoints:
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

def decisionMaker(m,xblock,yblock):
  gonw = lambda x: x - 101
  gow = lambda x: x-1
  gosw = lambda x: x + 99
  gos = lambda x: x + 100
  gose = lambda x: x +101
  goe = lambda x: x+1
  gone = lambda x: x - 99
  gon = lambda x: x-100
  convert = lambda x,y: x*100+y

  def indexConvert(index):
    return int(index/100),index%10

  def opposite(a,b):
    ax,ay,bx,by=a/100,a%100,b/100,b%100
    if(abs(ax-bx)==2 or abs(ay-by)==2):return True
    else: return False

  def thresholdCheck(index):
    if(len(dictionary[index])<threshold):return True
    else:return False

  def extrapolateCheck(xblock,yblock):
    #TODO: If there are more than one consequetive blocks with threshold number of points how do we handle it?
    #TODO: Need to make this logic more succint

    #go North West
    temp = gonw(convert(xblock,yblock))
    result1 = thresholdCheck(temp)
    if result == True:
      result2 = thresholdCheck(gonw(temp))
      if(result1 and result2 == True):
        return temp,gonw(temp)

    #go North 
    temp = gon(convert(xblock,yblock))
    result1 = thresholdCheck(temp)
    if result == True:
      result2 = thresholdCheck(gon(temp))
      if(result1 and result2 == True):
        return temp,gon(temp)

    #go North East
    temp = gone(convert(xblock,yblock))
    result1 = thresholdCheck(temp)
    if result == True:
      result2 = thresholdCheck(gone(temp))
      if(result1 and result2 == True):
        return temp,gone(temp)

    #go East
    temp = goe(convert(xblock,yblock))
    result1 = thresholdCheck(temp)
    if result == True:
      result2 = thresholdCheck(goe(temp))
      if(result1 and result2 == True):
        return temp,goe(temp)

    #go South East
    temp = gose(convert(xblock,yblock))
    result1 = thresholdCheck(temp)
    if result == True:
      result2 = thresholdCheck(gose(temp))
      if(result1 and result2 == True):
        return temp,gose(temp)

    #go South
    temp = gos(convert(xblock,yblock))
    result1 = thresholdCheck(temp)
    if result == True:
      result2 = thresholdCheck(gos(temp))
      if(result1 and result2 == True):
        return temp,gos(temp)

    #go South West
    temp = gosw(convert(xblock,yblock))
    result1 = thresholdCheck(temp)
    if result == True:
      result2 = thresholdCheck(gosw(temp))
      if(result1 and result2 == True):
        return temp,gosw(temp)

    #go West
    temp = gow(convert(xblock,yblock))
    result1 = thresholdCheck(temp)
    if result == True:
      result2 = thresholdCheck(gow(temp))
      if(result1 and result2 == True):
        return temp,gow(temp)
    return None,None

  newpoints=[]
  threshold=3
  if(thresholdCheck(convert(xblock,yblock))==False):
    print "Cell is relwatively sparse: Might need to generate new points"

  neigh = neighbourhood(xblock,yblock)
  neigh = dict((k, v) for k, v in neigh.iteritems() if v>threshold)
  for key, value in neigh.iteritems():
    print key,value,energy(int(key/100),key%10) 
  vallist=neigh.keys()
  import itertools 
  for pair in itertools.combinations(vallist,2):
    if(opposite(*pair)==True):
      print energy(xblock,yblock)
      print "We could create more points in this cell %d %d"%(xblock,yblock),
      print pair
      decisions = wrapperInterpolate(m,pair[0],pair[1])
      for decision in decisions:newpoints.append(generateSlot(m,decision,xblock,yblock))
  
  print "Interpolation: Number of new points generated: ", len(newpoints)
  for ij in newpoints:
    print ij.obj
  
  if(len(newpoints)==0):
    findex,sindex = extrapolateCheck(xblock,yblock)
    if(findex==None and sindex==None):
      print "In a tight spot..somewhere in the desert"
    else:
      decisions = wrapperextrapolate(m,findex,sindex)
      for decision in decisions: newpoints.append(generateSlot(m,decisions,xblock,yblock))
  
      print "Extrapolation: Number of new points generated: ", len(newpoints)
      for ij in newpoints:
        print ij.obj
  

  
def main():
  m='model'
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
  decisionMaker(m,5,6)
  #wrapperextrapolate(m,405,607)


if __name__ == '__main__':
 # _interpolate()
  main()
  #_extrapolate()
  #_neighbourhood()
