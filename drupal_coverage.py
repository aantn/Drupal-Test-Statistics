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

# Define constants
CODE_EXTS = ["php", "inc", "module", "install"]	# which file extensions are included in the linecount

# Setup command line arguments
parser = argparse.ArgumentParser(description="Test statistics for Drupal Core Modules. This script checks out all of the drupal"
				+ "core modules and calculates each module's ratio of [lines of code] / [unit tests]")
#parser.add_argument("-c", "--checkout-dir", dest="checkout", default="modules", help="the directory where we'll checkout drupal modules")
args = parser.parse_args()

# Functions
def print_header ():
	"""Prints the titles of each output column"""
	# these are titles of each output column
	cols = ["Module", "Code lines", "Test lines", "Asserts", "Ratio * 100"]
	
	# take each title and pad it with whitespace (so that each column has a standard width)	
	outp = ""
	for col in cols:
		outp += col.ljust(10) + "\t"

	# print out the header
	print "-" * 80	
	print outp
	print "-" * 80

def download_core_modules ():
	"""Downloads all core drupal modules from CVS and returns a list of paths to each module"""
	# Download all core modules to ./drupal/modules/
	os.system("cvs -z6 -d:pserver:anonymous:anonymous@cvs.drupal.org:/cvs/drupal checkout -P drupal/modules")
	# Return the paths of each module
	FILTER = ["README.txt", "CVS"]
	return [os.path.abspath("drupal/modules/" + module)
		for module in os.listdir("drupal/modules")
		if module not in FILTER]

def calc_module_stats (module):
	"""
	Calculates and prints stats for one module.
	
	module: the module directory
	"""
	# setup stats for this module
	lines = 0
	test_lines = 0
	test_asserts = 0
	
	# get the module's name from it's path
	name = module.split("/")[-1]

	# loop over all files in the module
	for f in os.listdir(module):
		# get the file's extension
		ext = f.split(".")[-1]
		
		# get the file's full path
		path = os.path.join(module, f)
		
		# if the file is a test case
		if ext == "test":
			for line in open(path):
				test_lines += 1
				test_asserts += line.count("assert")
		# if the file is php code
		elif ext in CODE_EXTS:
			for line in open(path): lines += 1
	
	# print out stats for this module
	print "%s\t%10d\t%10d\t%10d\t%4f" % (name.ljust(10), lines, test_lines, test_asserts,
						float(test_asserts) / lines * 100)

# Main program
if __name__ == "__main__":
	modules = download_core_modules()
	print_header()
	for mod in modules:
		calc_module_stats(mod)	

