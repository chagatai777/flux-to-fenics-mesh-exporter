#! Flux2D 19.1
#/usr/bin/env python3

# the first one above is the shebang for the pyflux
# the second one above is the shebang for normal python3

# Attention! pyflux uses python2.7

"""
FLUX TO FENICS MESH TRANSFER

A python script for exporting the Flux mesh of a geometry into FEniCS.

Written as part of the master's degree thesis work. Cagatay Eren, 2019 - 2020

INPUTS============
NODE_element_file : a txt file that's exported from FLUX. It specifies the
                    node number, node coordinates, and the weight of the nodes.

FACE_element_file : a txt file that's exported from FLUX. It specifies the
                    face element number, the nodes making up the face element,
                    and the type of the face element.

FACE_physical_description : a txt file that's exported from FLUX. It specifies
                            the names assigned by user to the geometrical faces
                            of the geometry.

OUTPUTS===========
MESH_output       : an xml file that this python script generates. This xml
                    file contains the node and element information of the mesh
                    that's generated by the FLUX, and is ready to be imported
                    into FEniCS.

PHYSICAL_region   : an xml file that this python script generates. This xml
                    file contains the element numbers and their corresponding
                    physical region characteristics in coded numbers.
"""


# IMPORT PYTHON LIBRARIES
import sys, getopt          # for script I/O arguments detection
from fnmatch import fnmatch # for recognizing patterns in a string of characters


# DEFINE FUNCTIONS
def check_inputoutput_arguments(script_arguments):
    '''
    Check for the input/output arguments of the script call.

    The function is active when the python script is called from linux/windows
        terminal. It parses the command line call for input filenames and the
        output filenames. Input filenames are assumed to follow the `-i` flag,
        and output filenames are assumed to follow `-o` flag. The `-h` flag
        prints back a simple usage information.

    Parameters
    ----------
    script_arguments : list
        This is a list of strings which contain the user's specification for the
            input/output filenames.

    Returns
    -------
    inputfile : list
        A list of strings which contains only the filenames given for `-i`
            flag.

    outputfile : list
        A list of strings which contains only the filenames given for `-o`
            flag.
    '''
    # initialize the input and output filenames
    inputfile = []
    outputfile = []
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
<FACE_element_file> -i <FACE_physical_description> -o <MESH_output> -o \
<PHYSICAL_region>')
        elif opt in ("-i", "--ifile"):
            # store input filename
            inputfile.append(arg)
        elif opt in ("-o", "--ofile"):
            # store output filename
            outputfile.append(arg)

    if (inputfile == []) or (outputfile == []):
        sys.exit('Error: I/O files are not specified!')

    print("Normal commencement.")
    print('Input files are : ', inputfile)
    print('Output files are : ', outputfile)

    return inputfile, outputfile

def scrub_node_element_file(inputfiles):
    '''
    Brush off the irrelevant information within the node element text file.

    The function receives the inputfiles list. Picks the zeroeth element in that
        list, and assumes it to be the name of the text file exported from Flux
        detailing the node information. Then, the function creates another text
        file for writing the relevant information of the nodes. These relevant
        information are parsed according to `pattern1`, `pattern2` and `pattern3`
        as defined below.

    Parameters
    ----------
    inputfiles : list
        A list of strings containing the filenames of input files that the user
            has provided to the script.

    Returns
    -------
    node_element_file_cleaned : string
        The name of the .txt file that the function has used to write the
            important information as parsed by `pattern1`, `pattern2` and
            `pattern3`.

    pattern2 : string
        The string for parsing the coordinate information of the nodes.

    Creates
    -------
    node_element_file_cleaned : .txt file
        A .txt file containing the simplified version of the node_element_file.
    '''
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

    # return the name of the cleaned node info file and pattern2
    return node_element_file_cleaned, pattern2

