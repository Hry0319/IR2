#!/bin/bash
# Put your command below to execute your program.
# Replace "./my-program" with the command that can execute your program.
# Remember to preserve " $@" at the end, which will be the program options we give you.

. pypy-env/bin/activate

pypy naivebayes.py $@

deactivate
