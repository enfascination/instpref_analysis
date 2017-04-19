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
#import gambit

from pprint import pprint
from game_topology_scaling_dynamics import OrdinalGameSpace
from ordinalGameSolver import EmpiricalOrdinalGame2P
import copy
import csv
import json
settings = json.load(open('settings.json', encoding='utf-8'))

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
def changeChoicePerspective( sStrat ):
    if sStrat == "Top":
        return( "Left" )
    elif sStrat == "Bottom":
        return( "Right" )
    elif sStrat == "Left":
        return( "Top" )
    elif sStrat == "Right":
        return( "Bottom" )
def changeOutcomePerspective( outcome ):
    s1, s2 = outcome.split(',')
    # note reversal of s1 and s2
    return( changeChoicePerspective( s2 ) + ',' + changeChoicePerspective( s1 ) )

def buildChooseGameIdToQuestionHash(  questionArray ):
    idsToQuestions = {}
    for oData in questionArray:
        #more easily queryable alternative/clone for deep queires
        dq = DictQuery(oData)
        # pprint( oData )
        #if oData["theData"]['type'] == 'chooseStrategy':
        #if dq.get("theData/type") == 'chooseStrategy':
        if oData.get("theDataConsummated") :
            q = oData["theDataConsummated"]
        else :
            q = oData["theData"]
        idsToQuestions[ oData["_id"] ] = q
    return( idsToQuestions)

# now let me index on (round, type, asst)
def buildRndToQuestionHash(  questionArray ):
    qs = DictQuery({})  ## more easily queryable
    for oData in questionArray:
        q = oData["theDataConsummated"] if oData.get("theDataConsummated") else oData["theData"]
        ### guide vars
        asst = q["mtAssignmentId"]
        sec = q["sec"]
        rnd = q["sec_rnd"]
        qtype = q["type"]
        #mtId = q["mtWorkerId"]
        #qOId = q["matchingGameId"]
        ## build hash on index: asst, rnd, type
        if not qs.get(asst): qs[asst] = {}
        if not qs.get(asst).get(sec): qs[asst][sec] = {}
        if not qs.get(asst).get(sec).get(rnd): qs[asst][sec][rnd] = {}
        if not qs.get(asst).get(sec).get(rnd).get(qtype): qs[asst][sec][rnd][qtype] = {}
        qs[asst][sec][rnd][qtype] = q
    return( qs )

def enrichQuestionObject(  q, qdb ):
    # now do some merging from neighboring questions
    asst = q["mtAssignmentId"]
    sec = q["sec"]
    rnd = q["sec_rnd"]
    qtype = q["type"]
    mtid = q["mtWorkerId"]
    qOId = q["matchingGameId"]
    # for round 1 or 2 question
    #     get preferred choice question from same round 
    #     get expected choice question from same round 
    #     get expected outcome question from previous question
    #     get choice from matching round 4 question (if exists)
    if (rnd == 0 or rnd == 1 ) and qtype == "chooseStrategy":
        # get preferred choice question from same round 
        qPref = qdb[asst][sec][rnd]["chooseOutcome"]
        assert qPref["text"][0:13] != "Hypothetically", qPref["text"][0:13]
        assert qPref["title"] == "Question 1.2" or qPref["title"] == "Question 2.2", qPref
        q["outcomePreferred"] = qPref["choice"]
        q["outcomePreferredID"] = qPref["_id"]

        qPred = qdb[asst][sec][rnd]["chooseStrategyTop"]
        assert qPred["title"] == "Question 1.3" or qPred["title"] == "Question 2.3", qPred
        q["choicePredicted"] = qPred["choice"]
        q["choicePredictedID"] = qPred["_id"]
        q["outcomePredicted"] = q["choice"] + ',' + q['choicePredicted']

        if not qdb[asst][sec].get(4): return( q )
        qRepeat = qdb[asst][sec][4]["chooseStrategy"]
        assert qRepeat["title"] == "Question 4" or qRepeat["title"] == "Question", qRepeat
        q["choiceRepeated"] = qRepeat["choice"]
        q["choiceRepeatedID"] = qRepeat["_id"]
    else:
        print("PROBLEM OFJDFLJG8: why did you even call me?", rnd, qtype, q)
    return( q )

