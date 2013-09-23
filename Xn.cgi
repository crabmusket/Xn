#!/usr/bin/python

import os
os.environ['PYTHON_EGG_CACHE'] = '/temp/dbuc6168'

# Essential modules
import cgi
import sys

# Xn module
import Xn

# Generation parameters
XNAME = "x"
YNAME = "y"
ZNAME = "z"
SEEDNAME = "seed"
DENSITYNAME = "density"
OFFSETNAME = "offset"
SPARSITYNAME = "sparsity"
OUTPUTNAME = "output"

print 'Content-type: text/plain\r\n'

fields = cgi.FieldStorage()

if fields.has_key(XNAME):
	Xn.WIDTH = int(fields[XNAME].value)
if fields.has_key(YNAME):
	Xn.LENGTH = int(fields[YNAME].value)
if fields.has_key(ZNAME):
	Xn.LEVELS = int(fields[ZNAME].value)
if fields.has_key(SEEDNAME):
	Xn.SEED = int(fields[SEEDNAME].value)
if fields.has_key(DENSITYNAME):
	Xn.DENSITY = fields[DENSITYNAME].value
if fields.has_key(OFFSETNAME):
	Xn.OFFSET = fields[OFFSETNAME].value
if fields.has_key(SPARSITYNAME):
	Xn.SPARSITY = int(fields[SPARSITYNAME].value)

try:
	a = Xn.generate()
except:
	print sys.exc_info()[0]

if fields.has_key(OUTPUTNAME) and fields[OUTPUTNAME].value == "ASCII":
	print a.render()
else:
	print a.list()