def retrieve_node_information(node_element_file_cleaned, pattern2):
    '''
    Retrieve and store the xyz-coordinates of individual nodes in a list.

    The function receieves the cleaned node element file, and the `pattern2`.
        Then, it creates the `node_list` for storing the xyz-coordinates of the
        nodes. The function follows the following convention:
            1) `node_list` element indices designate the node number:
                0eth element of list is Node(1)
                1st  element of list is Node(2)
                2nd  element of list is Node(3)
                ...  .................. .......
                n-1  element of list is Node(n)
                nth  element of list is Node(n+1)
            2) Each element of `node_list` is also a list of 3 elements:
                node_list == [[x-coord, y-coord, z-coord], --> Node (1)
                              [x-coord, y-coord, z-coord], --> Node (2)
                              [x-coord, y-coord, z-coord], --> Node (3)
                              [x-coord, y-coord, z-coord], --> Node (4)
                               ......., ......., ....... ,     .... ...
                              [x-coord, y-coord, z-coord], --> Node (n-1)
                              [x-coord, y-coord, z-coord], --> Node (n)
                              ]
                In this sense, len(node_list) equals to the total number of nodes
                that Flux has created for a given geometry. However, since python
                uses zero-index ordering, the zeroeth element of `node_list`
                gives the xyz-coordinates for Node (1) of Flux mesh.

    Parameters
    ----------
    node_element_file_cleaned : string
        The name of the .txt file containing the simplified node information.

    pattern2 : string
        The pattern to parse for, in order to catch the lines detailing the
            xyz-coordinates of the nodes.

    Returns
    -------
    node_list : list
        The list containing the xyz-coordinates of the nodes.
    '''
    node_list = [] # initilize as an empty list
    with open(node_element_file_cleaned, 'r') as cleaned:
        lines = cleaned.readlines()
        for i in range(0, len(lines)):
            if fnmatch(lines[i], pattern2):
                # parse the lines of the txt file
                node_list = node_list + \
                [[lines[i+1].replace(' ', '').replace('\n', '').replace('E','e'), \
                lines[i+2].replace(' ', '').replace('\n', '').replace('E','e'), \
                lines[i+3].replace(' ', '').replace('\n', '').replace('E','e')]]

    return node_list

def write_nodes(outputfile, node_list):
    '''
    Write the node number and their coordinates into an xml file.

    The function takes the outputfile which is a string naming the xml file to
        write the coordinates of the nodes into. Example: "mesh.xml". In writing
        the xml file, the function follows a formatting that is identifiable in
        FEniCS. `xml_header` contains the hardcoded info about the `celltype`
        and the `dim`. Lastly, the `xml_header` contains the total number of
        nodes, which is given in "<vertices size ="%d">". Here, the "%d"
        placeholder allows for writing the total node number for different mesh
        structures.

    This function doesn't return any values. It only creates an xml file in the
        working directory.

    Parameters
    ----------
    outputfile : string
        The name of the xml file to create.

    node_list : list
        The list containing the xyz-coordinates of the nodes.

    Creates
    -------
    outputfile : .xml file
        The first part of the xml file for the mesh, which contains the node
            numbers and the node coordinates.
    '''
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
    '''
    Brush off the irrelevant information within the face element text file.

    The function receives the inputfiles list. Picks the first element in that
        list, and assumes it to be the name of the text file exported from Flux
        detailing the face information. Then, the function creates another text
        file for writing the relevant information of the nodes. These relevant
        information are parsed according to `pattern4`, `pattern5`, `pattern6`
        and `pattern7` as defined below.

    Parameters
    ----------
    inputfiles : list
        A list of strings containing the filenames of input files that the user
            has provided to the script.

    Returns
    -------
    face_element_node_info : string
        The name of the txt file containing the node numbers for each faces.
            "Face", in the context of Flux, is synonymous with "element" that
            a mesh consists of. Nodes come together and define an element. Elements
            come together and define a mesh.

    face_element_face_info : string
        The name of the txt file containing the physical face location of each
            geometrical faces. "Geometrical face" means a single element of a
            mesh. "Physical face" means a collection of geometrical faces which
            have the common physical properties.

    Creates
    -------
    face_element_file_cleaned : .txt file
        A txt file containing the relevant parts of the given Flux txt file of
            faces.

    face_element_node_info : .txt file
        A txt file containing only the nodes of a given face element. The line
            numbers of this text file also encode the face number information.
            In this sense, the first line of this text file contains the node
            numbers of the face element (1). Second line of this text file
            contains the node numbers of the face element (2). And so on.

    face_element_face_info : .txt file
        A txt file containing only the physical region information of a given
            face element. Here, the numbers that are visible on each line,
            (1, 2, 3, ... and so on) encode the physical region information
            of a given face. The line numbers of this text file also encode the
            face number information. In this sense, the first line of this text
            file contains the node numbers of the face element (1). Second line
            of this text file contains the node numbers of the face element (2).
            And so on.
    '''
    # define filenames
    face_element_file = inputfiles[1]
    face_element_file_cleaned = 'face_element_file_cleaned.txt'
    face_element_node_info = 'face_element_node_info.txt' # node information
    face_element_face_info = 'face_element_face_info.txt' # face information

    # define text patterns for the relevant face info
    pattern4 = '*FaceElement*'
    pattern5 = '*NODES*'
    pattern6 = '*TYPE*'
    pattern7 = '* LOC *'

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