def enrichQuestionObjectOtherPlayer(  q, iddb, qdb ):
    # now do some merging from neighboring questions
    asst = q["mtAssignmentId"]
    sec = q["sec"]
    rnd = q["sec_rnd"]
    qtype = q["type"]
    mtid = q["mtWorkerId"]
    qOtherID = q["matchingGameId"]
    qOther = iddb[qOtherID]
    asstOther = qOther["mtAssignmentId"]
    secOther = qOther["sec"]
    rndOther = qOther["sec_rnd"]
    qtypeOther = qOther["type"]
    assert rnd == rndOther, json.dumps(q, indent=1) + json.dumps(qOther, indent=1)
    assert qOther["matchingGameId"] == q["_id"], json.dumps(q, indent=1) + json.dumps(qOther, indent=1)
    # for round 1 or 2 question
    #     get preferred choice from other player's matching question 
    #     get expected choice from other player's matching question 
    #     get choice from other player's matching question 
    if (rnd == 0 or rnd == 1 ) and qtype == "chooseStrategy":
        #qPred = qdb[asst][sec][rnd]["chooseStrategyTop"]
        #assert qPred["title"] == "Question 1.3" or qPred["title"] == "Question 2.3", qPred
        #q["choicePredicted"] = qPred["choice"]
        #q["outcomePredictedID"] = qPred["_id"]
        qPrefO = qdb[asstOther][secOther][rndOther]["chooseOutcome"]
        qPredO = qdb[asstOther][secOther][rndOther]["chooseStrategyTop"]
        q["choiceOther"] = changeChoicePerspective( qOther["choice"] )
        q["outcomePreferredOther"] = changeOutcomePerspective( qPrefO["choice"] )
        q["choicePredictedOther"] = changeChoicePerspective( qPredO["choice"] )
        q["outcomePredictedOther"] = changeOutcomePerspective( qOther["choice"] + ',' + qPredO["choice"] )
        if not qdb[asstOther][secOther].get(4): return( q )
        qRepeatO = qdb[asstOther][secOther][4]["chooseStrategy"]
        q["choiceRepeatedOther"] = changeChoicePerspective( qRepeatO["choice"] )
        pass
    else:
        print("PROBLEM IOFDL: this is fine except why did you even call me?", rnd, qtype, q)
    return( q )

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
    rndsToQuestions =  buildRndToQuestionHash( gameChoices )
    #idsToQuestionsR0R1 =  buildChooseGameIdToQuestionHash( gameChoices ,[0,1])
    #idsToQuestionsR4 =  buildChooseGameIdToQuestionHash( gameChoices ,[4])
    twoPSpace = OrdinalGameSpace(2)
    nGameCount = 0
    with open(sOut, 'w') as fOut:
        features = [ "gameRT", "nPNash", "nWPNash", "wwGame", "effGameF", "effGameO", "gratFGameF", "gratOGameF", "predGameF", "gratGameO", "predGameO", "cnssGame", "stratCertGame" ]
        featuresNOT = ["effGame", "habitGameF", "habitGameO", "expdGameF", "expdGameO", "gratGameF", ]
        ## diff level
        features.extend(["block","expdGameF","expdGameO","outRT"])
        fCSV = csv.DictWriter( fOut, fieldnames=features )
        fCSV.writeheader()
        for game in gameChoices:
            #print( game['theData']['type'] )
            q = game['theData']
            if q['type'] == 'chooseGame':
                # pprint( game['theData'] )
                # print( "1:", idsToQuestions[ q["idGameQ1"] ].payoffs, q["payoffsGame1"] )
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
                g1Q = enrichQuestionObject(g1Q, rndsToQuestions )
                g2Q = enrichQuestionObject(g2Q, rndsToQuestions )
                if not g1Q["matchingGameId"] is None:
                    g1Q = enrichQuestionObjectOtherPlayer(g1Q, idsToQuestions, rndsToQuestions )
                if not g2Q["matchingGameId"] is None:
                    g2Q = enrichQuestionObjectOtherPlayer(g2Q, idsToQuestions, rndsToQuestions )
                if not all( (f in g1Q and f in g2Q) for f in ["outcome", "choiceRepeated", "choiceRepeatedOther"] ):
                    print("FAIL q1 or q2 incomplete keys", g1Q["_id"], g2Q["_id"] )
                    #print("FAIL q1 or q2 incomplete keys", g1Q.keys(), g2Q.keys() )
                    continue

                ## create game object
                g1Game = expPayoffToGame( q["payoffsGame1"], twoPSpace )
                g2Game = expPayoffToGame( q["payoffsGame2"], twoPSpace )

                #pprint(g1Q)

                #print("INtrospect", q['sec'], q['treatment'])
                # caluc firtst game
                g1 = {}
                # choice rather than game property related
                g1["gameRT"] = ( g1Q["choiceMadeTime"] - g1Q["choiceLoadedTime"] ) / 10000 # not g1Q["choiceSubmittedTime"]
                g1["gratGameF"] = 1 if g1Q['outcomePreferred'] == g1Q['outcome'] else 0
                g1["gratFGameF"] = 1 if g1Q['outcomePreferred'].partition(',')[0] == g1Q['outcome'].partition(',')[0] else 0
                g1["gratOGameF"] = 1 if g1Q['outcomePreferred'].partition(',')[2] == g1Q['outcome'].partition(',')[2] else 0
                g1["predGameF"] = 1 if g1Q['outcomePredicted'] == g1Q['outcome'] else 0
                ## i obviously can't put habitGameF in the model.  talk about selection bias
                #g1["habitGameF"] = 1 if (g1Q['choice'] == g1Q['choiceRepeated']) else 0
                #print(g1Q['outcome'], g1Q['choice'], g1Q['outcomePreferred'], g1Q['choicePredicted'], (g1Q['choice'] + ',' + g1Q['choicePredicted']))
                # other player
                print( g1Q['outcome'], g1Q['outcomePreferred'], g1Q['outcomePreferredOther'], g1Q['outcomePredicted'], g1Q['outcomePredictedOther'] )
                g1["gratGameO"] = 1 if g1Q['outcomePreferredOther'] == g1Q['outcome'] else 0
                g1["predGameO"] = 1 if g1Q['outcomePredictedOther'] == g1Q['outcome'] else 0
                #g1["habitGameO"] = 1 if (g1Q['choiceOther'] == g1Q['choiceRepeatedOther']) else 0
                g1["cnssGame"] = 1 if g1Q['outcomePreferred'] == g1Q['outcomePreferredOther'] else 0
                g1["stratCertGame"] = 1 if g1Q['outcomePredicted'] == g1Q['outcomePredictedOther'] else 0

                # game properties
                g1["nPNash"] = len( g1Game.findNashEq() )
                g1["nWPNash"] = len( g1Game.findWeakNashEq() )
                g1["wwGame"] = 1 if g1Game.isWinWin() else 0
                g1["effGame"] = g1Game.efficiencyOfGame()
                g1["effGameF"] = g1Game.efficiencyOfGame(0)
                g1["effGameO"] = g1Game.efficiencyOfGame(1)

                # secodn game
                g2 = {}
                g2["gameRT"] = ( g2Q["choiceMadeTime"] - g2Q["choiceLoadedTime"] ) / 10000
                g2["gratGameF"] = 1 if g2Q['outcomePreferred'] == g2Q['outcome'] else 0
                g2["gratFGameF"] = 1 if g2Q['outcomePreferred'].partition(',')[0] == g2Q['outcome'].partition(',')[0] else 0
                g2["gratOGameF"] = 1 if g2Q['outcomePreferred'].partition(',')[2] == g2Q['outcome'].partition(',')[2] else 0
                g2["predGameF"] = 1 if (g2Q['choice'] + ',' + g2Q['choicePredicted']) == g2Q['outcome'] else 0
                #g2["habitGameF"] = 1 if (g2Q['choice'] == g2Q['choiceRepeated']) else 0
                g2["gratGameO"] = 1 if g2Q['outcomePreferredOther'] == g2Q['outcome'] else 0
                g2["predGameO"] = 1 if g2Q['outcomePredictedOther'] == g2Q['outcome'] else 0
                #g2["habitGameO"] = 1 if (g2Q['choiceOther'] == g2Q['choiceRepeatedOther']) else 0
                g2["cnssGame"] = 1 if g2Q['outcomePreferred'] == g2Q['outcomePreferredOther'] else 0
                g2["stratCertGame"] = 1 if g2Q['outcomePredicted'] == g2Q['outcomePredictedOther'] else 0
                g2["nPNash"] = len( g2Game.findNashEq() )
                g2["nWPNash"] = len( g2Game.findWeakNashEq() )
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
                    if f in chosenGame:
                        diffGame[f] = chosenGame[f] - otherGame[f]

                # diff-level controls
                diffGame["block"] = 0 if q['sec'] == "experiment1" else 1
                diffGame["expdGameF"] = 0 if q['treatment'] == "nofeedback" else 1
                diffGame["expdGameO"] = 1 if q['treatment'] == "nofeedback" else 0  # necessarily the opposite in this staggered deisgn
                diffGame["outRT"] = ( g2Q["choiceMadeTime"] - g2Q["choiceLoadedTime"] ) / 10000
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


