import string, io, sys, binascii, os
from time import gmtime, strftime

"""
USAGE
   You need to have previously created a drive image of your DVR and stored it on a different
   harddrive somewhere. Enter the path to the image below. Will take 10+ hours to run on 160GB drive
"""

"""
USER-DEFINED VARIABLES
   target_dir     -  Directory to dump a file names 1.mpg and 2.mpg, before and after split_byte
   split_file     -  Path and filename to the file you want to split
   split_byte     -  Size in bytes you want to divide the split_file (Google makes an excellent unit
                     calculator. For example, search "250000 KB to bytes")
"""

target_dir="C:\\work\\out\\"
split_file="C:\\work\\749.mpg"
split_byte=0

def main(split_file, split_byte, target_dir):
   """
   Execution enters here, controls master loop over data
   """
   # init screen
   print ""
   print "Pioneer Extractor (633H)"
   print "Mike Knoop, 2011, knoopgroup.com"
   print ""

   src = io.open(split_file, 'rb')
   src.seek(0)
   file_1 = src.read(split_byte)
   src.seek(split_byte)
   file_2 = src.read()

   f1 = io.open(build_target(target_dir, "1"), 'wb')
   f2 = io.open(build_target(target_dir, "2"), 'wb')

   f1.write(file_1)
   f2.write(file_2)

   f1.close()
   f2.close()

   print "done!"

def build_target(dir, filename):
   lst = []
   lst.append(dir)
   lst.append(filename)
   lst.append('.mpg')
   loc = string.join(lst, '')
   return loc

main(split_file, split_byte, target_dir)