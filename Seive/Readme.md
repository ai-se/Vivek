TODO
====

1. I don't have any nearness checking function. This means that as of now I am just assuming the interpolation and extrapolation is creating points in the same cluster, which may or may not be true.

2. At the point(10-27) the algorithm is a greedy one since it doesn't use any bad neighbours. I should add some changes. I am not sure how to do it...just use some magic constants.

3. Validation as usual is always a problem. I am still not sure how would this pan out.

4. The code is really crappy. I need to use write it more succintly. Mr. Krishna suggested that I should use decorators. Any ideas? Please take a look at checkextrapolation


