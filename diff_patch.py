import os
import sys


# Environment

file_before = sys.argv[1]
file_after = sys.argv[2]
file_target = sys.argv[3]

assert os.path.exists(file_before)
assert os.path.exists(file_after)
assert os.path.exists(file_target)

keep_original = True  # create a copy of the original file before patching
create_patch = True  # create a patch file
