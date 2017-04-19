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
        return( np.sum( out ) )

    def payoffsOfPlayer( self, player):
        topRowOs = self.outcomes[0]
        bottomRowOs = self.outcomes[1]
        topRowPsPx = np.array( tuple(zip( *topRowOs ))[player] )
        bottomRowPsPx = np.array( tuple(zip( *bottomRowOs ))[player] )
        return( np.append( topRowPsPx, bottomRowPsPx ) )

    def findNashEq(self):
        for s in self.strategySet:
            self.isNash( s )
        return( self.foundNashEq )

    def findOnlyWeakNashEq(self):
        for s in self.strategySet:
            self.isNash( s, weakOnly=True )
        return( self.foundWeakNashEq )

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
    def isNash(self, strategy_set, weakOnly=False):
        # do both players prefer this outcome?
        dominationOfOutcome = []
        for iplayer in range(0,self.nplayers):
            # payoff of this outcome
            playerPayoff = self.payoff( strategy_set, iplayer )
            # payoff of alternative outcome
            playerAltPayoff = self.payoff( self.flip( strategy_set, iplayer ), iplayer )
            # is this outcome preferred
            if not weakOnly:
                dominationOfOutcome.append( playerPayoff > playerAltPayoff )
            else:
                dominationOfOutcome.append( playerPayoff == playerAltPayoff )
            #print( list( self.outcomes ), strategy_set, iplayer, playerPayoff, playerAltPayoff, dominationOfOutcome, all( dominationOfOutcome ) )
        # ( add to obj's own list of its eqs )
        if all( dominationOfOutcome ) and not strategy_set in self.foundNashEq: 
            if not weakOnly:
                self.foundNashEq.append( strategy_set )
            else:
                self.foundWeakNashEq.append( strategy_set )
        # do both players prefer this outcome?
        return( all( dominationOfOutcome ) )


import unittest
class TestOrdinalGame(unittest.TestCase):

    def setUp(self):
        self.twoSpace = OrdinalGameSpace(2)
        self.pd = EmpiricalOrdinalGame2P( np.array([[[3,3],[1,4]],[[4,1],[2,2]]] ))
        self.sh = EmpiricalOrdinalGame2P( np.array([[[3,3],[1,2]],[[2,1],[4,4]]] ))
        self.unfair1 = EmpiricalOrdinalGame2P( np.array([[[4,1],[4,1]],[[1,4],[1,4]]] ))
        self.nongame1 = EmpiricalOrdinalGame2P( np.array([[[4,4],[4,4]],[[1,1],[1,1]]] ))
        self.nongame2 = EmpiricalOrdinalGame2P( np.array([[[4,4],[4,1]],[[1,4],[1,1]]] ))

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

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

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
