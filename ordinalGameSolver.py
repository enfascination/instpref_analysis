from game_topology_scaling_dynamics import *
import numpy as np
import copy

def outcomeToIdx( outcome ):
    if outcome == "Top,Left":
        return( tuple((0,0)) )
    elif outcome == "Top,Right":
        return( tuple((0,1)) )
    elif outcome == "Bottom,Left":
        return( tuple((1,0)) )
    elif outcome == "Bottom,Right":
        return( tuple((1,1)) )

def outcomeDiff( outcome ):
    return -np.diff(outcome)[0]

class Ordinal2PGameSpace(OrdinalGameSpace):

    def __init__(self):
        super(  Ordinal2PGameSpace, self).__init__(2)

    def generateRandomOrdinalGame( self, strictlyOrdinal=True):
        """ change internal game format in use """
        grow = deepcopy(self.gameskeleton)
        ### generate possible outcomes (but not in proper internal game format )
        potentialOutcomes = list(zip( *[ np.random.choice(range(1,2**self.nplayers+1),size=2**self.nplayers, replace=(not strictlyOrdinal)) for i in [1]*self.nplayers ] ) )
        #print( potentialOutcomes )
        tmp = EmpiricalOrdinalGame2P( self.populateEmptyGameTree(potentialOutcomes, grow) )
        return( tmp )

    def populateGameSpace( self, reps, prospectiveAttractor, strictlyOrdinal=True):
        """ change to use internal game object's own new and simpler nash solver"""
        for i in range(reps):
            game = self.generateRandomOrdinalGame(strictlyOrdinal)
            self.games[game.gameID()] = game
            ### check all strategies for nashhood
            game.findNashEq()
            ### stop populating when all games have been found
            if len(self.games) == self.ngames: break

    def gamesShareSymmetries( self, g1, g2 ):
        g2o = np.copy( g2.outcomes )
        g2o2 = np.copy( g2.outcomes )
        g2o3 = np.copy( g2.outcomes )
        g2o4 = np.copy( g2.outcomes )
        g2o5 = np.copy( g2.outcomes )
        # flip p1
        g2o2[0] = g2o[1]
        g2o2[1] = g2o[0]
        # flip p2
        g2o3[(0,0)] = g2o[(0,1)]
        g2o3[(0,1)] = g2o[(0,0)]
        g2o3[(1,0)] = g2o[(1,1)]
        g2o3[(1,1)] = g2o[(1,0)]
        # flip both
        g2o4[(0,0)] = g2o2[(0,1)]
        g2o4[(0,1)] = g2o2[(0,0)]
        g2o4[(1,0)] = g2o2[(1,1)]
        g2o4[(1,1)] = g2o2[(1,0)]
        # flip both, another way
        g2o5[(0,0)] = g2o[(1,1)]
        g2o5[(0,1)] = g2o[(1,0)]
        g2o5[(1,0)] = g2o[(0,1)]
        g2o5[(1,1)] = g2o[(0,0)]
        # double checking my work
        assert( (g2o4 == g2o5).all() )
        g2o6 = np.flipud( g2.outcomes )
        g2o7 = np.fliplr( g2.outcomes )
        assert( (g2o2 == g2o6).all() )
        assert( (g2o3 == g2o7).all() )
        # is game 1 equal to any version of game 2?
        return((g1.outcomes == g2o).all() or
            (g1.outcomes == g2o2).all() or
            (g1.outcomes == g2o3).all() or
            (g1.outcomes == g2o4).all()
            )

    def uniqueGames(self, games ):
        """ this function returns a list of games with games that share symmetries removed """
        ngl = []
        for ng in games:
            gameIsOld = any( [ self.gamesShareSymmetries( ng, og ) for og in ngl ] )
            if not gameIsOld:
                ngl.append( ng )
        return( ngl )

