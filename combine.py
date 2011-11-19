import string, io, sys, binascii, os
from time import gmtime, strftime


"""
USAGE
   Use this script to combine raw files together. It will give you a simple command
   prompt when run to enter filenames seperated by commas. ".mpg" is automatically
   appended to each filename.
   Example input: "543,547,591"
   Each file will be appended to the end of 543.mpg and then deleted. The result is the
   files combined and called 543.mpg
"""

"""
USER-DEFINED VARIABLES
   work_dir       -  The directory in which files are looked for and combined within
"""
work_dir="E:\\work\\out\\"

def main(work_dir):
   """
   Asks for a comma-seperated list of filenames to combine. Combines them then puts the
   resulting concatenation in the work_dir under the first filename
   """
   # init screen
   print ""
   print "Pioneer Extractor (633H)"
   print "Mike Knoop, 2011, knoopgroup.com"
   print ""
   print "combining files in",
   print work_dir
   print ""
   print "give a list of comma-seperated filenames to combine (or type quit)"
   print ".mpg will be automatically appended to each filename. do not include it"
   print ""
   inp = None
   while True:
      inp = raw_input(">")
      if inp == "quit":
         break
      print "working...",
      inp.replace(' ', '')
      inp_list = inp.split(',')
      target_loc = build_loc(work_dir, inp_list[0])
      if not os.path.isfile(target_loc):
         print "first filename must exist."
         print ""
         continue
      target = io.open(target_loc, 'ab')
      i = 0
      for filename in inp_list:
         if i == 0:
            # skip first file since we append to it
            i = i + 1
            continue
         src_loc = build_loc(work_dir, filename)
         if os.path.isfile(src_loc):
            src = io.open(src_loc, 'rb')
            target.write(src.read())
            src.close()
            os.remove(src_loc)
            i = i + 1
            sys.stdout.write(`filename`)
            sys.stdout.write(" ")
         else:
            sys.stdout.write("*")
            sys.stdout.write(" ")
      target.close()
      if i == 0:
         # no files written to ouput file, delete it
         os.remove(target_loc)
         print ""
         print "no files were combined.",
         print ""
         print ""
      else:
         info = os.stat(target_loc)
         target_size = info.st_size
         print ""
         print "success! combined",
         print i,
         print "files to create",
         print target_loc
         print target_size,
         print "bytes",
         print ""
         print ""
   print "now exiting."
   sys.exit()

def build_loc(dir, filename):
   lst = []
   lst.append(dir)
   lst.append(filename)
   lst.append('.mpg')
   loc = string.join(lst, '')
   return loc

main(work_dir)