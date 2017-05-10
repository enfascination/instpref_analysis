#!/usr/bin/env python
### from within python, I can type 
#execfile("game_topology_scaling_dynamics.py")

#an ordinal game is a normal form economic game with n players and m strategies
#a strategy is what a player chooses. all players strategies are a list that uniquely determines anoutcome out of the list of outcomes that defines a game.
import numpy as np
from random import shuffle, sample
from copy import deepcopy
import itertools
from pprint import pprint
#from math import factorial
#from scipy import factorial
def factorial(n):
  if n <= 0: return( 1 )
  else: return( n*factorial(n-1) )






class OrdinalGame(object):
  def __init__(self, n):
    self.nplayers = n
    self.nstrategies = 2
    self.noutcomes = 2**n
    self.outcomes = np.array([])
    self.name = ""
    self.__gameid = ""
    self.foundNashEq = []
    self.foundWeakNashEq = []
    self.ntests = 0 ### the number of times that this game has been probed for equilibria (the number of strategy sets that have been tested)
  ### changes one player's strategy in the list of strategies
  def flip(self, strategy_set, player):
    newStrats = list(strategy_set) 
    newStrats[player] = 1 if strategy_set[player] == 0 else 0
    return( tuple(newStrats) )
  #### i'll eventually have to generalize out of two strategies per player, but this isn't how that is going to happen
  #def flip(self, strategy_set, player, newStrategy):
    #newStrats = list(strategy_set) 
    #newStrats[player] = newStrategy
    #return( tuple(newStrats) )
  def outcome(self, strategy_set):
    pass
  def payoff(self, strategy_set, player):
    return( self.outcomes[strategy_set][player] )
  ### has a side effect of adding the strategy set to the list of equilibria
  def isNash(self, strategy_set):
    if all( [ (self.payoff(strategy_set, i) > self.payoff(self.flip(strategy_set, i), i ) ) for i in range(0,self.nplayers) ] ):
      if not strategy_set in self.foundNashEq: self.foundNashEq.append( strategy_set )
      return( True )
    ## also test for weak nash
    if all( [ (self.payoff(strategy_set, i) == self.payoff(self.flip(strategy_set, i), i ) ) for i in range(0,self.nplayers) ] ):
      if not strategy_set in self.foundWeakNashEq: self.foundWeakNashEq.append( strategy_set )
    else: return( False )
  ### two player, now generalized
  #def isNash(self, strategy_set):
    #if ((self.payoff(strategy_set, 0) >= self.payoff(self.flip(strategy_set, 0), 0 ) ) and
         #(self.payoff(strategy_set, 1) >= self.payoff(self.flip(strategy_set, 1), 1) ) )  :
      #return( True )
    #else: return( False )
  ### identify each game with a unique string
  def gameID(self):
    if self.__gameid != "":
      return( self.__gameid )
    else:
      #def subgameID(anArrayofArrays):
        #flattened = ""
        #if type(anArrayofArrays) == type(int()): return( str(anArrayofArrays) )
        #elif type(anArrayofArrays) == type(int64()): return( str(anArrayofArrays) )
        #else: 
          #for i in range(0, len(anArrayofArrays)):
            #flattened = flattened + subgameID(anArrayofArrays[i])
        #return( flattened )
      #self.__gameid = subgameID(self.outcomes)
      #print(  self.outcomes )
      #print(  self.outcomes.flatten() )
      #print( [i for i in tuple( self.outcomes.flatten() ) ] )
      self.__gameid = "".join(["%d"%i for i in tuple( self.outcomes.flatten( ) ) ] )
      return( self.__gameid )

  def findNashEq( self, strats, prospectiveAttractor=False):
    """ with the prospective attractor argument, this saves time by stopping early if the game has 
    multiple Nash eq (and is thus not an attractor)  """
    for i in range(len(strats)):
      self.isNash( strats[i] )
      self.ntests += 1
      if prospectiveAttractor and (len(self.foundNashEq) > 1): break

