#!/usr/bin/env Rscript
# setwd("/Users/sfrey/projecto/research_projects/instpref/analysis/")
# source("s2_model.r")
library(dplyr)
library(rjson)
library(ggplot2)
settings <- fromJSON( file="settings.json")

prefs <- read.csv(file.path( settings$data, "s2/out.csv"))
RTadj = diff( (prefs %>% 
              group_by(block) %>% 
              summarize(median=median(gameRT))
          )$median)/2
prefs$gameRTctl <- log10( ifelse(prefs$block == 0, prefs$gameRT - RTadj, prefs$gameRT + RTadj) + 1 )
colSums(prefs)
apply(prefs, 2,FUN=table)
str(prefs)
## way too colinear: get rid of gameRT, effGameO effNashO, prefFGameF, prefOGameF, prefOutcomeFSpoilt,  
## symnum( cor(prefs) )

## predict speed of choice
#summary(lm(outRT ~ . - expdGameO - out - gameRT - gameRTctl, prefs))
## predict choice
prefs$out <- 1
prefs$out <- 1
negRows = sample(1:nrow(prefs), nrow(prefs)/2)
prefs[negRows,] <- -prefs[negRows,]
prefs$out[negRows] <- 0
out <- prefs$out

preflm <- prefs
##  http://stackoverflow.com/questions/4605206/drop-data-frame-columns-by-name
drops <- c("effGameO", "effNashO", "prefFGameF", "prefOGameF", "prefOutcomeFSpoilt", "prefOutcomeOSpoilt")
controls_drops <- c("expdGameF", "block", "gameRT", "expdGameO")
preflm <- prefs[ , !(names(prefs) %in% drops)]
preflm <- prefs[ , !(names(prefs) %in% controls_drops)]
summary(lm(out ~ . - outRT, preflm))
summary(lm(out ~ . - outRT, preflm[ preflm$wwChoice == 0, ]))
#summary(lm(out ~ .*. - outRT, preflm))  ## all interactions

### stat learnings
# apply(preflrn, 2,FUN=table)
preflrn <- prefs
### managing sparse ness that is toxic
###apply(as.matrix(preflrn), 2, var)
super_sparse_drops <- c("effGameO", "effNashO", "prefFGameF", "prefOGameF", "prefOutcomeFSpoilt", "prefOutcomeOSpoilt")
sparse_drops <- c("effNashF", "WPNash", "nonGameO", "nonGameF", "indiffO", "indiffF")
controls_drops <- c("expdGameF", "block", "gameRT", "gameRTctl", "expdGameO", "outRT", "out", "wwChoice")
knowability_drops <- c("prefOutcomeO", "predGameO", "cnssPrefOut", "cnssPredOut" )
nonsimulatable_drops <- c("gameRT", "prefFGameF", "prefOGameF", "prefGameF", "predGameO", "prefOutcomeO", "cnssPrefOut", "cnssPredOut", "prefIneqGame", "prefOutcomeF",  "prefOutcomeFSpoilt",    "prefOutcomeOSpoilt",    "block", "expdGameF", "expdGameO",  "outRT", "gameRTctl"  )
nonsimulatable_drops <- c()
winwin_dropped <- c("wwChoice", "wwGame")
winwin_dropped <- c("wwGame")
winwin_dropped <- c()
preflrn <- preflrn[ , !(names(preflrn) %in% c( nonsimulatable_drops, super_sparse_drops, sparse_drops, controls_drops, knowability_drops, winwin_dropped ))]
outlrn <- prefs$out
## and: 
preflrn$PNashn  <- NULL
#preflrn$prefOutcomeO  <- NULL
preflrn$cmndGameF  <- NULL
#preflrn$domGameF  <- NULL
#preflrn$domGameO  <- NULL
#library(elasticnet)
#enet( y=outlrn, x=as.matrix(preflrn), lambda=0)

library(caret)
MyTrainControl=trainControl(
                            method = "repeatedCV",
                            number=2,
                            repeats=100,
                            #returnResamp = "all",
                            #classProbs = TRUE,
                            #summaryFunction=twoClassSummary
                            )
model <- train(outlrn ~ .*.,data=preflrn,method='enet',
                   metric = "RMSE",
                       tuneGrid = expand.grid(fraction=c(0,0.1, 0.5, 0.9, 1),lambda=seq(0,0.05,by=0.01)),
                       trControl=MyTrainControl)