class EmpiricalOrdinalGame2P(OrdinalGame):

    def __init__(self, outcomes):
        super(EmpiricalOrdinalGame2P, self).__init__(2)
        self.parentSpace = OrdinalGameSpace(2)
        self.strategySet = self.parentSpace.orderedStrategySets
        self.outcomes = outcomes

    def isWinWin( self ):
        payoffsP0 = self.payoffsOfPlayer( 0 )
        payoffsP1 = self.payoffsOfPlayer( 1 )
        return( np.argmax(payoffsP0) == np.argmax(payoffsP1) )

    def efficiencyOfGame( self, player=False):
        payoffsP0 = self.payoffsOfPlayer( 0 )
        payoffsP1 = self.payoffsOfPlayer( 1 )
        out = np.array([])
        if player is False:
            out = np.append(payoffsP0, payoffsP1)
        elif player == 0:
            out = payoffsP0
        elif player == 1:
            out = payoffsP1
        return( int( np.sum( out ) ) )

    def meanEfficiencyOfStrategies( self, strategy_set, player):
        return( np.mean([ self.outcomes[s][player] for s in strategy_set ]) )

    def payoffsOfPlayer( self, player):
        topRowOs = self.outcomes[0]
        bottomRowOs = self.outcomes[1]
        topRowPsPx = np.array( tuple(zip( *topRowOs ))[player] )
        bottomRowPsPx = np.array( tuple(zip( *bottomRowOs ))[player] )
        return( np.append( topRowPsPx, bottomRowPsPx ) )

    def findNashEq(self):
        for s in self.strategySet:
            self.isNash( s )
            self.ntests += 1
        return( self.foundNashEq )


    def outcomeDominates(self, strategy_set, iplayer, weakOnly=False):
        # payoff of this outcome
        playerPayoff = self.payoff( strategy_set, iplayer )
        # payoff of alternative outcome
        playerAltPayoff = self.payoff( self.flip( strategy_set, iplayer ), iplayer )
        # is this better than alternative
        if weakOnly:
            return( playerPayoff == playerAltPayoff )
        else:
            return( playerPayoff >  playerAltPayoff )

    def choiceDominates(self, strategy, iplayer, weakOnly=False):
        if iplayer == 0:
            out1 = tuple((strategy, 0))
            out2 = tuple((strategy, 1))
        elif iplayer == 1:
            out1 = tuple((0, strategy))
            out2 = tuple((1, strategy))
        return( self.outcomeDominates( out1, iplayer, weakOnly) and self.outcomeDominates( out2, iplayer, weakOnly) )

    def outcomeCommands(self, strategy_set, iplayer):
        """ Determine whether this outcome commands the other. Commanding is like dominating except calculated over others payoffs instead of my own. If my choice commands, I have unilateral power to provide an outcome that would dominate or be dominated if I was maximizing only your earnings."""
        ioplayer = 0 if iplayer == 1 else 1
        # payoff of this outcome
        otherPlayerPayoff = self.payoff( strategy_set, ioplayer )
        # payoff of alternative outcome
        otherPlayerAltPayoff = self.payoff( self.flip( strategy_set, iplayer ), ioplayer )
        #print( "inoutcome", list(self.outcomes), strategy_set, otherPlayerPayoff, otherPlayerAltPayoff)
        # is this better than alternative
        if otherPlayerPayoff == otherPlayerAltPayoff:
            return(0)
        elif otherPlayerPayoff >  otherPlayerAltPayoff:
            return(1)
        elif otherPlayerPayoff <  otherPlayerAltPayoff:
            return(-1)

    def choiceCommands(self, strategy, iplayer):
        if iplayer == 0:
            out1 = tuple((strategy, 0))
            out2 = tuple((strategy, 1))
        elif iplayer == 1:
            out1 = tuple((0, strategy))
            out2 = tuple((1, strategy))
        out1Command = self.outcomeCommands( out1, iplayer)
        out2Command = self.outcomeCommands( out2, iplayer)
        #print( list(self.outcomes), strategy, iplayer, out1Command, out2Command)
        if out1Command == out2Command:
            return( out1Command)
        else:
            return( False)

    ## rewrite of parent fn just for clarity (this works, as tested)
    def isNash(self, strategy_set):
        # do both players prefer this outcome?
        dominationOfOutcome = []
        weakDominationOfOutcome = []
        for iplayer in range(0,self.nplayers):
            # payoff of this outcome
            playerPayoff = self.payoff( strategy_set, iplayer )
            # payoff of alternative outcome
            playerAltPayoff = self.payoff( self.flip( strategy_set, iplayer ), iplayer )
            # is this outcome preferred
            weakDominationOfOutcome.append( playerPayoff == playerAltPayoff )
            dominationOfOutcome.append( playerPayoff > playerAltPayoff )
            #print( list( self.outcomes ), strategy_set, iplayer, playerPayoff, playerAltPayoff, dominationOfOutcome, all( dominationOfOutcome ) )
        # ( add to obj's own list of its eqs )
        if all( weakDominationOfOutcome ) and not strategy_set in self.foundWeakNashEq: 
            self.foundWeakNashEq.append( strategy_set )
        if all( dominationOfOutcome ) and not strategy_set in self.foundNashEq: 
            self.foundNashEq.append( strategy_set )
        # do both players prefer this outcome?
        return( all( dominationOfOutcome ) )

    def outcomesPivoted( self ):
        out = self.outcomes
        pout = np.copy( self.outcomes )
        pout[(0,0,0)] = out[(0,0,1)]
        pout[(0,1,0)] = out[(1,0,1)]
        pout[(1,0,0)] = out[(0,1,1)]
        pout[(1,1,0)] = out[(1,1,1)]
        pout[(0,0,1)] = out[(0,0,0)]
        pout[(0,1,1)] = out[(1,0,0)]
        pout[(1,0,1)] = out[(0,1,0)]
        pout[(1,1,1)] = out[(1,1,0)]
        return( pout )

    def isSymmetric( self ):
        out = self.outcomes
        pout = self.outcomesPivoted()
        return( ( out == pout ).all() )

    def gprint( self):
        p = self.outcomes
        print()
        print("  %d |   %d"%(p[(0,0,1)], p[(0,1,1)]))
        print("%d   | %d  "%(p[(0,0,0)], p[(0,1,0)]))
        print("----|----")
        print("  %d |   %d"%(p[(1,0,1)], p[(1,1,1)]))
        print("%d   | %d  "%(p[(1,0,0)], p[(1,1,0)]))
        # print(payoffs)
        print()





