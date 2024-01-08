#!/bin/sh
# BART_base
    nohup python -u main.py train -mn bart -mv base -t SRL -bs 32 -uc True -ep 50 -nf 10 -tt SRL > logs/testing_verbose_with_prints_bart_base.out

# GRUT
    nohup python -u main.py train -mn bart -mv base -t SRL -bs 32 -uc True -ep 50 -nf 10 -tt SRL -gr half -map lmd > logs/testing_verbose_with_prints_grut.out

# GRUT_LU
    nohup python -u main.py train -mn bart -mv base -t SRL -bs 32 -uc True -ep 50 -nf 10 -tt SRL -gr half -map lmd -alut True > logs/testing_verbose_with_prints_grut_lu.out
