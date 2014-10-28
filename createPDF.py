#
#   Usage: python createPDF.py hw1/baseline.py csc710sbse:hw1:VivekNair:vnair2
#

from __future__ import division
import sys,os
sys.dont_write_bytecode = True

def doSomethingCool():
  if(len(sys.argv) > 3):
    print "createPDF.py filename comment"
  filename = sys.argv[1]
  comment = sys.argv[2]
  if(os.path.isfile(filename)== False):
    print "Check your file path"
    return
  command1 = "a2ps --center-title=\""+str(comment)+"\" -qr1gC -f6 -o ./temp.ps " + str(filename)
  print command1
  os.system(command1)
  command2 = "ps2pdf ./temp.ps ./" + str(filename.split(".")[0])+".pdf"
  print command2
  os.system(command2)
  os.system("rm -f temp.ps")

if __name__ == '__main__':
  doSomethingCool();


