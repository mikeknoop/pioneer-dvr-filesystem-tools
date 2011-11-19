import string, io, sys, binascii, os
from time import gmtime, strftime

"""
USAGE
   You need to have previously created a drive image of your DVR and stored it on a different
   harddrive somewhere. Enter the path to the image below. Will take 10+ hours to run on 160GB drive
"""

"""
USER-DEFINED VARIABLES
   src_loc        -  Path and filename to an image file which is the raw contents of the drive.
                     Use a tool such as UFS Explorer Standard Recovery to backup the drive to an image
   target_dir     -  Directory in which to output each sequential movie-block
"""
src_loc="E:\\work\\drive\\pioneer.img"
target_dir="E:\\work\\out\\"

"""
DETAILS HOW IT WORKS
This is a script designed to extract raw video/audio data off
of a Pioneer DVR-633H device. The 633H frequently corrupts the
boot portion of the drive, rendering the device inoperable.
Fortunately, the data is often intact and recoverable. The 633H
appears to store all video/audio data in 2KB streaming mpeg chunks.
They are stored (convienently) sequentially on the disk. Each block
of mpeg media is prefixed with the following magic hex string
(mpeg identifer): 000001ba

Additionally, this sequence occurs reguarly every 2KB of data.
In other words, the 633H stores all it's content in 2KB mpeg
streaming chunks which can simply be concatenated to form the
full original media stream.

For whatever reason, the 633H sometimes stores "useless" chunks
with the mpeg identifier which are larger than 2KB. Inside these
larger chunks, many refernces to the magix hex string can be found
but the sizes are not 2KB and we defined them as corrupted/useless.

This data should not be used. If it is included in the final 
mpeg compilatoin, playback may end when that piece of video 
is reached.

We take the following strategy:
   1. Starting at sector 0
   2. Loop io stream over all sectors until first occurence
      of magic hex string is found
   3. Continue iterating forward until next magic hex string
      is found. Substract the location of second from first 
      to get a raw chunk size
   4. If chunk size != 2KB, discard it and go to (2)
   5. If chunk == 2KB, write it output stream
   6. Loop (2) through (5) until end of io stream

Additionally, we look for the new_file_hex string in each chunk. If it
exists, write to a new outpul file. This may not be perfect (some video
tracks skip around) but gives you a manageable amount of output videos
to concatenate together using simple video editing software (VirtualDub)

"""

magic_hex="000001ba"
new_file_hex="50494f4e454552"
new_file_counter=0
starting_stream_loc=0
ending_stream_loc=0
chunk_size=2048

def main(src_loc, target_dir, magic_hex, new_file_hex, new_file_counter, starting_stream_loc, ending_stream_loc, chunk_size):
   """
   Execution enters here, controls master loop over data
   """
   # init screen
   print ""
   print "Pioneer Extractor (633H)"
   print "Mike Knoop, 2011, knoopgroup.com"
   print ""

   print "the current time is",
   print strftime("%Y-%m-%d %H:%M:%S", gmtime())
   print ""

   # open files
   print "opening source and initial target...",
   src = io.open(src_loc, 'rb')
   target = io.open(build_target(target_dir, `new_file_counter`), 'wb')
   print "done!\n"

   # master loop
   end_of_stream = False
   is_new_file = False
   new_extra_check_last = False
   bad_chunk_count = 0
   bad_chunk_size = 0
   i = 0
   info = os.stat(src_loc)
   src_size = info.st_size
   target_size = 0
   print "total source size:",
   print src_size,
   print "bytes"
   print "processing data..."
   try:
      # find first instance
      loc = find_string(src, magic_hex, starting_stream_loc)
      last_loc = loc
      while (not end_of_stream):
         # find next instance
         loc_search_start = last_loc + (len(magic_hex) / 2)
         new_loc = find_string(src, magic_hex, loc_search_start)
         if (not new_loc):
            end_of_stream = True
            break
         # calculate byte size of chunk
         size = new_loc - last_loc
         if (size == chunk_size):
            # check if new file first
            is_new_file = False
            is_new_file_2 = False
            is_new_file = find_string(src, new_file_hex, last_loc, chunk_size, chunk_size-100, new_loc)
            if is_new_file:
               # perform a secondary check                
               src.seek(is_new_file-29)
               p = src.read(2)
               new_extra_check = binascii.hexlify(p)
               if (new_extra_check != "0000") and (new_extra_check_last != new_extra_check) and new_extra_check_last:
                  new_file_counter = new_file_counter + 1
                  target.close()
                  target = io.open(build_target(target_dir, `new_file_counter`), 'wb')
               new_extra_check_last = new_extra_check
            src.seek(last_loc)
            tmp = src.read(chunk_size)
            target.write(tmp)
            target_size = target_size + chunk_size
            i = i + 1
            if (i % 100000 == 0):
               print target_size,
               print "bytes"
         else:
            bad_chunk_count = bad_chunk_count + 1
            bad_chunk_size = bad_chunk_size + size
            #sys.stdout.write("*")
         # else the chunk is bad mpeg data. discard it
         # prepare for next iert
         last_loc = new_loc
         if (ending_stream_loc != 0):
            if (new_loc > ending_stream_loc):
               end_of_stream = True
               print "ending because ending_stream_loc was reached."
               break
   except Exception as e:
      print "exception:",
      print e
   print "success!\n"
   print "extracted",
   print i,
   print "files."
   print "found",
   print bad_chunk_count,
   print "bad chunks with total size",
   print bad_chunk_size,
   print "bytes\n"

   # clean up
   print "cleaning up...",
   target.close()
   src.close()

   # exit
   print "clean exit.\n"
   print "the current time is",
   print strftime("%Y-%m-%d %H:%M:%S", gmtime())
   print ""
   sys.exit()

def build_target(dir, filename):
   lst = []
   lst.append(dir)
   lst.append('0')
   lst.append(filename)
   lst.append('.mpg')
   loc = string.join(lst, '')
   return loc

def find_string(src, val, start, buffer=2500, inc_buffer=2000, max_i=0):
   """
   Given io source (src), str (val), starting byte offset (start),
   incremental search size (buffer),
   Return a byte offset where first occurence of val is found
   else false
   """
   found = False
   end_of_stream = False
   i = start
   count = 0
   while (not found and not end_of_stream):
      src.seek(i)
      tmp = src.read(buffer)
      if (len(tmp) == 0):
         end_of_stream = True
         break
      tmp = binascii.hexlify(tmp)
      if (val in tmp):
         # div by two since hexlify makes string twice as long
         idx = tmp.find(val) / 2
         found = True
         break
      if max_i != 0:
         if i > max_i:
            end_of_stream = True
            break
      i = i + inc_buffer
      count = count + 1
   if (end_of_stream):
      return False
   if (found):
      return i + idx

main(src_loc, target_dir, magic_hex, new_file_hex, new_file_counter, starting_stream_loc, ending_stream_loc, chunk_size)