gonw = lambda x: x - 101
gow = lambda x: x-1
gosw = lambda x: x + 99
gos = lambda x: x + 100
gose = lambda x: x +101
goe = lambda x: x+1
gone = lambda x: x - 99
gon = lambda x: x-100

for i in xrange(1,9):
  for j in xrange(1,9):
    print "%d   "%(i*100+j),
  print


print gonw(406),gow(406),gosw(406),gos(406),gose(406),goe(406)