import unittest
class TestOrdinalGame(unittest.TestCase):

    def setUp(self):
        #self.twoSpace = OrdinalGameSpace(2)
        #self.pd = EmpiricalOrdinalGame2P( np.array([[[3,3],[1,4]],[[4,1],[2,2]]] ))
        #self.sh = EmpiricalOrdinalGame2P( np.array([[[3,3],[1,2]],[[2,1],[4,4]]] ))
        with open(
            settings["dataTest"] + 'SubDataTestSample.json',
            'r',
            encoding='utf-8'
        ) as testFile:
            self.gameChoices = json.load(testFile)

    def test_buildChooseGameIdToQuestionHash(self):
        qHash = buildChooseGameIdToQuestionHash( self.gameChoices )
        q1 = qHash["aDsp4bhaLxWM9NDnt"]
        self.assertTrue( qHash.get("aDsp4bhaLxWM9NDnt"), "PROBLEM: "+ json.dumps(q1) )
        self.assertEqual( q1["choiceLoadedTime"], 1491924056516.0,  "PROBLEM: "+ json.dumps(q1) )
        #np.testing.assert_array_equal( self.sh.payoffsOfPlayer(0), np.array([3,1,2,4]) )
        #np.testing.assert_array_equal( self.sh.payoffsOfPlayer(1), np.array([3,2,1,4]) )

    def test_buildRndToQuestionHash( self ):
        qHash = buildRndToQuestionHash( self.gameChoices )
        q1 = qHash["3M0BCWMB8VW9HRSLQPHEG8SSQ56WB9"]["experiment1"][1]["chooseStrategy"]
        self.assertEqual( q1["_id"], "aDsp4bhaLxWM9NDnt", "PROBLEM: "+ json.dumps(q1) )
        self.assertEqual( q1["choiceLoadedTime"], 1491924056516.0,  "PROBLEM: "+ json.dumps(q1) )
        q1 = qHash["3M0BCWMB8VW9HRSLQPHEG8SSQ56WB9"]["experiment1"][0]["chooseOutcome"]
        self.assertEqual( q1["_id"], "TrywhPxnyFSbpkiZa", "PROBLEM: "+ json.dumps(q1) )
        self.assertEqual( q1["choiceLoadedTime"], 1491924045731.0, "PROBLEM: "+ json.dumps(q1) )
        q1 = qHash["33FOTY3KEMLZQV4O71OOY28GCDYC1Y"]["survey"][0]["dropdown"]
        self.assertEqual( q1["_id"], "x4pXuDqNxtRAr2hep", "PROBLEM: "+ json.dumps(q1) )
        self.assertEqual( int( q1["choice"] ), 3, "PROBLEM: "+ json.dumps(q1) )
        #self.pd.findNashEq()
        #self.sh.findNashEq()
        #self.assertEqual( len( self.pd.foundNashEq ), 1)
        #self.assertEqual( len( self.sh.foundNashEq ), 2)
        #np.testing.assert_array_equal( self.pd.outcomes[ self.pd.foundNashEq[0] ], np.array([2,2]) )

    def test_enrichQuestionObject( self ):
        qIdHash = buildChooseGameIdToQuestionHash( self.gameChoices )
        qRndHash = buildRndToQuestionHash( self.gameChoices )
        q1 = qIdHash["aDsp4bhaLxWM9NDnt"]
        qnew = enrichQuestionObject( q1, qRndHash)
        self.assertTrue( qnew.get( "outcomePreferredID", qnew ) )
        self.assertEqual( qnew["outcomePreferredID"], "dsKwc27cCJyyLovyd"  )
        self.assertEqual( qnew["outcomePreferred"], qIdHash[ qnew["outcomePreferredID"] ]["choice"]  )
        self.assertTrue( qnew.get( "outcomePredictedID", qnew ) )
        self.assertEqual( qnew["choicePredictedID"], "4PvmaGuw4gq4BBikj" )
        self.assertEqual( qnew["choicePredicted"], qIdHash[ qnew["choicePredictedID"] ]["choice"]  )
        self.assertTrue( qnew.get( "choiceRepeatedID", qnew ) )
        self.assertEqual( qnew["choiceRepeatedID"], "Nhiu2HeQKuxKBHKBu" )
        self.assertEqual( qnew["choiceRepeated"], qIdHash[ qnew["choiceRepeatedID"] ]["choice"]  )

    def test_changePerspective( self ):
        self.assertEqual( "Top,Left" , changeOutcomePerspective( "Top,Left" ))
        self.assertEqual( "Bottom,Left" , changeOutcomePerspective( "Top,Right" ))


testing = False
if testing :
    print("testing")
    #gameChoices = json.load(open(
        #settings["dataTest"] + 'SubDataTestSample.json',
        #'r',
        #encoding='utf-8'
    #))
    #print("HKDSLJK", len(gameChoices))
    #qHash = buildChooseGameIdToQuestionHash( gameChoices )
    #print( len(qHash), qHash.keys() )

    unittest.main()
else:
    sIn = settings["data"]+"v1_20170418_first100/"
    main( sIn, settings["data"]+"s2/out.csv" )


