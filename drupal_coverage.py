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

# Define constants and global variables
CODE_EXTS = ["php", "inc", "module", "install"]	# file extensions to be included in the linecount
OUTPUT_SEP = "-" * 100				# string used to separate between different sections of output
best_ratio = 0					# the best ratio out of all the modules 
best_module = ""				# name of module with the best ratio
sum_ratios = 0					# sum of all ratios
num_ratios = 0					# num of non-zero ratios
testless_modules = []				# list of modules with no tests at all

# Setup command line arguments
parser = argparse.ArgumentParser(description="Test statistics for Drupal Core Modules. This script checks out all of the drupal"
				+ "core modules and calculates each module's ratio of [lines of code] / [unit tests]")
#parser.add_argument("-c", "--checkout-dir", dest="checkout", default="modules", help="the directory where we'll checkout drupal modules")
parser.add_argument("-c", "--custom-module", dest="custom_module", default=None, help="the directory of a custom module to include in the stats count")
args = parser.parse_args()

# Functions
def download_core_modules ():
	"""Downloads all core drupal modules from CVS and returns a list of paths to each module"""
	# Download all core modules to ./drupal/modules/
	os.system("cvs -z6 -d:pserver:anonymous:anonymous@cvs.drupal.org:/cvs/drupal checkout -P drupal/modules")
	
	# Return the paths of each module
	FILTER = ["README.txt", "CVS"]
	return [os.path.abspath("drupal/modules/" + module)
		for module in os.listdir("drupal/modules")
		if module not in FILTER]

def print_header (name):
	"""
	Prints the titles of each output column
	
	name: the name of this group of modules	
	"""
	# these are titles of each output column
	cols = ["Module", "Code lines", "Test lines", "Asserts", "Ratio * 100"]
	
	# take each title and pad it with whitespace (so that each column has a standard width)	
	outp = "\t"
	for col in cols:
		outp += col.ljust(10) + "\t"

	# print out the header
	print OUTPUT_SEP
	print outp
	print OUTPUT_SEP
	print name

def print_module_stats (module):
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
	
	# calculate the ratio
	ratio = float(test_asserts) / lines

	# calculate global stats
	global sum_ratios, num_ratios, best_ratio, best_module
	if ratio == 0:
		testless_modules.append(name)
	else:
		sum_ratios += ratio
		num_ratios += 1
		
		if ratio > best_ratio:
			best_ratio = ratio
			best_module = name

	# print out stats for this module
	print "\t%s\t%10d\t%10d\t%10d\t%4f" % (name.ljust(10), lines, test_lines, test_asserts,
						ratio * 100)

# Main program
if __name__ == "__main__":
	# Download all core modules and get their paths
	modules = download_core_modules()
	
	# Print the header row
	print_header("Core Modules:")
	
	# Print stats for all core modules
	for mod in modules:
		print_module_stats(mod)	
	
	# If the user wants, print stats for a custom module
	if args.custom_module is not None:
		print "Custom Modules:"
		print_module_stats(os.path.abspath(args.custom_module))
	
	# Print out the best and average ratios
	print OUTPUT_SEP
	print "Overall Stats:"
	print "\tAverage ratio: %f" % (sum_ratios / num_ratios)
	print "\tBest ratio: %f (%s module)" % (best_ratio, best_module)
	print "\tThe following %d modules have no tests at all: %s" % (len(testless_modules), ", ".join(testless_modules))

