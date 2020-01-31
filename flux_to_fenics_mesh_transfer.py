#! Flux2D 19.1
#/usr/bin/env python3

# the first one above is the shebang for the pyflux
# the second one above is the shebang for normal python3

"""
DOCSTRING
==================

INPUTS============
NODE_element_file : a txt file that's exported from FLUX. It specifies the
                    node number, node coordinates, and the weight of the nodes.

FACE_element_file : a txt file that's exported from FLUX. It specifies the
                    face element number, the nodes making up the face element,
                    and the type of the face element.

OUTPUTS===========
MESH_output       : an xml file that this python script generates. This xml
                    file contains the node and element information of the mesh
                    that's generated by the FLUX, and is ready to be imported
                    into FEniCS.
"""

"""
Import Python Libraries
"""

import sys, getopt          # for script I/O arguments detection
from fnmatch import fnmatch # for recognizing patterns in a string of characters

"""
Function Definitions
"""

def check_the_inputoutput_arguments(script_arguments):
    # CHECK FOR I/O ARGUMENTS
    # initialize the input and output filenames
    inputfile = []
    outputfile = ''
    # try for the options
    try:
        opts, args = getopt.getopt(script_arguments, "hi:o:", ["ifile=","ofile="])
    except getopt.GetoptError:
        sys.exit("Error: Unrecognized option specified! and/or \
input file missing!")
    # store the input and output filenames
    for opt, arg in opts:
        if opt == '-h':
            # display help
            sys.exit('flux_to_fenics_mesh_transfer.py -i <NODE_element_file> -i \
<FACE_element_file> -o <MESH_output>')
        elif opt in ("-i", "--ifile"):
            # store input filename
            inputfile.append(arg)
        elif opt in ("-o", "--ofile"):
            # store output filename
            outputfile = arg

    if (inputfile == []) or (outputfile == ''):
        sys.exit('Error: I/O files are not specified!')

    print("Normal commencement.")
    print('Input files are : ', inputfile)
    print('Output files are : ', outputfile)

    return inputfile, outputfile

def scrub_node_element_file(inputfiles):
    # define filenames
    node_element_file = inputfiles[0]
    node_element_file_cleaned = 'node_element_file_cleaned.txt'

    # define text patterns for the relevant node info
    pattern1 = '*Node*'
    pattern2 = '* coordinates *'
    pattern3 = '*WEIGHT*'

    with open(node_element_file_cleaned, 'w') as cleaned: # open write-only
        with open(node_element_file, 'r') as node_info:   # open read-only
            lines = node_info.readlines() # read all the lines in the file
            for i in range(0, len(lines)):# search through the read lines
                # check for the patterns of text in the lines
                if fnmatch(lines[i], pattern1):
                    # Node number info
                    cleaned.write(lines[i])
                elif fnmatch(lines[i], pattern2):
                    # Node coordinate info
                    cleaned.write(lines[i]) # Node number
                    cleaned.write(lines[i+1]) # x-coordinate value
                    cleaned.write(lines[i+2]) # y-coordinate value
                    cleaned.write(lines[i+3]) # z-coordinate value
                elif fnmatch(lines[i], pattern3):
                    # Node weight info
                    cleaned.write(lines[i])

    # return the name of the cleaned node info file
    return node_element_file_cleaned, pattern2

def retrieve_node_information(node_element_file_cleaned, pattern2):
    # save the nodes in a list
    # list's element order designate the node number
    # in this sense:
    #    0eth element of list is Node(1)
    #    1st  element of list is Node(2)
    #    2nd  element of list is Node(3)
    #    ...  ................... .......
    #    nth  element of list is Node(n+1)
    node_list = [] # initilize as an empty list
    with open(node_element_file_cleaned, 'r') as cleaned:
        lines = cleaned.readlines()
        for i in range(0, len(lines)):
            if fnmatch(lines[i], pattern2):
                node_list = node_list + \
                [[lines[i+1].replace(' ', '').replace('\n', '').replace('E','e'), \
                lines[i+2].replace(' ', '').replace('\n', '').replace('E','e'), \
                lines[i+3].replace(' ', '').replace('\n', '').replace('E','e')]]

    # node_list contains the xyz-coordinates of the nodes.
    # the node number is contained in the element indices. For example, 0th element
    #    of the node_list belongs to the node 1. The 1st element of the node_list
    #    belongs to the node 2, and so forth.
    return node_list

def write_nodes(outputfile, node_list):
    # define the header of the xml file
    xml_header = \
    """<?xml version="1.0" encoding="UTF-8"?>

<dolfin xmlns:dolfin="http://www.fenicsproject.org">
<mesh celltype="triangle" dim="2">
<vertices size="%d">
"""
    with open(outputfile, 'w') as notepad: # open write-only
        notepad.write(xml_header % len(node_list)) # write the xml file header
        for i in range(0, len(node_list)): # write xyz-coordinates of nodes
            notepad.write('      <vertex index="%d" x="%s" y="%s" z="%s"/>\n' \
            % (i, node_list[i][0], node_list[i][1], node_list[i][2]))

        notepad.write('    </vertices>\n') # write the closing of vertices info

