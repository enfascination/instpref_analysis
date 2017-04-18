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

from pprint import pprint
from game_topology_scaling_dynamics import OrdinalGameSpace
from ordinalGameSolver import EmpiricalOrdinalGame2P
import copy
import csv
import json
settings = json.load(open('settings.json', encoding='utf-8'))
print(settings)

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
    for oData in questionArray:
        #more easily queryable alternative/clone for deep queires
        dq = DictQuery(oData)
        # pprint( oData )
        #if oData["theData"]['type'] == 'chooseStrategy':
        if dq.get("theData/type") == 'chooseStrategy':
            q = oData["theDataConsummated"] if oData.get("theDataConsummated") else oData["theData"]
            idsToQuestions[ oData["_id"] ] = q
    return( idsToQuestions)

# now let me index on (round, type, asst)
def buildRndToQuestionHash(  questionArray ):
    qs = DictQuery({})  ## more easily queryable
    for oData in questionArray:
        q = oData["theDataConsummated"] if oData.get("theDataConsummated") else oData["theData"]
        ### guide vars
        rnd = q["sec_rnd"]
        qtype = q["type"]
        asst = q["mtAssignmentId"]
        #mtId = q["mtWorkerId"]
        #sec = q["sec"]
        #qOId = q["matchingGameId"]
        ## build hash on index: asst, rnd, type
        if not qs.get(asst): qs[asst] = {}
        if not qs.get(asst).get(rnd): qs[asst][rnd] = {}
        if not qs.get(asst).get(rnd).get(qtype): qs[asst][rnd][qtype] = {}
        qs[asst][rnd][qtype] = q
    return( qs )

def enrichQuestionObject(  questionArray ):
    # now do some merging from neighboring questions
    for oData in questionArray:
        q = idsToQuestions[ oData["_id"] ]
        sec = q["sec"]
        rnd = q["sec_rnd"]
        qtype = q["type"]
        mtWId = q["mtWorkerId"]
        mtAsstId = q["mtAssignmentId"]
        qOId = q["matchingGameId"]
        # for round 1 or 2 question
        #     get preferred choice question from same round 
        #     get expected choice question from same round 
        #     get expected outcome question from previous question
        #     get choice from matching round 4 question (if exists)
        #     get choice from other player's matching question 
        #     get preferred choice from other player's matching question 
        #     get expected choice from other player's matching question 
        if rnd == 0 or rnd == 1:
            pass
    return( idsToQuestions )

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
    gameChoices = json.load(open(sIn + 'SubData.json', 'r', encoding='utf-8'))
    idsToQuestions =  buildChooseGameIdToQuestionHash( gameChoices )
    #idsToQuestionsR0R1 =  buildChooseGameIdToQuestionHash( gameChoices ,[0,1])
    #idsToQuestionsR4 =  buildChooseGameIdToQuestionHash( gameChoices ,[4])
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
                # print( "1:", idsToQuestions[ q["idGameQ1"] ].payoffs, q["payoffsGame1"], showPayoff( q["payoffsGame1"] ) )
                # print( "2:", idsToQuestions[ q["idGameQ2"] ].payoffs, q["payoffsGame2"] )
                # print()
                # gprint(q["payoffsGame2"])
                nGameCount += 1
                #pprint( q )
                g1Q = idsToQuestions.get( q["idGameQ1"], False)
                g2Q = idsToQuestions.get( q["idGameQ2"], False)
                if not g1Q:
                    print("FAIL question q1", g1Q, q["idGameQ1"] )
                    continue
                if not g2Q:
                    print("FAIL question q2", g2Q, q["idGameQ2"] )
                    continue
                g1Game = expPayoffToGame( q["payoffsGame1"], twoPSpace )
                g2Game = expPayoffToGame( q["payoffsGame2"], twoPSpace )

                #pprint(g1Q)

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
                #print(features)
                #print( [ chosenGame[f] for f in features ] )
                #print( [ otherGame[f] for f in features ] )
                #print( [ diffGame[f] for f in features ] )
                #print()
                fCSV.writerow( diffGame )



                #pprint( idsToQuestions[ q["idGameQ1"] ] )

        pass
    #print( len( idsToQuestions ))
    print( len( gameChoices ), nGameCount)

sIn = settings["data"]+"v1_20170418_first100/"
main( sIn, settings["data"]+"s2/out.csv" )
import gambit
