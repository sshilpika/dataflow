"""
A -> B map microbenchmark.

Reads FILESIZE/24 double vectors per record. This is more memory efficient than reading one vector per record.

Requires NumPy (http://www.numpy.org/).
"""

from __future__ import print_function
import sys
import numpy as np
from pyspark import SparkContext
from glob import glob

def parseVectors(arr):
    arr= np.fromstring(arr,dtype=np.float64)
    arr.reshape(arr.shape[0]/3,3)
    return arr

def add_vec3(arr,vec):
    for v in arr:
        v[0] += vec[0]
        v[1] += vec[1]
        v[2] += vec[2]
    return arr

def construct_apply_shift(shift):
    return lambda p: add_vec3(p,shift)
        
def savebin(iterator):
    basedir='/tmp'  #'/mnt'
    idx=len(glob(basedir+'/binary_output*.bin'))
    outfilename=basedir+"/binary_output-"+str(idx).zfill(2)+".bin"
    outfile=open(outfilename,'w')
    for x in iterator:
        outfile.write(x.data)

if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: simple_map <file>", file=sys.stderr)
        exit(-1)

    sc = SparkContext(appName="SimpleMap")

    rdd = sc.binaryFiles(sys.argv[1])
    A = rdd.map(parseVectors)
    print("numPartitions(%d,%s): %d"%(A.id(),A.name(),A.getNumPartitions()))

    shift=np.array([25.25,-12.125,6.333],dtype=np.float64)
    B = A.map(construct_apply_shift(shift))
    print("numPartitions(%d,%s): %d"%(B.id(),B.name(),B.getNumPartitions()))
    B.foreachPartition(savebin)

    sc.stop()