def scrub_face_element_file(inputfiles):
    # define filenames
    face_element_file = inputfiles[1]
    face_element_file_cleaned = 'face_element_file_cleaned.txt'
    face_element_node_info = 'face_element_node_info.txt' # node information
    face_element_face_info = 'face_element_face_info.txt' # face information

    # define text patterns for the relevant face info
    pattern4 = '*FaceElement*'
    pattern5 = '*NODES*'
    pattern6 = '*TYPE*'
    pattern7 = '*LOC*'

    with open(face_element_file_cleaned, 'w') as face_cleaned: # open write-only
        with open(face_element_file, 'r') as face_info:        # open read-only
            face_lines = face_info.readlines() # read all the lines in the file
            for i in range(0, len(face_lines)):# search through the read lines
                if fnmatch(face_lines[i], pattern4):
                    # Face element number info
                    face_cleaned.write(face_lines[i])
                elif fnmatch(face_lines[i], pattern5):
                    # Face element nodes info
                    face_cleaned.write(face_lines[i])
                elif fnmatch(face_lines[i], pattern6):
                    # Face element type info
                    face_cleaned.write(face_lines[i])
                elif fnmatch(face_lines[i], pattern7):
                    # Face element LOC info
                    face_cleaned.write(face_lines[i])

    # further clean the face file for node numbers
    with open(face_element_node_info, 'w') as face_super_cleaned: # open write-only
        with open(face_element_file_cleaned, 'r') as face_info:            # open read-only
            face_lines = face_info.readlines() # read all the lines in the file
            for i in range(0, len(face_lines)):# search through the read lines
                if fnmatch(face_lines[i], pattern5):
                    # Only retain node info of the face elements
                    face_super_cleaned.write(face_lines[i])

    # further clean the face file for Face geometric entities
    with open(face_element_face_info, 'w') as face_super_cleaned: # open write-only
        with open(face_element_file_cleaned, 'r') as face_info:   # open read-only
            face_lines = face_info.readlines() # read all the lines in the file
            for i in range(0, len(face_lines)):# search through the read lines
                if fnmatch(face_lines[i], pattern7):
                    # Only retain node info of the face elements
                    face_super_cleaned.write(face_lines[i])

    return face_element_node_info, face_element_face_info

def retrieve_face_information(face_element_node_info, face_element_face_info):
    # collect the node numbers for each face elements
    with open(face_element_node_info, 'r') as face_super_cleaned: # open read-only
        lines = face_super_cleaned.readlines() # read all the lines in the file
        face_list = [] # initialize the face_list
        for i in range(0, len(lines)): # append the node numbers to the face_list
            face_list = face_list + \
            [[str(int(lines[i].split(' ')[9].replace('(', '').replace(')', ''))-1), \
            str(int(lines[i].split(' ')[11].replace('(', '').replace(')', ''))-1), \
            str(int(lines[i].split(' ')[13].replace('(', '').replace(')', ''))-1)]]

    # collect the Face geometric entity info for each face elements
    with open(face_element_face_info, 'r') as face_super_cleaned: # open read-only
        lines = face_super_cleaned.readlines() # read all the lines in the file
        # append to the existing face_list as 4th dimension for each element
        for i in range(0, len(lines)): # append the node numbers to the face_list
            face_list[i] = face_list[i] + \
            [lines[i].split(' ')[9].replace('(', '').replace(')', '')]

    return face_list

def write_faces(outputfile, face_list):
    # define the footer of the xml file
    xml_footer = \
    """    </cells>
  </mesh>
</dolfin>

"""
    with open(outputfile, 'a') as notepadtwo: # open append-only
        notepadtwo.write('    <cells size="%d">\n' % len(face_list))
        for i in range(0, len(face_list)): # write the node numbers for each faces
            notepadtwo.write('      <triangle index="%d" v0="%s" v1="%s" v2="%s"/>\n' \
            % (i, face_list[i][0], face_list[i][1], face_list[i][2]))

        notepadtwo.write(xml_footer) # end of the xml file

#def write_physical_region(face_list):
    # write xml_header
    # write face index physical property value


def flux_commands():
    # flux commands to export the node and face element info as txt files
    # export node information into a txt file on the current folder
    # export face information into a txt file on the current folder
    # feed those two files as inputs to the check_the_inputoutput_arguments()
    # commence with the normal operation of the remaining script

    # define filenames
    node_element_file = 'mesh-node-export-first-order.txt'
    face_element_file = 'mesh-face-export-first-order.txt'
    mesh_output = 'mesh.xml'
    face_physical_description='face_physical_description.txt'

    # Flux commands to export node, and face information into txt files
    Node[ALL].exportTXT(txtFile=node_element_file, mode='replace')
    FaceElement[ALL].exportTXT(txtFile=face_element_file, mode='replace')

    inputfile = [node_element_file, face_element_file]

    # create a text file describing the physical region names and the
    #   corresponding geometric face entities
    with open(face_physical_description, 'w') as face_description: # open append-only
        i = 1
        j = True
        while j:
            try:
                face_description.write('Face (number) is : (face_region_name)'.\
                format(number = i, face_region_name = Face[i].region.name))
                i += 1
            except:
                j = False

    return inputfile, mesh_output

def main():

    if sys.argv == ['pydb.py']:
        inputfiles, outputfile = flux_commands()
    else:
        inputfiles, outputfile = check_the_inputoutput_arguments(sys.argv[1:])

    node_element_file_cleaned, pattern2 = scrub_node_element_file(inputfiles)

    node_list = retrieve_node_information(node_element_file_cleaned, pattern2)

    write_nodes(outputfile, node_list)

    face_element_node_info, face_element_face_info = scrub_face_element_file(inputfiles)

    face_list = retrieve_face_information(face_element_node_info, face_element_face_info)

    write_faces(outputfile, face_list)

    #write_physical_region(face_list)

"""
Run the Main Function
"""
main()
