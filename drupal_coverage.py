#!/usr/bin/env python

# Drupal Test Statistics - Writen as part of Google Code-In
# Copyright (C) 2010 Natan Yellin <aantny@gmail.com> (http://natanyellin.com)
# 
# This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.
#
# TODO:
#	* Count lines of code in subdirectories (right now we don't properly line-count the "field" module)
# 	* Allow using an existing checkout (using the partially implemented -c argument)

import os
import argparse

parser = argparse.ArgumentParser(description="Test statistics for Drupal Core Modules. This script checks out" +
				" all of the drupal core modules and calculates each module's ratio of [lines of code]" +
				" / [unit tests]")

# add an argument to use an existing drupal checkout
#parser.add_argument("-c", "--checkout-dir", dest="checkout", default="modules",
#	help="the directory where we'll checkout drupal modules")
args = parser.parse_args()

# The following file extensions are included in the linecount
exts = ["php", "inc", "module", "install"]

# Download all drupal core modules from CVS
os.system("cvs -z6 -d:pserver:anonymous:anonymous@cvs.drupal.org:/cvs/drupal checkout -P drupal/modules")

# Get a list of all modules
modules = os.listdir("drupal/modules")
for r in ["README.txt", "CVS"]:
	modules.remove(r)
 
# Loop over modules
print_header()
for mod in modules:
	# setup stats for this module
	lines = 0
	test_lines = 0
	test_asserts = 0
	
	# loop over all files in the module
	for f in files = os.listdir("drupal/modules/" + mod):
		# get the file extension and check code type
		ext = f.split(".")[-1]
		if ext == "test":	# this is test code
			for line in open("drupal/modules/" + mod + "/" + f):
				test_lines += 1
				test_asserts += line.count("assert")
		elif ext in exts:	# this is the module's php code
			for line in open("drupal/modules/" + mod + "/" + f): lines += 1
	# print out stats for this module
	print "%s\t%10d\t%10d\t%10d\t%4f" % (mod.ljust(10), lines, test_lines, test_asserts, float(test_asserts) / lines * 100)

def print_header ():
	"""Prints the titles of each output column"""
	print "-" * 80
	print "%s\t%s\t%s\t%s\t%s" %	("Module".ljust(10), "Code lines".ljust(10), "Test lines".ljust(10),
					 "Asserts".ljust(10), "Ratio * 100".ljust(10))
	print "-" * 80

