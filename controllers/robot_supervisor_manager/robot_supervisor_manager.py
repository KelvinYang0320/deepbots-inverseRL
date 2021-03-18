"""
More runners for RL algorithms can be added here.
"""
import DDPG_runner
import os

path = "./tmp"
try:
    os.mkdir(path)
except OSError:
    print ("Creation of the directory %s failed" % path)
else:
    print ("Successfully created the directory %s " % path)

path = "./tmp/ddpg"
try:
    os.mkdir(path)
except OSError:
    print ("Creation of the directory %s failed" % path)
else:
    print ("Successfully created the directory %s " % path)
DDPG_runner.run()