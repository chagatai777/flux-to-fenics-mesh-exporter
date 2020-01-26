#!/usr/bin/env python3

"""
DOCSTRING
==================

INPUTS============
node_element_file : a txt file that's exported from FLUX. It specifies the
                    node number, node coordinates, and the weight of the nodes.

face_element_file : a txt file that's exported from FLUX. It specifies the
                    face element number, the nodes making up the face element,
                    and the type of the face element.

OUTPUTS===========
mesh_output       : an xml file that this python script generates. This xml
                    file contains the node and element information of the mesh
                    that's generated by the FLUX, and is ready to be imported
                    into FEniCS.
"""

"""
Import Python Libraries
"""

import sys, getopt # for script I/O arguments detection
from fnmatch import fnmatch     # for recognizing patterns in a string of characters

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
            sys.exit('test.py -i <node_element_file> -i <face_element_file> -o \
            <mesh_output>')
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
    pattern2 = '*coordinates*'
    pattern3 = '*WEIGHT*'

    with open(node_element_file_cleaned, 'w+') as cleaned:
        # erase the contents of the file `cleaned`
        cleaned.truncate(0)
        with open(node_element_file, 'r') as node_info:
            lines = node_info.readlines()
            for i in range(0, len(lines)):
                # check for the patterns of text in the lines
                if fnmatch(lines[i], pattern1):
                    # Node number info
                    cleaned.write(lines[i])
                elif fnmatch(lines[i], pattern2):
                    # Node coordinate info
                    cleaned.write(lines[i])
                    cleaned.write(lines[i+1])
                    cleaned.write(lines[i+2])
                    cleaned.write(lines[i+3])
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
    notepad_file = 'notepadone.xml'
    with open(notepad_file, 'w+') as notepad:
        notepad.truncate(0)
        notepad.write("""<?xml version="1.0" encoding="UTF-8"?>

<dolfin xmlns:dolfin="http://www.fenicsproject.org">
  <mesh celltype="triangle" dim="2">
    <vertices size="%d">
""" % len(node_list))
        for i in range(0, len(node_list)):
            notepad.write('      <vertex index="%d" x="%s" y="%s" z="%s"/>\n' \
            % (i, node_list[i][0], node_list[i][1], node_list[i][2]))

        notepad.write('    </vertices>\n')

    # return the name of the xml file
    return notepad_file

def scrub_face_element_file(inputfiles):
    # define filenames
    face_element_file = inputfiles[1]
    face_element_file_cleaned = 'face_element_file_cleaned.txt'
    face_element_file_super_cleaned = 'face_element_file_super_cleaned.txt'

    # define text patterns for the relevant face info
    pattern4 = '*FaceElement*'
    pattern5 = '*NODES*'
    pattern6 = '*TYPE*'

    with open(face_element_file_cleaned, 'w+') as face_cleaned:
        # erase the contents of the file `cleaned`
        face_cleaned.truncate(0)
        with open(face_element_file, 'r') as face_info:
            face_lines = face_info.readlines()
            for i in range(0, len(face_lines)):
                if fnmatch(face_lines[i], pattern4):
                    # Face element number info
                    face_cleaned.write(face_lines[i])
                elif fnmatch(face_lines[i], pattern5):
                    # Face element nodes info
                    face_cleaned.write(face_lines[i])
                elif fnmatch(face_lines[i], pattern6):
                    # Face element type info
                    face_cleaned.write(face_lines[i])

    # further clean the face file

    with open(face_element_file_super_cleaned, 'w+') as face_super_cleaned:
        # erase the contents of the file `cleaned`
        face_super_cleaned.truncate(0)
        with open(face_element_file_cleaned, 'r') as face_info:
            face_lines = face_info.readlines()
            for i in range(0, len(face_lines)):
                if fnmatch(face_lines[i], pattern5):
                    # Only retain node info of the face elements
                    face_super_cleaned.write(face_lines[i])

    return face_element_file_super_cleaned

def retrieve_face_information(face_element_file_super_cleaned):
    # collect the node numbers for each face elements

    with open(face_element_file_super_cleaned, 'r') as face_super_cleaned:
        lines = face_super_cleaned.readlines()
        face_list = []
        for i in range(0, len(lines)):
            face_list = face_list + \
            [[str(int(lines[i].split(' ')[9].replace('(', '').replace(')', ''))-1), \
            str(int(lines[i].split(' ')[11].replace('(', '').replace(')', ''))-1), \
            str(int(lines[i].split(' ')[13].replace('(', '').replace(')', ''))-1)]]

    # write the collected information on another xml file
    notepadtwo_file = 'notepadtwo.xml'

    with open(notepadtwo_file, 'r+') as notepadtwo:
        notepadtwo.truncate(0)
        notepadtwo.write('    <cells size="%d">\n' % len(face_list))
        for i in range(0, len(face_list)):
            notepadtwo.write('      <triangle index="%d" v0="%s" v1="%s" v2="%s"/>\n' \
            % (i, face_list[i][0], face_list[i][1], face_list[i][2]))

        notepadtwo.write('    </cells>\n')
        notepadtwo.write('  </mesh>\n')
        notepadtwo.write('</dolfin>\n')

    return notepadtwo_file

def write_xml_file(nodes_xml, faces_xml, outputfile):
    filenames = [nodes_xml, faces_xml]
    with open(outputfile, 'w+') as outfile:
        for fname in filenames:
            with open(fname) as infile:
                outfile.write(infile.read())

def main():
    inputfiles, outputfile = check_the_inputoutput_arguments(sys.argv[1:])
    node_element_file_cleaned, pattern2 = scrub_node_element_file(inputfiles)
    nodes_xml = retrieve_node_information(node_element_file_cleaned, pattern2)
    face_element_file_super_cleaned = scrub_face_element_file(inputfiles)
    faces_xml = retrieve_face_information(face_element_file_super_cleaned)
    write_xml_file(nodes_xml, faces_xml, outputfile)



"""
Run the Main Function
"""
main()
