#!/usr/bin/env python
### from within python, I can type 
#execfile("sim_game_topology_scaling_dynamics.py")

from game_topology_scaling_dynamics import *
import cProfile
from time import clock
#import simplejson ###stackoverflow python-write-a-list-to-a-file
import sys
import csv

def runClassifyAttractors(i, reps=10000):
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

def runAttractorFairness(i, reps=10000, useGini=True):
    space = OrdinalGameSpace(i)
    space.ngamesrecommended=reps
    #print( "players: %d\noutcomes: %d"%(i,space.noutcomes) )
    #print( "games, total: (2^%d)!^%d\ngames, sample size: %d"%(i, i, space.ngamesrecommended ) )
    space.populateGameSpace( space.ngamesrecommended, True  )
    games = space.attractorGames( space.games.values() )
    ### start to measure ineqaulity of each game
    nstrats = len(space.orderedStrategySets)
    inequalitiesGames = [0] * len( games )
    inequalitiesOutcomes = [0] * len( games )
    inequalityGame =  [0] * nstrats
    for j, g in enumerate( games ):
        ### get average geni of all of this game's outcomes
        for k, o in enumerate(space.orderedStrategySets):
            if useGini:
                inequalityGame[k] = gini( g.outcomes[ o ] )
            else:
                inequalityGame[k] = np.var( g.outcomes[ o ] / nstrats )
        inequalitiesGames[j] = np.mean( inequalityGame )
        ### now just on its one nash outcome
        if useGini:
            inequalitiesOutcomes[j] = gini( g.outcomes[g.foundNashEq[0]] )
        else:
            inequalitiesOutcomes[j] = np.var( g.outcomes[g.foundNashEq[0]]  / nstrats )
    return( (i, np.mean( inequalitiesGames ), np.mean( inequalitiesOutcomes ) ) )

#http://planspace.org/2013/06/21/how-to-calculate-gini-coefficient-from-raw-data-in-python/
def gini(list_of_values):
    sorted_list = sorted(list_of_values)
    height, area = 0, 0
    for value in sorted_list:
        height += value
        area += height - value / 2.
    fair_area = height * len(list_of_values) / 2.
    return (fair_area - area) / fair_area

with open("./sim_inequality_dataout.txt", "w") as output:
    csvwriter = csv.writer(output)
    #for i in tuple([2,9,8, 9,8,9,8,7,7,9,8,9,8,10]):
    #for i in (6,7,8):
    for i in range(2,9):
        #start = clock()
        out = runAttractorFairness(i, 100000)
        csvwriter.writerow( out )
        print( out )
    out = runAttractorFairness(9, 10000)
    csvwriter.writerow( out )
    print( out )

### # in R
### library(ggplot2)
### sizes <- 2:9
### unfairGame <- c(0.11549823633156965, 0.2043476318026391 , 0.24915603960198865, 
###                  0.27397074170401914, 0.28808446224417095, 0.29693421118742458, 0.30269643433195914, 0.3067281221615708 )
### unfairOutcome <- c( 0.051587301587301571 , 0.10640309885233581 , 0.13704308541023494 , 
###                  0.15771847461723548 , 0.16837088043409834 , 0.17528690842329989 , 0.17948750254140727 , 0.17910942249101042)
### unf <- data.frame(systemSize=c(sizes,sizes), measure=c(rep("game", length(sizes)), c(rep("outcome", length(sizes)) ) ), 
###                                        geni=c(unfairGame, unfairOutcome))
### ggplot( unf[unf$measure == "outcome",], aes(x=systemSize, y=geni, group=measure) ) + 
###                          geom_line() + scale_y_continuous( limits=c(0,0.25) )  + 
###                          scale_x_discrete( limits=2:9 ) + theme_bw()
