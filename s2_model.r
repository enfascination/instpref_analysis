#!/usr/bin/env Rscript
library(dplyr)
library(rjson)
settings <- fromJSON( file="settings.json")

prefs <- read.csv(file.path( settings$data, "s2/out.csv"))
prefs$out <- 1
colSums(prefs)

negRows = sample(1:nrow(prefs), nrow(prefs)/2)
prefs[negRows,] <- -prefs[negRows,]
summary(lm(out ~ ., prefs))