class OrdinalGameSpace(object):
  def __init__(self, n):
    self.nplayers=n
    self.noutcomes = 2**n
    self.ngames = factorial(2**n)**n
    self.games = {}
    self.attractorgames = {}
    self.winwinattractorgames = {}
    self.nstrategysetsrecommended = min(2**self.nplayers, 10000)
    self.ngamesrecommended = min(10 * 10**self.nplayers, 10000)
    #self.nstrategysetsrecommended = min(2**self.nplayers, 5000)
    #self.ngamesrecommended = 10 * 10**self.nplayers
    self.orderedStrategySets = self.generateOrderedStrategySets()
    ### make an empty game tree with the right number of players
    self.gameskeleton = []
    for i in range(0, self.nplayers): 
      self.gameskeleton = [deepcopy(self.gameskeleton), deepcopy(self.gameskeleton) ]

  def generateRandomStrategySet( self):
    strategy = []
    for i in range(0, self.nplayers):
      strategy.append(sample([0,1],1)[0])
    return( tuple(strategy) )

  def generateRandomStrategySets( self, reps, replace=True):
    """ hould generate with and without replacement, but I haven't implemented the second yet 
    (which will be handy for large-but-not-astronomical spaces)"""
    print("random sets is happening")
    return( [ self.generateRandomStrategySet() for i in [1]*reps ] )

  def generateNextStrategySet( self, previousss):
    strategy = list(previousss)
    strategy = np.array(strategy)
    strategy = strategy[::-1]
    for i in range(0,len(strategy)):
      if strategy[i] == 0: 
        strategy[i] = 1
        strategy[0:i] = 0
        break
    strategy = strategy[::-1]
    return( tuple(strategy) )

  def generateOrderedStrategySets( self):
    strategy_sets = [(0,)*self.nplayers,]
    for i in range(2**self.nplayers-1): strategy_sets.append( self.generateNextStrategySet(strategy_sets[i]) )
    return( strategy_sets )

  ### work through the tree
  ### a helper function for generating random ordinal games
  def populateEmptyGameTree( self, outcomes, skeleton ):
    if len(skeleton) == 0:
      return( outcomes.pop() )
    else:
      for i in range(0, len(skeleton)):
        skeleton[i] = self.populateEmptyGameTree(outcomes, skeleton[i] )
      return( np.array(skeleton) )

  ### a skeleton game is a game in which, for each outcome gives each player a payoff of a different unique consecutive integer from 1 to 2**nplayers.
  ###  another way of saying this is that payoffs are selected from a series without replacement
  def generateRandomOrdinalGame( self, strictlyOrdinal=True):
    grow = deepcopy(self.gameskeleton)
    ### generate possible outcomes
    potentialOutcomes = list(zip( *[ np.random.choice(range(1,2**self.nplayers+1),2**self.nplayers, replace = (not strictlyOrdinal)) for i in [1]*self.nplayers ] ) )
    tmp = OrdinalGame(self.nplayers)
    tmp.outcomes = self.populateEmptyGameTree(potentialOutcomes, grow)
    #print("trest")
    #pprint(potentialOutcomes )
    #pprint(tmp.outcomes )
    #print()
    return( tmp )
  #space = OrdinalGameSpace(4)
  #h = space.generateRandomOrdinalGame()
  #h.outcomes

  ### does the game have a unique nash eq with at least one highest-possible-payoff in its payoffs?
  def gameIsAttractor( self, aGame):
    if len(aGame.foundNashEq) != 1: return( False )
    if aGame.ntests < self.nstrategysetsrecommended:
      print("Warning OIUFD: game has been tested with %d < %d steps"%(aGame.ntests, self.nstrategysetsrecommended))
    return( aGame.outcomes[aGame.foundNashEq[0]][0]==2**self.nplayers )
  ### does the game have a unique nash eq with all payoffs as the highest possible? 

  def gameIsWinWinAttractor( self, aGame):
    if len(aGame.foundNashEq) != 1: return( False )
    if aGame.ntests < self.nstrategysetsrecommended:
      print("Warning FLKD: game has been tested with %d < %d steps"%(aGame.ntests, self.nstrategysetsrecommended))
    return( all( aGame.outcomes[aGame.foundNashEq[0]] == 2**self.nplayers ) )

  def populateGameSpace( self, reps, prospectiveAttractor):
    for i in range(reps):
      game = self.generateRandomOrdinalGame()
      #if not aGame.gameID() in self.games: self.games[aGame.gameID()] = aGame
      self.games[game.gameID()] = game
      ### check all strategies for nashhood
      if self.noutcomes > reps: 
        game.findNashEq(self.generateRandomStrategySets(reps), prospectiveAttractor)
      else: 
        game.findNashEq(self.orderedStrategySets, prospectiveAttractor)
      ### stop populating when all games have been found
      if len(self.games) == self.ngames: break

  def winWinAttractorGames( self, games):
    attractors = []
    for game in games:
      if self.gameIsWinWinAttractor(game): attractors.append(game)
    return( attractors )

  def attractorGames( self, games):
    attractors = []
    for game in games:
      if self.gameIsAttractor(game): attractors.append(game)
    return( attractors )

  def classifyGameAttractors( self, games ):
    categories = [0,]*(self.nplayers+3)
    for game in games:
      #print(len(game.foundNashEq), [game.outcomes[s] for s in game.foundNashEq], )
      if len(game.foundNashEq)==0: 
        categories[self.nplayers+1] += 1
        #print("none")
      elif len(game.foundNashEq)>1: 
        categories[self.nplayers+2] += 1
        #print ( "mult" )
      else: 
        categories[sum([payoff == 2**self.nplayers for payoff in game.outcomes[game.foundNashEq[0]]])] += 1
        #print (sum([payoff == self.nplayers for payoff in game.outcomes[game.foundNashEq[0]]]) , [payoff == self.nplayers for payoff in game.outcomes[game.foundNashEq[0]]], game.outcomes[game.foundNashEq[0]])
    return( np.array(categories) )

