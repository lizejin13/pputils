#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 gmsh2slf.py                           # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: June 26, 2015
#
# Purpose: Script takes the file generated by gmsh mesh generator, and 
# converts them to the SELAFIN mesh format; THE IPOBO ARRAY IS NOT
# PROPERLY SET. DOES NOT WORK! DO NOT USE!
#
# Uses: Python2.7.9, Matplotlib v1.4.2, Numpy v1.8.2
#
# Example:
#
# python gmsh2slf.py -i out.msh -o out.slf
# where:
# -i input *.msh file generated by gmsh
# -o output *.slf output mesh file in SELAFIN format
# 
# note: boundary nodes are written, but may not be CCW
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys                              # system parameters
import matplotlib.tri    as mtri           # matplotlib triangulations
import numpy             as np             # numpy
import math                                # for the ceil function
from parsers.parserSELAFIN import SELAFIN 
curdir = os.getcwd()
#
#
# I/O
if len(sys.argv) != 5 :
	print 'Wrong number of Arguments, stopping now...'
	print 'Usage:'
	print 'python gmsh2slf.py -i out.msh -o out.slf'
	sys.exit()
dummy1 =  sys.argv[1]
gmsh_file = sys.argv[2]
dummy2 =  sys.argv[3]
slf_file = sys.argv[4]

# to create the output file
#fout = open(adcirc_file,"w")

# to read the entire *.msh file as string (and clip of the stuff that is
# not needed
# each line in the file is a list object
line = list()
with open(gmsh_file, "r") as f1:
	for i in f1:
		line.append(i)
		
# to write to a temp file nodes and 2d elements only
temp_nodes_file ="temp_nodes"
temp_elements_file ="temp_elements"
temp_boundaries_file = "temp_boundaries_file"

fout_nodes = open(temp_nodes_file,"w")
fout_elements = open(temp_elements_file,"w")
fout_boundaries = open(temp_boundaries_file,"w")

# read how many nodes in the file (it is in *.gmsh file as line 5)
n = line[4] # it is a string
n = int(n)  # now it becomes an integer

# read the next n lines (this is the nodes file)
for i in range(5,5+n):
	fout_nodes.write(line[i])
	
# the next two lines are 
# $EndNodes 
# $Elements

# then number of elements
e = line[5+n+2]
e = int(e)

for i in range(5+n+3,5+n+3+e):
	# write only the boundary elements (i.e., if there are 6 blanks)
	if(line[i].count(' ') == 6):
		fout_boundaries.write(line[i])	
	
	# write only the 2d elements (i.e., if there are 7 blanks)
	if(line[i].count(' ') == 7):
		fout_elements.write(line[i])
		
fout_nodes.close()
fout_elements.close()
fout_boundaries.close()

# now open the nodes and elements files using numpy arrays

# use numpy to read the file
# each column in the file is a row in data read by no.loadtxt method
nodes_data = np.genfromtxt(temp_nodes_file,unpack=True)
elements_data = np.genfromtxt(temp_elements_file,unpack=True)
boundaries_data = np.genfromtxt(temp_boundaries_file,unpack=True)

# nodes 
node_id = nodes_data[0,:]
node_id = node_id.astype(np.int16)
node_id = np.subtract(node_id, 1)
x = nodes_data[1,:]
y = nodes_data[2,:]
z = nodes_data[3,:]

n = len(node_id)

# elements
e1 = elements_data[5,:]
e1 = e1.astype(np.int16)
e1 = np.subtract(e1, 1)
e2 = elements_data[6,:]
e2 = e2.astype(np.int16)
e2 = np.subtract(e2, 1)
e3 = elements_data[7,:]
e3 = e3.astype(np.int16)
e3 = np.subtract(e3, 1)

e = len(e1)

# stack the elements
ikle = np.column_stack((e1,e2,e3))  
ikle = ikle.astype(np.int16)

# boundaries
b1 = boundaries_data[5,:]
b1 = b1.astype(np.int16)
b2 = boundaries_data[6,:]
b2 = b2.astype(np.int16)

# stack these horizontally
b_stk = np.hstack((b1,b2))

# get only the unique elements
b = np.unique(b_stk)

b = np.subtract(b, 1)

# to create the output file
#fout = open("junk.out","w")

#for i in range(len(b)):
#	fout.write(str(b[i]) + '\n')

# now we can delete the temp file
os.remove(temp_nodes_file)
os.remove(temp_elements_file)
os.remove(temp_boundaries_file)

# now to write the SELAFIN mesh file
slf2d = SELAFIN('')

#print '     +> Set SELAFIN variables'
slf2d.TITLE = 'Converted from gmsh'
slf2d.NBV1 = 1 
slf2d.NVAR = 1
slf2d.VARINDEX = range(slf2d.NVAR)
slf2d.VARNAMES.append('BOTTOM          ')
slf2d.VARUNITS.append('M               ')

#print '     +> Set SELAFIN sizes'
slf2d.NPLAN = 1
slf2d.NDP2 = 3
slf2d.NDP3 = 3
slf2d.NPOIN2 = n
slf2d.NPOIN3 = n
slf2d.NELEM2 = e
slf2d.NELEM3 = e
slf2d.IPARAM = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0]

#print '     +> Set SELAFIN mesh'
slf2d.MESHX = x
slf2d.MESHY = y

#print '     +> Set SELAFIN IPOBO'
junkIPOB = np.zeros(n-len(b))
junkIPOB = junkIPOB.astype(np.int16)
slf2d.IPOB2 = np.hstack((b,junkIPOB))
slf2d.IPOB3 = slf2d.IPOB2

#print '     +> Set SELAFIN IKLE'
slf2d.IKLE2 = ikle
slf2d.IKLE3 = ikle

#print '     +> Set SELAFIN times and cores'
# these two lists are empty after constructor is instantiated
slf2d.tags['cores'].append(0)
slf2d.tags['times'].append(0)

#slf2d.tags = { 'times':[0] } # time (sec)
#slf2d.DATETIME = sel.DATETIME
slf2d.DATETIME = [2015, 1, 1, 1, 1, 1]
#slf2d.tags = { 'cores':[long(0)] } # time frame 

#print '     +> Write SELAFIN headers'
slf2d.fole.update({ 'hook': open(slf_file,'w') })
slf2d.fole.update({ 'name': 'Converted from gmsh by pputils' })
slf2d.fole.update({ 'endian': ">" })     # big endian
slf2d.fole.update({ 'float': ('f',4) })  # single precision

slf2d.appendHeaderSLF()
slf2d.appendCoreTimeSLF(0) 
slf2d.appendCoreVarsSLF([z])

# to write the *.cli file

# to create the *.cli output file
cli_file = slf_file[0:len(slf_file)-4] + str(".cli")
fout = open(cli_file,"w")

for i in range(len(b)):
	fout.write(str('2 2 2 0.000 0.000 0.000 0.000 2 0.000 0.000 0.000 ') +
		str(slf2d.IPOB2[i]+1) + " " + str(i+1) + " " + "\n")
	



	

