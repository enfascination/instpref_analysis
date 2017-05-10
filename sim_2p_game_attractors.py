#!/usr/bin/env python
### from within python, I can type 
#execfile("sim_game_topology_scaling_dynamics.py")

from game_topology_scaling_dynamics import *
from ordinalGameSolver import    Ordinal2PGameSpace, EmpiricalOrdinalGame2P
import cProfile
from time import clock
#import simplejson ###stackoverflow python-write-a-list-to-a-file
import sys
import numpy as np

def run():
    space = Ordinal2PGameSpace()
    space.ngamesrecommended = 10000
    space.populateGameSpace( space.ngamesrecommended, False, strictlyOrdinal=True )
    games = space.attractorGames( space.games.values() )
    print( "all games:", len( space.games.values() ) )
    print( "all games:", len( set( space.games.values() ) ) )
    print( "all games, sans symm:", len( space.uniqueGames( space.games.values() ) ) )
    print( "attractors:", len( games ) )
    print( "attractors:", len( set( games ) ) )
    print( "all games, sans sym", len( space.uniqueGames( games )))
    return( space.uniqueGames( games ) )

games = run()
games44 = []
games43 = []
games42 = []
gamesother = []
for g in games:
    if np.all( g.outcomes[ g.foundNashEq[0] ] == (4,4)) :
        games44.append(g)
    elif np.all( g.outcomes[ g.foundNashEq[0] ] == (4,3)) :
        games43.append(g)
    elif np.all( g.outcomes[ g.foundNashEq[0] ] == (4,2)) :
        games42.append(g)
    else:
        gamesother.append(g)
print( "games in 44:%d, 43:%d, 42:%d, other:%d"%( len(games44), len(games43), len(games42), len(gamesother) ) )
print()
print("44s")
[ g.gprint() for g in games44 ]
print()
print("43s")
[ g.gprint() for g in games43 ]
print()
print("42s")
[ g.gprint() for g in games42 ]
