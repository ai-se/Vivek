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
threshold =3

There is something wrong with the lambda expressions need to make sure it wraps around.
gonw = lambda x: x - 101
gow = lambda x: x-1
gosw = lambda x: x + 99
gos = lambda x: x + 100
gose = lambda x: x +101
goe = lambda x: x+1
gone = lambda x: x - 99
gon = lambda x: x-100
convert = lambda x,y: (x*100)+y
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
  print "xblock: %d yblock: %d"%(xblock,yblock)
  print "TempIndex>>>>>>>>>: " ,tempIndex
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
  #print "Number of points in ",xindex," is: ",len(dictionary[xindex])
  #print "Number of points in ",yindex," is: ",len(dictionary[yindex])
  xpoints=getpoints(xindex)
  ypoints=getpoints(yindex)
  import itertools 
  listpoints=list(itertools.product(xpoints,ypoints))
  #print "Length of Listpoints: ",len(listpoints)
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
  print "xblock: %d yblock: %d"%(xblock,yblock)
  #print "convert: ",convert(xblock,yblock)
  #print "thresholdCheck(convert(xblock,yblock): ",thresholdCheck(convert(xblock,yblock))
  if(thresholdCheck(convert(xblock,yblock))==False):
    print "Cell is relatively sparse: Might need to generate new points"
    xb,yb=interpolateCheck(xblock,yblock)
    if(xb!=None and yb!=None):
      print thresholdCheck(xb),thresholdCheck(yb)
      decisions = wrapperInterpolate(m,xb,yb)
      print len(decisions)
      if convert(xblock,yblock) in dictionary: pass
      else:
        assert(convert(xblock,yblock)>101),"Something's wrong!" 
        dictionary[convert(xblock,yblock)]=[]
      for decision in decisions:newpoints.append(generateSlot(m,decision,xblock,yblock))
      print "Interpolation works!"
      print "Number of new points generated: ", len(newpoints)
      return True
    else:
      print "Interpolation failed!"
      findex,sindex = extrapolateCheck(xblock,yblock)
      if(findex==None and sindex==None):
        print "In a tight spot..somewhere in the desert RANDOM JUMP REQUIRED"
        return False
      else:
        decisions = wrapperextrapolate(m,findex,sindex)
        if convert(xblock,yblock) in dictionary: pass
        else: 
          assert(convert(xblock,yblock)>101),"Something's wrong!" 
          dictionary[convert(xblock,yblock)]=[]
        for decision in decisions: dictionary[convert(xblock,yblock)].append(generateSlot(m,decision,xblock,yblock))
        print "Extrapolation Worked ",len(dictionary[convert(xblock,yblock)])
        return True
  else:
    findex,sindex = extrapolateCheck(xblock,yblock)
    if(findex==None and sindex==None):
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
  print "listofneighboursBBBBBBBBBBBBBB: ",index
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
      if(len(dictionary[index])>threshold):return True
      else:return False
    except:
      return False

  for i in xrange(1,9):
    for j in xrange(1,9):
      print (convert(i,j)),thresholdCheck(convert(i,j)),
      print "      ",
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

  tries,repeat=0,0
  bmean,biqr=1e6,1e6
  bsoln=[-1,-1]
  while(tries<19):
    print "------------------------------------------------------------------"
    soln = randomcell()
    while(repeat<32):
      print "Solution being tried: %d %d "%(soln[0],soln[1])
      result = generateNew(m,soln[0],soln[1])
      if(result == False): 
        print ">>>>>>>>>>>>>here %d"%tries
        tries+=1
        printNormal()
        break
      else:
        print "*********************************Solution being tried: %d %d "%(soln[0],soln[1])
        mean,iqr = energy(soln[0],soln[1])
        neighbours = listofneighbours(m,soln[0],soln[1])
        for neighbour in neighbours:
          print "neighbour: ",neighbour
          result = generateNew(m,int(neighbour/100),neighbour%10)
          print result
          if(result == True):
            mean,iqr = energy(int(neighbour/100),neighbour%10)
            print ">>>>>>>>>>>>>>Temp Mean:%f IQR: %f"%(mean,iqr)
            if(mean<bmean or (mean == bmean and iqr<biqr)):
              print "&&&&&&&&&&&&&&&&&&&& Better than best found!!"
              bmean = mean
              biqr = iqr
              bsoln = [int(neighbour/100),neighbour%10]
              print "SOLUTION: ",bsoln
          else:
            print "NAAAAAAAAAAAAH"

        print "++++++++++++++++++++++soln: ",soln
        print "++++++++++++++++++++++bsoln: ",bsoln
        if(compare(bsoln,soln)!=True):
          print "##################Found old solution!!: ",bsoln
          print "##################Found new solution!!: ",soln
          soln=bsoln
          print "Mean: %f IQR: %f "%(bmean,biqr)
          repeat+=1
        else:
          tries+=1
          break

  print ">>>>>>>>>>>>>>WOW Mean:%f IQR: %f"%(bmean,biqr)
  print ">>>>>>>>>>>>>>WOW Soultion: ",bsoln



      


def _checkDictionary():
  sum=0
  for i in dictionary.keys():
    sum+=len(dictionary[i])
  print sum

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
  #generateNew(m,3,6)
  #_checkDictionary()
  #wrapperextrapolate(m,405,607)
  searcher(m)
  _checkDictionary()


if __name__ == '__main__':
 # _interpolate()
  main()
  #_extrapolate()
  #_neighbourhood()
