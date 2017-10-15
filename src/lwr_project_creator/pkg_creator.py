#!/usr/bin/env python
# Antoine Hoarau <hoarau.robotics@gmail.com>
__version__="1.4.0"

import argparse
import textwrap
from pkg_creator_tools import *

def main(argv):
    if len(argv)>1:
        ## Console interface
        parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent("""
        Welcome to the LWR Project Creator.
        ----------------------------------------------------------------------------
        | This script helps generate a controller for the KUKA LWR4+ at ISIR.      |
        | Launch this script without arguments to use the GUI.                     |
        |                                                                          |
        | example : lwr_create_pkg rtt_lwr_jt_controller -c JTController           |
        |                                                                          |
        | Author : Antoine Hoarau <hoarau.robotics@gmail.com>                      |
        ----------------------------------------------------------------------------

        """),epilog='Maintainer: Antoine Hoarau <hoarau.robotics@gmail.com>')


        parser.add_argument('--version', action='version', version='%(prog)s 2.0')

        parser.add_argument('-r','--root_dir',type=str,help='The root dir of your project (default : '+str(os.getcwd())+')',default=os.getcwd())

        parser.add_argument('project_name', type=str,nargs=1,help='The name of the main directory/namespace used in classes.')

        parser.add_argument('-c','--class_name', type=str, nargs='+',help='Your controller class name.')

        parser.add_argument('-a','--author', type=str,default=get_username(),help='Who wrote the script (default: '+get_username()+')')

        args,_ = parser.parse_known_args()
        project_name= args.project_name[0]
        root_dir = args.root_dir
        author=args.author
        class_name = args.class_name
        
        template_dir = 'template'
            
        fgen=ProjGenerator(root_dir,project_name,class_name,author,template_dir)
        ## Print the files to be generated
        input_ = fgen.get_list_of_files_out()
        main_dict = create_dict_tree(input_)

        if not proj_exists(project_name):
            print("Project to be generated")
            print("")
            prettify(main_dict)
            print("")
            #if(yn_choice("Generate the project ?", 'y')):
            if fgen.write_files():
                print('\nSuccessfully created files in %s. Please adjust the values in package.xml.' % root_dir)
        else:
            parser.print_usage()
            print("lwr_create_pkg: error: File exists: "+os.getcwd()+'/'+project_name+"/CMakeLists.txt")

    else:
        import pkg_creator_gui as gui
        ## Gui interface
        win = gui.LWRComponentAssistant()
        win.main()

if __name__ == '__main__':
    main(sys.argv)
    exit(0)