model
plot(model, metric='RMSE')
plot(model$finalModel)
model$bestTune
model$finalModel
enetCoefIsolate <- function(xs, y, model, lambda, toPrint=TRUE) {
    gg <- cv.enet(as.matrix(xs),y=y,lambda=lambda,s=seq(0,1,length=100),mode="fraction",trace=FALSE,max.steps=80, plot.it=toPrint)
    ggfrac <- gg$s[min(which(gg$cv < min(gg$cv) + gg$cv.error[which.min(gg$cv)]  ))]
    #ggfrac
    ggcoef <- predict(model, s=ggfrac, type="coefficients", mode="fraction")
    ggcoef_reduced <- ggcoef$coef[ ggcoef$coef != 0]
    ggcoef_reduced[ sort(abs(ggcoef_reduced), index.return=TRUE, decreasing=TRUE)$ix ]
}
lmCoefIsolate <- function(xs, y) {
    return( coef( preflm <- lm(y ~ .*., xs) ))
}
enetCoefBootstrap <- function(xs, y, mod, lambda, reps=100, conf=.98) {
    coefNames = c()
    coefList = as.list(rep(0,reps) )
    ### get all the coefs of each boottrpa sample
    for (i in 1:reps) {
        samp <- sample(1:nrow(xs))
        #coefs <- enetCoefIsolate(xs[samp,], y, mod, lambda, toPrint=FALSE)
        coefs <- lmCoefIsolate(xs[samp,], y)
        coefList[[i]] <- coefs
        coefNames <- union( coefNames, names( coefs ) )
        #print(  names( coefs) )
    }
    mcoefs = matrix(0, nrow=reps, ncol=length(coefNames))
    colnames(mcoefs) <- coefNames
    ### get all the coefs into a matrix by col
    #print( coefList )
    #print( coefList[[1]] )
    #print( str( coefList[[1]] ))
    #print( coefList[[1]][1] )
    for (i in 1:reps) {
        for (j in 1:length(coefNames)) {
            n <- coefNames[j]
            if ( n %in% names( coefList[[i]] )  && ( length(coefList[[i]]) > 0 ) ) {
                #print( n )
                #print( coefList[[i]] )
                #print( names( coefList[[i]] ) )
                mcoefs[i, n] <- coefList[[i]][ n ]
            }
        }
        #print( c(i, coefList[[i]]  ) )
        #print( c(i, c(n, mcoefs[i,]) ) )
    }
    #print( mcoefs )
    ### calculate mean, min and max
    cutoff = as.integer( ( reps - reps * conf ) / 2 ) + 1
    #dfcoefs <- matrix(0, ncol=4, nrow=length(coefNames) )
    dfcoefs <- data.frame(f=rep('',length(coefNames)), v=rep(0,length(coefNames)), vmin=rep(0,length(coefNames)), vmax=rep(0,length(coefNames)) )
    dfcoefs[,1] <- names( apply(mcoefs, 2, sum) )
    dfcoefs[,2] <- apply(mcoefs, 2, mean)
    dfcoefs[,3] <- apply(mcoefs, 2, function(x) sort(x)[cutoff])
    dfcoefs[,4] <- apply(mcoefs, 2, function(x) sort(x)[length(x) - cutoff])
    return( dfcoefs )
}
enetCoefIsolate(preflrn, outlrn, model$finalModel, model$bestTune$lambda )
prefplot <- enetCoefBootstrap(preflrn, outlrn, model$finalModel, model$bestTune$lambda, conf=0.950 )
ggplot(prefplot, aes(x=f, y=v)) + geom_point() + geom_errorbar(aes(ymin=vmin, ymax=vmax))

library(randomForest)
library(inTrees)
#X <- iris[,-1]; target <- iris[,"Sepal.Length"] 
X <- preflrn; target <- outlrn
rf <- randomForest(X,target,importance=TRUE,ntree=10000) # random forest
ruleExec0 <- extractRules(RF2List(rf),X, ntree=4000, maxdepth=3) 
ruleExec <- unique(ruleExec0)
ruleMetric <- getRuleMetric(ruleExec,X,target) # regression rules
#ruleMetric
# transform regression rules to classification rules
target <- dicretizeVector(as.character(target)) # discretize it into three levels in default with equal frequency (the function also allows one to customize the number of levels to be discretized) 

# methods for classification rules can then be used for the conditions extracted from the regression trees
ruleMetric <- getRuleMetric(ruleExec,X,target)
ruleMetric <- pruneRule(ruleMetric,X,target) # prune each rule
# ruleMetric <- selectRuleRRF(ruleMetric,X,target) # rule selection
learner <- buildLearner(ruleMetric,X,target) #build the simplified tree ensemble learner
readableLearner <- presentRules(learner,colnames(X)) # present the rules with a more readable format
readableLearner
varImpPlot( rf , type=1)
