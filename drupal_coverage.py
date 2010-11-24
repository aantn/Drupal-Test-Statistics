#!/usr/bin/env python

# Drupal Test Statistics - Writen as part of Google Code-In
# Copyright (C) 2010 Natan Yellin <aantny@gmail.com> (http://natanyellin.com)
# 
# This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.
#
# TODO:
#	* Count lines of code in subdirectories (right now we don't properly line-count the "field" module)

import os
import argparse

# Define constants and global variables
DOWNLOAD_DIR = "stats_checkout/"		# dir where we download core and contrib modules
CODE_EXTS = ["php", "inc", "module", "install"]	# file extensions to be included in the linecount
OUTPUT_SEP = "-" * 100				# string used to separate between different sections of output
best_ratio = 0					# the best ratio out of all the modules 
best_module = ""				# name of module with the best ratio
sum_ratios = 0					# sum of all ratios
num_ratios = 0					# num of non-zero ratios
testless_modules = []				# list of modules with no tests at all

# lastly, include a list of the top 49 most popular drupal modules (in order of popularity)
TOP_MODULES = ['views', 'cck', 'token', 'pathauto', 'filefield', 'admin_menu', 'imageapi', 'imagefield', 'imagecache', 'date', 'imce', 'google_analytics', 'wysiwyg', 'webform', 'advanced_help', 'poormanscron', 'captcha', 'image', 'jquery_ui', 'ctools', 'lightbox2', 'nodewords', 'link', 'backup_migrate', 'jquery_update', 'devel', 'xmlsitemap', 'fckeditor', 'panels', 'globalredirect', 'calendar', 'page_title', 'zen', 'imce_wysiwyg', 'transliteration', 'votingapi', 'ckeditor', 'views_slideshow', 'print', 'nice_menus', 'tagadelic', 'email', 'logintoboggan', 'contemplate', 'rules', 'site_map', 'path_redirect', 'emfield', 'i18n']


# Setup command line arguments
parser = argparse.ArgumentParser(description="Test statistics for Drupal Core Modules. This script checks out all of the drupal"
				+ "core modules and calculates each module's ratio of [lines of code] / [unit tests]")
parser.add_argument("-l", "--local-module", dest="local_module", default=None, help="the directory of a custom local module to include in the stats count")
parser.add_argument("-c", "--contrib-module", dest="contrib_module", default=None, help="the name of a custom contrib module to download and include in the stats count")
args = parser.parse_args()

# Functions
def download_core_modules ():
	"""Downloads all core drupal modules from CVS and returns a list of paths to each module"""
	# Download all core modules to ./DOWNLOAD_DIR/core/
	dest = DOWNLOAD_DIR + "core/"
	os.system("cvs -z6 -d:pserver:anonymous:anonymous@cvs.drupal.org:/cvs/drupal checkout -P -d %s drupal/modules" % (dest,))
	
	# Return the paths of each module
	FILTER = ["README.txt", "CVS"]
	return [os.path.abspath(dest + module)
		for module in os.listdir(dest)
		if module not in FILTER]

def download_contrib_module (module):
	"""Takes the name of a community module, downloads it, and returns the path"""
	# Download the module to ./DOWNLOAD_DIR/contrib
	dest = DOWNLOAD_DIR + "contrib/" + module + "/"
	os.system("cvs -z6 -d:pserver:anonymous:anonymous@cvs.drupal.org:/cvs/drupal-contrib checkout -P -d %s contributions/modules/%s/" % (dest, module))
	
	# Return the path of the downloaded module
	return os.path.abspath(dest)

def download_top_modules ():
	"""Downloades the top 50 community modules and returns a list of paths to each module"""
	return [download_contrib_module(mod) for mod in TOP_MODULES]		

def print_header ():
	"""Prints the titles of each output column"""
	# these are titles of each output column
	cols = ["Module", "Code lines", "Test lines", "Asserts", "Ratio (%)"]
	
	# take each title and pad it with whitespace (so that each column has a standard width)	
	outp = "\t"
	for col in cols:
		outp += col.ljust(10) + "\t"

	# print out the header
	print OUTPUT_SEP
	print outp
	print OUTPUT_SEP

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
	ratio = float(test_asserts) / lines * 100

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
	print "\t%s\t%10d\t%10d\t%10d\t%f%%" % (name.ljust(10), lines, test_lines, test_asserts,
						ratio)

def print_overall_stats ():
	print OUTPUT_SEP
	print "Overall Stats:"
	print "\tAverage ratio: %f%%" % (sum_ratios / num_ratios)
	print "\tBest ratio: %f%% (%s module)" % (best_ratio, best_module)
	print "\tThe following %d modules have no tests at all: %s" % (len(testless_modules), ", ".join(testless_modules))

# Main program
if __name__ == "__main__":
	# Download all core and top modules and get their paths
	core_modules = download_core_modules()
	top_modules = download_top_modules()

	# Do the same for the custom module
	if args.contrib_module is not None:
		custom_contrib = download_contrib_module(args.contrib_module)

	# Print the header row
	print_header()
	
	# Print stats for all core and top modules
	print "Core Modules:"
	for mod in core_modules:
		print_module_stats(mod)	
	print "Top Modules (sorted by popularity):"
	for mod in top_modules:
		print_module_stats(mod)

	# If the user wants, print stats for a custom modules
	print "Custom Modules:"
	if args.local_module is not None:
		print_module_stats(os.path.abspath(args.local_module))
	if args.contrib_module is not None:
		print_module_stats(custom_contrib)
	if not args.local_module and not args.contrib_module:
		print "\t(None)"

	# Print out the best and average ratios
	print_overall_stats ()
	