import unittest
class TestOrdinalGame(unittest.TestCase):

    def setUp(self):
        #self.twoSpace = OrdinalGameSpace(2)
        self.twoSpace =   Ordinal2PGameSpace()
        self.pd = EmpiricalOrdinalGame2P( np.array([[[3,3],[1,4]],[[4,1],[2,2]]] ))
        self.sh = EmpiricalOrdinalGame2P( np.array([[[3,3],[1,2]],[[2,1],[4,4]]] ))
        self.unfair1 = EmpiricalOrdinalGame2P( np.array([[[4,1],[4,1]],[[1,4],[1,4]]] ))
        self.nongame1 = EmpiricalOrdinalGame2P( np.array([[[4,4],[4,4]],[[1,1],[1,1]]] ))
        self.nongame2 = EmpiricalOrdinalGame2P( np.array([[[4,4],[4,1]],[[1,4],[1,1]]] ))
        self.nongame3 = EmpiricalOrdinalGame2P( np.array([[[4,4],[3,1]],[[1,3],[1,1]]] ))
        self.attractor = EmpiricalOrdinalGame2P( np.array([[[4,3],[2,2]],[[3,1],[1,4]]] ))
        self.weakattractor = EmpiricalOrdinalGame2P( np.array([[[4,4],[1,4]],[[4,1],[1,1]]] ))

        ### now add symmetries of games
        #self.pd =      EmpiricalOrdinalGame2P( np.array([[[3,3],[1,4]],[[4,1],[2,2]]] ))
        self.pd_sym1 = EmpiricalOrdinalGame2P( np.array([[[4,1],[2,2]],[[3,3],[1,4]]] ))
        self.pd_sym2 = EmpiricalOrdinalGame2P( np.array([[[1,4],[3,3]],[[2,2],[4,1]]] ))
        self.pd_sym3 = EmpiricalOrdinalGame2P( np.array([[[2,2],[4,1]],[[1,4],[3,3]]] ))
        self.pd_sym4 = EmpiricalOrdinalGame2P( np.array([[[2,2],[4,1]],[[1,4],[3,3]]] ))
        #self.unfair1 =      EmpiricalOrdinalGame2P( np.array([[[4,1],[4,1]],[[1,4],[1,4]]] ))
        self.unfair1_sym1 = EmpiricalOrdinalGame2P( np.array([[[1,4],[1,4]],[[4,1],[4,1]]] ))
        self.unfair1_sym2 = EmpiricalOrdinalGame2P( np.array([[[4,1],[4,1]],[[1,4],[1,4]]] ))
        self.unfair1_sym3 = EmpiricalOrdinalGame2P( np.array([[[1,4],[1,4]],[[4,1],[4,1]]] ))
        self.clock =      EmpiricalOrdinalGame2P( np.array([[[1,4],[2,3]],[[3,2],[4,1]]] ))
        self.clock_sym1 = EmpiricalOrdinalGame2P( np.array([[[3,2],[4,1]],[[1,4],[2,3]]] ))
        self.clock_sym2 = EmpiricalOrdinalGame2P( np.array([[[2,3],[1,4]],[[4,1],[3,2]]] ))
        self.clock_sym3 = EmpiricalOrdinalGame2P( np.array([[[4,1],[3,2]],[[2,3],[1,4]]] ))
        self.clock_asym = EmpiricalOrdinalGame2P( np.array([[[1,3],[2,2]],[[3,1],[4,4]]] ))
        ## other games to test
        self.cassurance = EmpiricalOrdinalGame2P( np.array([[[4,4],[1,2]],[[3,1],[2,3]]] ))


    def test_payoffsOfPlayer(self):
        np.testing.assert_array_equal( self.sh.payoffsOfPlayer(0), np.array([3,1,2,4]) )
        np.testing.assert_array_equal( self.sh.payoffsOfPlayer(1), np.array([3,2,1,4]) )

    def test_isWinWin(self):
        self.assertEqual('foo'.upper(), 'FOO')
        self.assertFalse( self.pd.isWinWin()  )
        self.assertTrue( self.sh.isWinWin()  )

    def test_efficiencyOfGame( self):
        self.assertEqual( self.pd.efficiencyOfGame(), 20 )
        self.assertEqual( self.sh.efficiencyOfGame(), 20 )
        self.assertEqual( self.pd.efficiencyOfGame( 0 ), 10 )
        self.assertEqual( self.pd.efficiencyOfGame( 1 ), 10 )
        self.assertEqual( self.pd.efficiencyOfGame( 0 ) + self.pd.efficiencyOfGame( 1 ), self.pd.efficiencyOfGame() )

    def test_payoffsToOutcomes( self ):
        #payoffsPrimitive = [3,3,1,4,4,1,2,2]
        payoffsPrimitive = [(3,3),(1,4),(4,1),(2,2)] ## needs reversing
        outcomes = np.array([[[3,3],[1,4]],[[4,1],[2,2]]] )
        skeleton = self.twoSpace.gameskeleton
        np.testing.assert_array_equal( self.twoSpace.populateEmptyGameTree( list(reversed(payoffsPrimitive)), skeleton ), outcomes )

    def test_findNash( self ):
        self.pd.findNashEq()
        self.sh.findNashEq()
        self.assertEqual( len( self.pd.foundNashEq ), 1)
        self.assertEqual( len( self.sh.foundNashEq ), 2)
        np.testing.assert_array_equal( self.pd.outcomes[ self.pd.foundNashEq[0] ], np.array([2,2]) )
        self.cassurance.findNashEq()
        self.assertEqual( len( self.cassurance.foundNashEq ), 2)

    def test_isAttractor( self ):
        self.pd.findNashEq()
        self.sh.findNashEq()
        self.cassurance.findNashEq()
        self.nongame1.findNashEq()
        self.nongame2.findNashEq()
        self.nongame3.findNashEq()
        self.attractor.findNashEq()
        self.weakattractor.findNashEq()
        self.assertFalse( self.twoSpace.gameIsAttractor( self.pd ) )
        self.assertFalse( self.twoSpace.gameIsAttractor( self.sh))
        self.assertFalse( self.twoSpace.gameIsAttractor( self.cassurance))
        self.assertFalse( self.twoSpace.gameIsAttractor( self.nongame1))
        self.assertTrue( self.twoSpace.gameIsAttractor( self.nongame2))
        self.assertTrue( self.twoSpace.gameIsWinWinAttractor( self.nongame2))
        self.assertTrue( self.twoSpace.gameIsAttractor( self.nongame3))
        self.assertTrue( self.twoSpace.gameIsWinWinAttractor( self.nongame3))
        self.assertTrue( self.twoSpace.gameIsAttractor( self.attractor))
        self.assertFalse( self.twoSpace.gameIsWinWinAttractor( self.attractor))
        self.assertFalse( self.twoSpace.gameIsAttractor( self.weakattractor))
        self.assertFalse( self.twoSpace.gameIsWinWinAttractor( self.weakattractor))

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

    def test_outcomeToIdx(self):
        np.testing.assert_array_equal( self.pd.outcomes[ outcomeToIdx("Bottom,Right") ] , np.array([2,2]) )
        np.testing.assert_array_equal( self.pd.outcomes[ outcomeToIdx("Top,Left") ] , np.array([3,3]) )
        self.assertEqual( np.diff( np.array([3,3]) )[0], 0 )
        self.assertEqual( -np.diff( np.array([3,4]) )[0], -1 )
        self.assertEqual( outcomeDiff( [4,3] ), 1 )

    def test_dominanceTests(self):
        self.assertFalse( self.pd.outcomeDominates( (0,0), 0) )
        self.assertTrue( self.pd.outcomeDominates( (1,1), 0) )
        self.assertTrue( self.pd.outcomeDominates( (1,1), 1) )

        self.assertTrue( self.sh.outcomeDominates( (1,1), 1) )
        self.assertTrue( self.sh.outcomeDominates( (0,0), 1) )
        self.assertFalse( self.sh.outcomeDominates( (1,0), 1) )

        self.assertFalse( self.pd.choiceDominates( 0, 0) )
        self.assertFalse( self.pd.choiceDominates( 0, 1) )
        self.assertTrue( self.pd.choiceDominates( 1, 0) )
        self.assertTrue( self.pd.choiceDominates( 1, 1) )

        self.assertFalse( self.sh.choiceDominates( 0, 0) )
        self.assertFalse( self.sh.choiceDominates( 0, 1) )
        self.assertFalse( self.sh.choiceDominates( 1, 0) )
        self.assertFalse( self.sh.choiceDominates( 1, 1) )

        self.assertTrue( self.nongame1.choiceDominates( 0, 0))
        self.assertFalse( self.nongame1.choiceDominates( 0, 1))
        self.assertFalse( self.weakattractor.choiceDominates( 0, 0))
        self.assertFalse( self.weakattractor.choiceDominates( 0, 1))
        self.assertFalse( self.nongame1.choiceDominates( 0, 0, weakOnly=True ))
        self.assertTrue( self.nongame1.choiceDominates( 0, 1, weakOnly=True ))
        self.assertTrue( self.weakattractor.choiceDominates( 0, 0, weakOnly=True ))
        self.assertTrue( self.weakattractor.choiceDominates( 0, 1, weakOnly=True ))

    def test_commandTests(self):
        ### these are defined in setUp()
        #self.unfair1 = EmpiricalOrdinalGame2P( np.array([[[4,1],[4,1]],[[1,4],[1,4]]] ))
        #self.nongame1 = EmpiricalOrdinalGame2P( np.array([[[4,4],[4,4]],[[1,1],[1,1]]] ))
        #self.nongame2 = EmpiricalOrdinalGame2P( np.array([[[4,4],[4,1]],[[1,4],[1,1]]] ))
        self.assertEqual( self.sh.choiceCommands( 1, 1) , False)
        self.assertEqual( self.unfair1.choiceCommands( 0, 0), -1 )
        self.assertEqual( self.unfair1.choiceCommands( 1, 0), 1 )
        self.assertEqual( self.unfair1.choiceCommands( 0, 1), 0 )
        self.assertEqual( self.nongame1.choiceCommands( 0, 0), 1 )
        self.assertEqual( self.nongame1.choiceCommands( 0, 1), 0 )
        self.assertEqual( self.nongame2.choiceCommands( 0, 0), 0 )
        self.assertEqual( self.pd.choiceCommands( 1, 1) , -1)

    def test_meanEfficiencyOfStrategies( self ):
        self.sh.findNashEq()
        self.assertEqual( self.sh.meanEfficiencyOfStrategies([(0,0),(1,1)], 0), 3.5 )
        self.assertEqual( self.sh.meanEfficiencyOfStrategies( self.sh.foundNashEq, 0), 3.5 )
        self.assertEqual( self.pd.meanEfficiencyOfStrategies([(1,0)], 0), 4)
        self.assertEqual( self.pd.meanEfficiencyOfStrategies([(1,0)], 1), 1)

    def test_gamesAreSame( self ):
        self.assertTrue( self.twoSpace.gamesShareSymmetries( self.pd, self.pd_sym1 ) )
        self.assertTrue( self.twoSpace.gamesShareSymmetries( self.pd, self.pd_sym2 ) )
        self.assertTrue( self.twoSpace.gamesShareSymmetries( self.pd, self.pd_sym3 ) )
        self.assertTrue( self.twoSpace.gamesShareSymmetries( self.pd, self.pd_sym4 ) )
        self.assertTrue( self.twoSpace.gamesShareSymmetries( self.pd_sym1, self.pd_sym4 ) )
        self.assertTrue( self.twoSpace.gamesShareSymmetries( self.unfair1, self.unfair1_sym1 ) )
        self.assertTrue( self.twoSpace.gamesShareSymmetries( self.unfair1, self.unfair1_sym2 ) )
        self.assertTrue( self.twoSpace.gamesShareSymmetries( self.unfair1, self.unfair1_sym3 ) )
        self.assertTrue( self.twoSpace.gamesShareSymmetries( self.unfair1_sym1, self.unfair1_sym3 ) )
        self.assertTrue( self.twoSpace.gamesShareSymmetries( self.clock, self.clock_sym1 ) )
        self.assertTrue( self.twoSpace.gamesShareSymmetries( self.clock, self.clock_sym2 ) )
        self.assertTrue( self.twoSpace.gamesShareSymmetries( self.clock, self.clock_sym3 ) )
        self.assertTrue( self.twoSpace.gamesShareSymmetries( self.clock, self.clock_sym3 ) )
        self.assertFalse( self.twoSpace.gamesShareSymmetries( self.clock, self.clock_asym ) )
        self.assertFalse( self.twoSpace.gamesShareSymmetries( self.clock, self.pd ) )
        self.assertFalse( self.twoSpace.gamesShareSymmetries( self.sh, self.pd ) )

    def test_outcomesPivoted( self ):
        ## test symmetric games
        np.testing.assert_array_equal( self.pd.outcomes, self.pd.outcomesPivoted() )
        np.testing.assert_array_equal( self.sh.outcomes, self.sh.outcomesPivoted() )
        # test for np inequality nonequality not equal unequal nonequal
        self.assertFalse( (self.unfair1.outcomes == self.unfair1.outcomesPivoted() ).all() )
        # but double flip should be equal to self
        tmpunfair = copy.deepcopy( self.unfair1 )
        tmpunfair.outcomes = self.unfair1.outcomesPivoted()
        np.testing.assert_array_equal( self.unfair1.outcomes, tmpunfair.outcomesPivoted() )

    def test_isSymmetric( self ):
        self.assertTrue( self.sh.isSymmetric() )
        self.assertTrue( self.pd.isSymmetric() )
        self.assertFalse( self.unfair1.isSymmetric() )
        self.assertFalse( self.nongame1.isSymmetric() )
        self.assertTrue( self.nongame2.isSymmetric() )

    def test_uniqueGames( self ):
        self.assertEqual( len( self.twoSpace.uniqueGames( [self.pd, self.pd] )), 1 )
        self.assertEqual( len( self.twoSpace.uniqueGames( [self.pd, self.sh] )), 2 )
        self.assertEqual( len( self.twoSpace.uniqueGames( [self.pd, self.sh] )), 2 )
        gl1 = [self.clock , self.clock_sym1, self.clock_sym2, self.clock_sym3]
        self.assertEqual( len( self.twoSpace.uniqueGames( gl1 )) , 1)
        gl1.append(self.clock_asym)
        self.assertEqual( len( self.twoSpace.uniqueGames( gl1 )) , 2)

if __name__ == '__main__':

    print('testing')
    #print(OrdinalGameSpace(2).orderedStrategySets)
    #pd = EmpiricalOrdinalGame2P(np.array([[[3,3],[1,4]],[[4,1],[2,2]]] ))
    #print( pd )
    #print( pd.outcomes )
    #print('testing over')
    #twoSpace = OrdinalGameSpace( 2 )
    #payoffsLegacy = list(zip( *[ sample(range(1,2**2+1),2**2) for i in [1]*2 ] ) )
    #payoffsPrimitive = [3,3,1,4,4,1,2,2]
    #outcomes = np.array([[[3,3],[1,4]],[[4,1],[2,2]]] )
    #skeleton = twoSpace.gameskeleton
    #print("legacy", payoffsLegacy)
    #print( "fromlegacy", twoSpace.populateEmptyGameTree( payoffsLegacy, copy.deepcopy( skeleton ) ) )
    #print("skeelcton", skeleton)
    #print("output", outcomes)
    #print("from basic", twoSpace.populateEmptyGameTree( payoffsPrimitive, copy.deepcopy( skeleton ) ) )

    unittest.main()
