#!/usr/bin/env Rscript
library(dplyr)
library(rjson)
settings <- fromJSON( file="settings.json")

prefs <- read.csv(file.path( settings$data, "s2/out.csv"))
prefs$out <- 1
RTadj = diff( (prefs %>% 
              group_by(block) %>% 
              summarize(median=median(gameRT))
          )$median)/2
prefs$gameRTctl <- ifelse(prefs$block == 0, prefs$gameRT - RTadj, prefs$gameRT + RTadj) 
colSums(prefs)
apply(prefs, 2,FUN=table)

## predict speed of choice
#summary(lm(outRT ~ . - expdGameO - out - gameRT - gameRTctl, prefs))
## predict choice
negRows = sample(1:nrow(prefs), nrow(prefs)/2)
prefs[negRows,] <- -prefs[negRows,]
summary(lm(out ~ . - expdGameO - block - outRT - gameRT - expdGameF, prefs))