if __name__ == '__main__':
  g = OrdinalGame(2)
  g.outcomes = np.array([[[3,3],[1,4]],[[4,1],[2,2]]] )
  #g.outcomes = np.array((((3,3),(1,4)),((4,1),(2,2))) )
  g.name = "pd"
  #print ( g.outcomes )
  print(" test flipping of strategy sets" )
  print(all( g.outcomes[0][0] == g.outcomes[(0,0)] ) )
  print(all( [3,3] == g.outcomes[(0,0)] ) )
  print(g.outcomes[0][0][1] == 3 )
  print(g.flip([0,0],1) == (0,1) )
  print(g.flip([0,0],0)== (1,0) )
  strategy_set = [0,0]
  strategy_set = (0,0)
  print( " test indexing of outcomes via strategy sets" )
  print( g.outcomes[strategy_set[0]][strategy_set[1]][1] == g.outcomes[strategy_set][1] )
  print( g.outcomes[strategy_set[0]][strategy_set[1]][1] == 3 )
  print( g.payoff(strategy_set, 1) ==  3 )
  print( g.payoff(g.flip(strategy_set, 1), 1 ) == 4 )
  print( g.payoff(g.flip(strategy_set, 0), 1 ) == 1 )
  print( " test Nash testing" )
  print( g.isNash((0,0)) == False )
  print( g.isNash((1,0)) == False )
  print( g.isNash((0,1)) == False )
  print( g.isNash((1,1)) == True )

  print( " test three player games" )
  threep = OrdinalGame(3)
  threep.outcomes = np.array( [[[[1,1,1],[0,0,0]],[[0,0,0],[4,0,0]]], [[[0,0,0],[0,4,0]],[[0,0,4],[3,3,3]]]] )
  # if all agree then all get a payoff.  but if they are the only one to pick strategy one, they get lots more.
  threep2 = OrdinalGame(3)
  threep2.outcomes = np.array( [[[[1,1,1],[0,0,0]],[[0,0,0],[4,0,0]]], [[[0,0,0],[0,4,0]],[[0,0,4],[5,5,5]]]] )
  # if all agree then all get a payoff.  but if they are the only one to pick strategy one, they get lots more.
  s1 = (0,0,0) 
  s2 = (1,1,1) 
  s3 = (1,0,1) 
  s4 = (1,0,0) 
  print( all(threep.outcomes[s1] == [1,1,1]) )
  print( all(threep.outcomes[s3] == [0,4,0]) )
  print( all(threep.flip(s3, 1)== s2 ) )
  print( " test 3p Nash testing" )
  print( threep.flip(s4, 0)==s1 )
  print( threep.isNash(s1) == True )
  print( threep.isNash(s2) ==False )
  print( threep.isNash(s3) ==False )
  print( threep.isNash(s4) ==False )
  print( " more 3p Nash testing" )
  print( threep2.isNash(s1) == True )
  print( threep2.isNash(s2) == True )
  print( threep2.isNash(s3) ==False )
  print( threep2.isNash(s4) ==False )
  s = """
  So the number of strategies 

  OK, i've got the number of win-win games
  """


  print( " tests for two space" )
  ### count the number of 2x2 games
  twoSpace = OrdinalGameSpace(2)
  for i in range(0, 10000):
    aGame = twoSpace.generateRandomOrdinalGame()
    if not aGame.gameID() in twoSpace.games: twoSpace.games[aGame.gameID()] = aGame
  print( len(twoSpace.games.keys())/4 == 144  )
  print( len(twoSpace.winwinattractorgames.keys())/4 == 36 )
  print( )
  print( " test heuristic Nash hunting" )
  fourSpace = OrdinalGameSpace(4)
  h = fourSpace.generateRandomOrdinalGame()
  h.outcomes
  h.findNashEq( fourSpace.orderedStrategySets, False)
  print( h.foundNashEq )

