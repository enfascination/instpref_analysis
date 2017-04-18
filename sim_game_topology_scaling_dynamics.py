#!/usr/bin/env python
### from within python, I can type 
#execfile("sim_game_topology_scaling_dynamics.py")

from game_topology_scaling_dynamics import *
import cProfile
from time import clock
#import simplejson ###stackoverflow python-write-a-list-to-a-file
import sys
import gc

def run(i, reps=10000):
  space = OrdinalGameSpace(i)
  space.ngamesrecommended=reps
  #print( "players: %d\noutcomes: %d"%(i,space.noutcomes) )
  #print( "games, total: (2^%d)!^%d\ngames, sample size: %d"%(i, i, space.ngamesrecommended ) )
  space.populateGameSpace( space.ngamesrecommended, True  )
  dist = space.classifyGameAttractors( space.games.values() )
  for j in range(i+3):
    commentary = "%d winner attractor games "%j
    if j==0: commentary="%d winner games (non-attractors)"%j
    elif j==i: commentary="%d winner games (win-win attractors)"%j
    elif j==i+1: commentary="games without Nash eq."
    elif j==i+2: commentary="games with multiple Nash eq."
    #print( "%s: %d"%(commentary, dist[j]) )
  
  #print( "attractor games: %d  win-win games: %d"%(len(attractors),len(winwinattractors)) )
  #print( "mean length of trajectories: %d"%(0,) )
  dist = list(dist)
  dist.append(i)
  dist.append(reps)
  return( dist )

#output = open("/Users/fry/Desktop/remote_runs/topology/dataout.txt", "w")
for i in tuple([2,9,8, 9,8,9,8,7,7,9,8,9,8,10]):
  #start = clock()
  for j in range(20):
    out = run(i, 1000)
    print( out )
    #output.write( " ".join(list(out)))
    #simplejson.dump(out,output)
    sys.stdout.flush()
    #gc.collect()
  #cProfile.run('run()')
  #print( (clock() - start) )
  #print(  )
