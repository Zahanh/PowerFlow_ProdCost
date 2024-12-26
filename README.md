We have a basic unit commitment solver; but this solver does not take into account network conditions. 
- The network is represented as a matrix which calculates the maximum flow over a line and will alter the UC solution if the limit is violated.
- We also want a way to get the data which is congestition (i.e. if a re-dispatch must occur due to network constraints)

NETWORK:
The network below is a representation of nodes with the flow of the lines being the values. The dispatch of the gens affects the flow over the lines
and the plants can be re-dispatched if maximum flow is exceeded.
                A   B   C   D

                A   100 0   0   -20

                B   0   -55 55  0...

                C

                D