def retrieve_face_information(face_element_node_info, face_element_face_info, face_physical_description):
    '''
    Retrieve and store the node numbers and physical numbers of elements in a list.

    This function reads the lines of the face_element_node_info and face_element_face_info
        files and parses those lines for the node numbers of a given face element,
        and its physical region number.

    `face_list` == [[node1, node2, node3, physical-region-number], --> Face (1)
                    [node1, node2, node3, physical-region-number], --> Face (2)
                    [node1, node2, node3, physical-region-number], --> Face (3)
                    ......, ....., ....., .......................,     .... ...
                    [node1, node2, node3, physical-region-number], --> Face (n-1)
                    [node1, node2, node3, physical-region-number], --> Face (n)
                    ]

    Parameters
    ----------
    face_element_node_info : string
        The name of the txt file containing the node numbers for each faces.
            "Face", in the context of Flux, is synonymous with "element" that
            a mesh consists of. Nodes come together and define an element. Elements
            come together and define a mesh.

    face_element_face_info : string
        The name of the txt file containing the physical face location of each
            geometrical faces. "Geometrical face" means a single element of a
            mesh. "Physical face" means a collection of geometrical faces which
            have the common physical properties.

    face_physical_description : string

    Returns
    -------
    face_list : list
        The list containing the nodes of a face element, and physical region
            number of a face element.
    '''
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

    # replace the physical number codes with their reduced equivalents
    with open(face_physical_description, 'r') as physical_description: # open read-only
        lines = physical_description.readlines() # read all the lines in the file
        face_info = [] # collect face names
        for i in range(0, len(lines)):
            face_info = face_info + [lines[i].split(' ')[4].replace('\n', '')]

    face_unique_info = [] # collect unique face names
                              # and preserve occurrence order
    for face in face_info:
        if face not in face_unique_info:
            face_unique_info.append(face)

    for face in face_info:
        for index, s in enumerate(face_unique_info):
            if face == s:
                face_info[face_info.index(face)] = [index+1, face]

    # now update the face_list's physical-region-number according to face_info
    for element in face_list:
        element[3] = face_info[int(element[3])-1][0]

    return face_list

def write_faces(outputfile, face_list):
    '''
    Write the face number and their node numbers into an xml file.

    The function appends the information contained in `face_list` into the same
        xml file containing the node coordinate information. Example: "mesh.xml".
        In writing the xml file, the function follows a formatting that is identifiable
        in FEniCS.

    This function doesn't return any values. It only appends to an xml file in the
        working directory.

    Parameters
    ----------
    outputfile : list
        The name of the xml file to append.

    face_list : list
        The list containing the nodes of a face element, and physical region
            number of a face element.
    '''
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

