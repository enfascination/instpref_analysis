from game_topology_scaling_dynamics import *
import numpy as np
import copy

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

import unittest
class TestOrdinalGame(unittest.TestCase):

    def setUp(self):
        self.twoSpace = OrdinalGameSpace(2)
        self.pd = EmpiricalOrdinalGame2P( np.array([[[3,3],[1,4]],[[4,1],[2,2]]] ))
        self.sh = EmpiricalOrdinalGame2P( np.array([[[3,3],[1,2]],[[2,1],[4,4]]] ))

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
