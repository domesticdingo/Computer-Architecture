#!/usr/bin/env python3

"""Main."""

import sys
import os
from cpu import CPU

path = os.getcwd()
print(path)

with open('./ls8/examples/mult.ls8') as program:
    cpu = CPU()
    cpu.load(program)
    cpu.run()