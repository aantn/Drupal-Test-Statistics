#!/usr/bin/env python

# Drupal Test Statistics - Writen as part of Google Code-In
# Copyright (C) 2010 Natan Yellin <aantny@gmail.com> (http://natanyellin.com)
# 
# This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

import os
import sys
import urllib

from xml.dom import minidom

try:
	import argparse
except ImportError:
	print "You're running an older version of Python that doesn't include the argparse module. You install it manually by running 'sudo easy_install argparse'"
	sys.exit()

# Define constants and global variables
DOWNLOAD_DIR = "stats_checkout/"		# root dir where we download core and contrib modules
CONTRIB_DIR = DOWNLOAD_DIR + "contrib/"		# dir for contrib modules
CODE_EXTS = ["php", "inc", "module", "install"]	# file extensions to be included in the linecount
OUTPUT_SEP = "-" * 100				# string used to separate between different sections of output
best_ratio = 0					# the best ratio out of all the modules 
best_module = ""				# name of module with the best ratio
sum_ratios = 0					# sum of all ratios
num_ratios = 0					# num of non-zero ratios
testless_modules = []				# list of modules with no tests at all

# lastly, include a list of the top 49 most popular drupal modules (in order of popularity)
TOP_MODULES = ['modules/views', 'modules/cck', 'modules/token', 'modules/pathauto', 'modules/filefield', 'modules/admin_menu', 'modules/imageapi', 'modules/imagefield', 'modules/imagecache', 'modules/date', 'modules/imce', 'modules/google_analytics', 'modules/wysiwyg', 'modules/webform', 'modules/advanced_help', 'modules/poormanscron', 'modules/captcha', 'modules/image', 'modules/jquery_ui', 'modules/ctools', 'modules/lightbox2', 'modules/nodewords', 'modules/link', 'modules/backup_migrate', 'modules/jquery_update', 'modules/devel', 'modules/xmlsitemap', 'modules/fckeditor', 'modules/panels', 'modules/globalredirect', 'modules/calendar', 'modules/page_title', 'themes/zen', 'modules/imce_wysiwyg', 'modules/transliteration', 'modules/votingapi', 'modules/ckeditor', 'modules/views_slideshow', 'modules/print', 'modules/nice_menus', 'modules/tagadelic', 'modules/email', 'modules/logintoboggan', 'modules/contemplate', 'modules/site_map', 'modules/path_redirect', 'modules/emfield', 'modules/i18n']

# Setup command line arguments
parser = argparse.ArgumentParser(description="Test statistics for Drupal Core Modules. This script checks out all of the drupal"
				+ "core modules and calculates each module's ratio of [lines of code] / [unit tests]")
parser.add_argument("-l", "--local-module", dest="local_module", default=None, help="the directory of a custom local module to include in the stats count")
parser.add_argument("-c", "--contrib-module", dest="contrib_module", default=None, help="the name of a custom contrib module to download and include in the stats count")
args = parser.parse_args()

# Functions
def get_cvs_tag (module, drupal_version):
	"""
	Parses drupal.org's xml feeds to find a module's cvs tag for the latest release.
	
	module: the module's name (e.g. "views")
	drupal_version: "7.x" or "6.x"
	
	returns the tag or None, if there is no release for the given drupal version
	"""
	# Parse the module's XML feed to find the main development tag
	feed = urllib.urlopen("http://updates.drupal.org/release-history/%s/%s" % (module, drupal_version))
	doc = minidom.parse(feed)
	tags = doc.getElementsByTagName("tag")
	if len(tags) == 0:
		return None
	tag = tags[0].toxml()[5:-6]	# there may be more than one tag - we take the most recent
	return tag

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
	# Get the module name (right now we have something like "modules/x" or "themes/x")
	name = module.split("/")[-1]
	
	# Get the module's tag
	tag = get_cvs_tag(name, "7.x")
	if tag is None:
		tag = get_cvs_tag(name, "6.x")

	# Download the module to ./DOWNLOAD_DIR/contrib
	dest = CONTRIB_DIR + module + "/"
	os.system("cvs -z6 -d:pserver:anonymous:anonymous@cvs.drupal.org:/cvs/drupal-contrib checkout -P " +
		"-r %s -d %s contributions/%s/" % (tag, dest, module))
	
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
	outp += cols[0].ljust(17) + "\t"
	for col in cols[1:]:
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
	for root, subdirs, files in os.walk(module):
		for f in files:
			# get the file's extension
			ext = f.split(".")[-1]
		
			# get the file's full path
			path = os.path.join(root, f)
			
			# if the file is a test case (or if it's regular code under the tests/ directory)
			if ext == "test" or (ext in CODE_EXTS and root.count("tests") > 0):
				for line in open(path):
					test_lines += 1
					test_asserts += line.count("assert")
			
			# if the file is php code
			elif ext in CODE_EXTS:
				for line in open(path): lines += 1
	
	# calculate the ratio
	if lines != 0:
		ratio = float(test_asserts) / lines * 100
	else:
		ratio = 0
		#print "WARNING: 0 lines were found for the %s module" % (name,)

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
	print "\t%s\t%10d\t%10d\t%10d\t%f%%" % (name.ljust(17), lines, test_lines, test_asserts,
						ratio)

def print_overall_stats ():
	print OUTPUT_SEP
	print "Overall Stats:"
	print "\tAverage ratio: %f%%" % (sum_ratios / num_ratios)
	print "\tBest ratio: %f%% (%s module)" % (best_ratio, best_module)
	print "\tThe following %d modules have no tests at all: %s" % (len(testless_modules), ", ".join(testless_modules))

# Main program
if __name__ == "__main__":
	# Create the download dirs for contrib modules
	try:
		os.makedirs(CONTRIB_DIR + "modules")
		os.makedirs(CONTRIB_DIR + "themes")
	except OSError:	# if the directories already exist
		pass

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
	
