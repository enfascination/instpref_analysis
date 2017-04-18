### boilerplate for living in the past
#import future        # pip install future
#import builtins      # pip install future
#import past          # pip install future
#import six           # pip install six
#from __future__ import unicode_literals    # at top of module
#from __future__ import division
#from builtins import int
#from builtins import str
#from builtins import range
#from builtins import dict
#from builtins import range
#from io import open

import pickle
from pprint import pprint
from game_topology_scaling_dynamics import OrdinalGameSpace
from ordinalGameSolver import EmpiricalOrdinalGame2P
import copy
import csv

### for handling deeply nested objects
###  https://www.haykranen.nl/2016/02/13/handling-complex-nested-dicts-in-python
class DictQuery(dict):
    def get(self, path, default = None):
        keys = path.split("/")
        val = None

        for key in keys:
            if val:
                if isinstance(val, list):
                    val = [ v.get(key, default) if v else None for v in val]
                else:
                    val = val.get(key, default)
            else:
                val = dict.get(self, key, default)

            if not val:
                break;

        return val
class DQ(DictQuery):
    pass

# fns
def showPayoff( aPayoff):
    return aPayoff


def buildChooseGameIdToQuestionHash(  questionArray ):
    idsToQuestions = {}
    for q in questionArray:
        # pprint( q )
        #if q["theData"]['type'] == 'chooseStrategy':
        if DQ(q).get("theData/type") == 'chooseStrategy':
            idsToQuestions[ q["_id"] ] = q["theDataConsummated"] if q.get("theDataConsummated") else q["theData"]
        # now do some merging from neighboring questions
    return( idsToQuestions )

def buildChooseGameIdToPayoffHash(  questionArray ):
    idsToPayoffs = {}
    for q in questionArray:
        # pprint( q )
        if q["theData"]['type'] == 'chooseStrategy':
            idsToPayoffs[ q["_id"] ] = q["theData"]["payoffs"]
    return( idsToPayoffs )

def gprint( payoffs ):
    p = payoffs
    print()
    print("  %d |   %d"%(p[4], p[6]))
    print("%d   | %d  "%(p[0], p[1]))
    print("----|----")
    print("  %d |   %d"%(p[5], p[7]))
    print("%d   | %d  "%(p[2], p[3]))
    # print(payoffs)
    print()

def expPayoffToGame( payoffs, gameSpace ):
    g1in = list(zip( payoffs[0:4], [payoffs[4],payoffs[6],payoffs[5],payoffs[7],]))
    g1o = gameSpace.populateEmptyGameTree( list(reversed(g1in)), copy.deepcopy( gameSpace.gameskeleton) )
    g1 = EmpiricalOrdinalGame2P( g1o )
    return( g1 )

def main( sIn, sOut ):
    gameChoices = pickle.load(open(sIn + 'SubData.p', 'rb'))
    idsToQuestions =  buildChooseGameIdToQuestionHash( gameChoices )
    #idsToQuestionsR0R1 =  buildChooseGameIdToQuestionHash( gameChoices ,[0,1])
    #idsToQuestionsR4 =  buildChooseGameIdToQuestionHash( gameChoices ,[4])
    idsToPayoffs = buildChooseGameIdToPayoffHash( gameChoices )
    twoPSpace = OrdinalGameSpace(2)
    nGameCount = 0
    with open(sOut, 'w') as fOut:
        features = [ "block", "RT", "nPNash", "wwGame", "effGame", "effGameF", "effGameO", "expdGameF", "expdGameO", ]
        fCSV = csv.DictWriter( fOut, fieldnames=features )
        fCSV.writeheader()
        for game in gameChoices:
            #print( game['theData']['type'] )
            q = game['theData']
            if q['type'] == 'chooseGame':
                # pprint( game['theData'] )
                # print( "1:", idsToPayoffs[ q["idGameQ1"] ], q["payoffsGame1"], showPayoff( q["payoffsGame1"] ) )
                # print( "2:", idsToPayoffs[ q["idGameQ2"] ], q["payoffsGame2"] )
                # print()
                # gprint(q["payoffsGame2"])
                nGameCount += 1
                g1Q = idsToQuestions[ q["idGameQ1"] ]
                g2Q = idsToQuestions[ q["idGameQ2"] ]
                g1Game = expPayoffToGame( q["payoffsGame1"], twoPSpace )
                g2Game = expPayoffToGame( q["payoffsGame2"], twoPSpace )

                pprint(g1Q)

                # caluc firtst game
                g1 = {}
                # controls
                g1["block"] = 0 if q['sec'] == "experiment1" else 1
                g1["expdGameF"] = 0 if q['treatment'] == "nofeedback" else 1
                g1["expdGameO"] = 1 if q['treatment'] == "nofeedback" else 2  # necessarily the opposite in this staggered deisgn
                # choice rather than game property related
                g1["RT"] = ( g1Q["choiceMadeTime"] - g1Q["choiceLoadedTime"] ) / 10000 # not g1Q["choiceSubmittedTime"]
                #
                g1["nPNash"] = len( g1Game.findNashEq() )
                g1["wwGame"] = 1 if g1Game.isWinWin() else 0
                g1["effGame"] = g1Game.efficiencyOfGame()
                g1["effGameF"] = g1Game.efficiencyOfGame(0)
                g1["effGameO"] = g1Game.efficiencyOfGame(1)

                # secodn game
                g2 = {}
                g2["block"] = 0 if q['sec'] == "experiment1" else 1
                g2["expdGameF"] = 0 if q['treatment'] == "nofeedback" else 1
                g2["expdGameO"] = 1 if q['treatment'] == "nofeedback" else 2
                g2["RT"] = ( g2Q["choiceMadeTime"] - g2Q["choiceLoadedTime"] ) / 10000
                g2["nPNash"] = len( g2Game.findNashEq() )
                g2["wwGame"] = 1 if g2Game.isWinWin() else 0
                g2["effGame"] = g2Game.efficiencyOfGame()
                g2["effGameF"] = g2Game.efficiencyOfGame(0)
                g2["effGameO"] = g2Game.efficiencyOfGame(1)

                # game to diff
                if q["choice"] == q["idGameQ1"]:
                    chosenGame = g1
                    otherGame = g2
                else:
                    chosenGame = g2
                    otherGame = g1

                # get diff
                diffGame = {}
                for f in features:
                    diffGame[f] = chosenGame[f] - otherGame[f]

                ### output
                ### csvwriter
                print(features)
                print( [ chosenGame[f] for f in features ] )
                print( [ otherGame[f] for f in features ] )
                print( [ diffGame[f] for f in features ] )
                print()
                fCSV.writerow( diffGame )



                #pprint( idsToQuestions[ q["idGameQ1"] ] )

        pass
    #print( len( idsToPayoffs ))
    print( len( gameChoices ), nGameCount)

sIn = "../instpref/data/v1_writable_20170411/"
main( sIn, "./data/s2/out.csv" )
import gambit
