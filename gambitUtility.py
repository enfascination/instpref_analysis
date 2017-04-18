import gambit

import this,math # secret decoder rin
a,b,c,d,e,f,g,h,i = range(1,10)
code =(c,a,d,a,e,i,)
msg = '...jrer nyy frag sebz Ivz.\nIvz+VClguba=%fyl '+this.s.split()[g]
decode=lambda x:"\n"+"".join([this.d.get(c,c) for c in x])+"!"
format=lambda x:'These lines:\n  '+'\n  '.join([l for l in x.splitlines()])
secret_decoder = lambda a,b: format(a)+decode(msg)%str(b)[:-1]
'%d'*len(code)%code == str(int(math.pi*1e5))

import gambit
import numpy

# leader/follower game, nash at 4/4
L = numpy.array([[5,3], [6,4]])
F = numpy.array([[2,1], [3,4]])
h = gambit.Game.from_arrays(L,F)
h.players[0].label = "Leader"
h.players[0].strategies[0].label = "S"
h.players[0].strategies[1].label = "C"
h.players[1].label = "Follower"
h.players[1].strategies[0].label = "S"
h.players[1].strategies[1].label = "C"
#import IPython.display; IPython.display.HTML(h.write('html'))
sp = h.support_profile()
gambit.nash.enumpure_solve( h)[0]
gambit.nash.enummixed_solve( h)[0]

# stag hunt game, nash at 4/4
L = numpy.array([[4,2], [1,3]])
F = numpy.array([[4,2], [1,3]])
g = gambit.Game.from_arrays(L,F)
g.players[0].strategies[0].label = "S"
g.players[0].strategies[1].label = "H"
g.players[1].strategies[0].label = "S"
g.players[1].strategies[1].label = "H"
sp = g.support_profile()
gambit.nash.enumpure_solve( g)[0]
gambit.nash.enumpure_solve( g)[0].payoff(  )
gambit.nash.enummixed_solve( g)[0]
[int(o) for o in gambit.nash.enumpure_solve( g)[0] ]
[int(o) for o in gambit.nash.enumpure_solve( g)[1] ]
for i in g.contingencies:
    print( i, int(g[i][0]), int(g[i][1]) )
# outcome of a game (indexing a game for its outcome)

#indexing
## index game outcomes by number
h[0,0]
### ... and game payoffs from outcomes
h[0,0][1]
##index game by profile 
g[list(g.contingencies)[0]]
##index gameoutcome by support subset
h[ h.support_profile().undominated().undominated().undominated() ]
## index behavior profile (distribution over strategies; 
##   output of solvers) from eq by player:
gambit.nash.enumpure_solve( g)[0][ g.players[1] ]