def write_physical_region(outputfile ,face_list):
    '''
    Write the face number and their phyical region numbers into an xml file.

    This function doesn't return any values. It only writes to an xml file in the
        working directory.

    Parameters
    ----------
    outputfile : list
        The name of the xml file to write into.

    face_list : list
        The list containing the nodes of a face element, and physical region
            number of a face element.

    Creates
    -------
    outputfile : .xml file
        The xml file, which contains the face numbers and their corresponding
            physical region numbers.
    '''
    # define xml header
    xml_header = \
    """<?xml version="1.0" encoding="UTF-8"?>
<dolfin xmlns:dolfin="http://fenicsproject.org">
  <mesh_function type="uint" dim="2" size="%d">
"""
    # define xml footer
    xml_footer = \
    """  </mesh_function>
</dolfin>
"""

    # write xml_header
    # write the face element indices and the corresponding physical region number code
    with open(outputfile, 'w') as physical_region: # open write-only
        physical_region.write(xml_header % len(face_list))
        for i in range(0, len(face_list)): # write the node numbers for each faces
            physical_region.write('      <entity index="%s" value="%s"/>\n' \
            % (i, face_list[i][3]))

    # write xml footer
        physical_region.write(xml_footer) # end of the xml file


def flux_commands():
    '''
    Commands that are executed when the script is executed within Flux.

    Following commands specify the .txt and .xml filenames for the script, for
        future use by other function within the script. Further, the commands
        below export all node and face element information into a txt file in the
        working directory. Lastly, it compiles the names of different physical
        faces in the given Flux geometry.

    Returns
    -------
    inputfile : list
        A list of strings which contains only the filenames that the script
            will use to read informaion from.

    outputfile : list
        A list of strings which contains only the filenames that the script
            will use to write information into.

    Creates
    -------
    node_element_file : .txt file
        A txt file exported from Flux containing the various information about
            the nodes in a given Flux geometry.

    face_element_file : .txt file
        A txt file exported from Flux containing the various information about
            the faces in a given Flux geometry.

    face_physical_description : .txt file
        A txt file containing the names of the various physical regions in a
            given Flux geometry.

    '''
    # define filenames
    node_element_file = 'mesh-node-export-first-order.txt'
    face_element_file = 'mesh-face-export-first-order.txt'
    mesh_output = 'mesh.xml'
    face_physical_description='face-physical-description.txt'
    physical_region = 'physical_region.xml'

    # Flux commands to export node, and face information into txt files
    Node[ALL].exportTXT(txtFile=node_element_file, mode='replace')
    FaceElement[ALL].exportTXT(txtFile=face_element_file, mode='replace')

    # create a text file describing the physical region names and the
    #   corresponding geometric face entities
    with open(face_physical_description, 'w') as face_description:
        i = 1
        j = True
        while j:
            try:
                k = Face[i].region.name
                face_description.write('Face %d is : ' % (i))
                face_description.write(k)
                face_description.write('\n')
                i += 1
            except:
                j = False

    inputfile = [node_element_file, face_element_file, face_physical_description]
    outputfile = [mesh_output, physical_region]

    return inputfile, outputfile

def main():
    '''
    The main function calling all the other functions.

    The first if-else block below checks for whether the script is being called
        from a linux/windows terminal, or from within the Flux.
    '''

    if sys.argv == ['pydb.py']:
        inputfiles, outputfiles = flux_commands()
    else:
        inputfiles, outputfiles = check_inputoutput_arguments(sys.argv[1:])

    node_element_file_cleaned, pattern2 = scrub_node_element_file(inputfiles)

    node_list = retrieve_node_information(node_element_file_cleaned, pattern2)

    write_nodes(outputfiles[0], node_list)

    face_element_node_info, face_element_face_info = scrub_face_element_file(inputfiles)

    face_list = retrieve_face_information(face_element_node_info, face_element_face_info, \
inputfiles[2])

    write_faces(outputfiles[0], face_list)

    write_physical_region(outputfiles[1] ,face_list)

# RUN MAIN
main()
