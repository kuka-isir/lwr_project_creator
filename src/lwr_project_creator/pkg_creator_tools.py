#!/usr/bin/env python
# Antoine Hoarau <hoarau.robotics@gmail.com>

import os, pwd, sys, time
import re
from collections import defaultdict
FILE_MARKER = '<files>'
import webbrowser

def attach(branch, trunk):
    '''
    Insert a branch of directories on its trunk.
    '''
    parts = branch.split('/', 1)
    if len(parts) == 1:  # branch is a file
        trunk[FILE_MARKER].append(parts[0])
    else:
        node, others = parts
        if node not in trunk:
            trunk[node] = defaultdict(dict, ((FILE_MARKER, []),))
        attach(others, trunk[node])

def prettify(d, indent=0):
    '''
    Print the file tree structure with proper indentation.
    '''
    for key, value in d.items():
        if key == FILE_MARKER:
            if value:
                print('  ' * indent + str(value))
        else:
            print('  ' * indent + str(key))
            if isinstance(value, dict):
                prettify(value, indent+1)
            else:
                print('  ' * (indent+1) + str(value))

def format_comp_name(comp_name):
    s = comp_name.replace(' ', '')
    s = s.strip()
    s = s.lower()
    return s

def format_class_name(c):
    s = c.replace(' ', '')
    s = s.split('_')
    s = [p[0].upper() + p[1:] for p in s if p]
    s = ''.join(s)
    s = s.strip()
    return s

def get_username():
   comment = pwd.getpwuid(os.getuid())[4]
   name = comment.split(',')[0]
   if name == "":
       return pwd.getpwuid(os.getuid())[0]

   return name

def get_home_dir():
    from os.path import expanduser
    return expanduser("~")

def create_dict_tree(list_of_path):
    main_dict = defaultdict(dict, ((FILE_MARKER, []),))
    for line in list_of_path:
        attach(line[1:], main_dict)
    return main_dict

def yn_choice(message, default='y'):
    choices = 'Y/n' if default.lower() in ('y', 'yes') else 'y/N'
    choice = raw_input("%s (%s) " % (message, choices))
    values = ('y', 'yes', '') if default == 'y' else ('y', 'yes')
    return choice.strip().lower() in values

def proj_exists(rel_path):
    return os.path.isdir(os.getcwd()+"/"+rel_path)


class ProcFile:
    '''
    This basic class deals with a single file in / file out. Can read/write, replace variables by text.
    '''
    def __init__(self,f_in_path,f_out_path,var=[]):
        assert isinstance(var,list)
        assert isinstance(f_in_path,str)
        assert isinstance(f_out_path,str)
        self.var =var
        self.f_in_path = f_in_path
        self.f_in = open(self.f_in_path,'r').read()
        self.f_out_path = f_out_path
        self.f_out=''
        self.dir_out=''
        tmp_dir = get_home_dir()+'/.tmp/'
        self.tmp_dir_out=tmp_dir
        self.tmp_file_out_path=self.tmp_dir_out

    def get_f_in(self):
        return self.f_in

    def process_var_in_file_path(self):
        '''
        Takes the raw output file path and replace the variables by predefined text.
        Does the same with the content of the input file, stores it in att f_in.
        '''
        self.f_out_path = self.process_var_in_str(self.get_file_out_path(), self.var)[0]
        self.f_out = self.process_var_in_str(self.get_f_in(), self.var)[0]
        self.dir_out = '/'.join(self.get_file_out_path().split('/')[:-1])

    def get_file_in_path(self):
        return self.f_in_path

    def get_file_out_path(self):
        return self.f_out_path


    def add_var(self,var):
        if not isinstance(var[0],list):
            var=[var]
        for v in var:
            self.var.append(v)

    @staticmethod
    def process_var_in_str(str_in,vars,overwrite=False):
        str_out=[]
        if not isinstance(str_in,list):
            str_in=[str_in]
        if not isinstance(vars[0],list):
            vars=[vars]
        for line in str_in:
            for v in vars:
                variable = v[0]
                repl_str = v[1]
                line = line.replace(variable,repl_str)
            str_out.append(line)
        return str_out

    def pretty_print(self):
        print("")
        print("f_in_path:",self.f_in_path)
        print("f_out_path: ",self.f_out_path)
        print("dir_out:",self.dir_out)
        print("vars : ",self.var)

    def write_tmp(self,f_name_in=''):
        self.tmp_file_out_path = self.tmp_dir_out+f_name_in
        self.__create_dir(self.tmp_dir_out)
        self.__write_stream_to_file(self.f_out,self.tmp_file_out_path,overwrite=True)

    def open_tmp(self):
        try:
            webbrowser.open(self.tmp_file_out_path)
        except Exception as e:
            print(e)

    def write(self):
        self.__create_dir(self.dir_out)
        self.__write_stream_to_file(self.f_out,self.f_out_path,overwrite=False)

    def remove_tmp_file(self):
        try:
            if not os.path.isdir(self.tmp_file_out_path):
                os.remove(self.tmp_file_out_path)
                print(self.tmp_file_out_path,'deleted')
        except Exception as e:
            print("Error while tying to remove ",self.tmp_file_out_path,e)

    def __write_stream_to_file(self,stream_in,f_out_path,overwrite=False):
        if overwrite or (not overwrite and not os.path.isfile(f_out_path)):
            with open(f_out_path,'w') as f :
                f.write(stream_in)
            print('Created file ' + f_out_path)
        else:
            print(f_out_path +' already exists, skipping.')

    def __create_dir(self,dir_out):
        if not os.path.isdir(dir_out):
            os.makedirs(dir_out)
            return True
        else:
            return False

class ProjGenerator():
    def __init__(self,root_path,project_name,classname,author='',template_dir='template'):
        assert isinstance(root_path,str)
        assert isinstance(project_name,str)
        assert isinstance(author,str)
        assert os.path.isdir(root_path)

        self.template_dir = template_dir
        self.template_extension = ''
        
        self.pfiles=[]

        if not classname:
            c = format_class_name(project_name)
            print(("Using default class name : "+c))
            self.classname = [c]
        else:
            self.classname = [format_class_name(c) for c in classname]

        self.author = author

        self.root_path = self.__wo_backslash_path(root_path)
        self.filename = [self.__get_filename_from_classname(c) for c in self.classname]
        self.project_name = format_comp_name(project_name)

        all_files_path_to_open = self.__get_file_tree_raw()
        files_path_to_open = [s for s in all_files_path_to_open if "CATKIN_IGNORE" not in s]
        files_path_to_open_abs = [f.split(self.template_dir)[1] for f in files_path_to_open]
        files_path_to_write_raw = [self.root_path+f.replace(self.template_extension,'') for f in files_path_to_open_abs]

        #### Defining the elements to remplace in files
        self.template_elem=[]
        self.template_elem.append(['@PROJECT_PATH@',self.get_project_path()])
        self.template_elem.append(['@PROJECT_NAME@',self.get_project_name()])
        self.template_elem.append(['@PROJECT_NAME_UPPER@',self.get_project_name().upper()])
        self.template_elem.append(['@AUTHOR@',self.get_author()])
        self.template_elem.append(['@DATE@',time.strftime("%c")])
        self.template_elem.append(['@YEAR@',time.strftime("%c")])

        ### Defining Multiple elements here
        self.template_elem_multi=[]
        self.template_elem_multi.append(['@CLASS_NAME@' ,self.get_class_name()])
        self.template_elem_multi.append(['@FILE_NAME@'   ,self.get_filename()])
        self.template_elem_multi.append(['@FILE_NAME_UPPER@',[fn.upper() for fn in self.get_filename()]])
        self.template_elem_multi.append(['@FILE_NAME_LOWER@',[fn.lower() for fn in self.get_filename()]])
        self.template_elem_multi.append(['@CLASS_NAME_UPPER@',[cl.upper() for cl in self.get_class_name()]])
        self.template_elem_multi.append(['@CLASS_NAME_LOWER@',[cl.lower() for cl in self.get_class_name()]])

        ## Processing the multiple elements
        files_path_to_write=[]
        for f_in,f_out in zip(files_path_to_open,files_path_to_write_raw):
            n_class = len(self.get_class_name())
            for i in range(n_class):
                new_f_out = [str(f_out)]
                new_var_out=[]
                for e in self.template_elem_multi:
                    new_var = [e[0],e[1][i]]
                    new_f_out = ProcFile.process_var_in_str(new_f_out, new_var)
                    new_var_out.append(new_var)
                if new_f_out[0] not in files_path_to_write:
                    pfile = ProcFile(str(f_in), str(new_f_out[0]),new_var_out)
                    files_path_to_write.append(new_f_out[0])
                    self.pfiles.append(pfile)

        ## Processing single elements
        for pfile in self.pfiles:
            pfile.add_var(self.template_elem)
            pfile.process_var_in_file_path()

    def __wo_backslash_path(self,path):
        if path[-1]=='/':
            return path[:-1]
        return path
    def get_list_of_files_out(self):
        input_=[]
        for pfile in self.pfiles:
            input_.append(pfile.f_out_path)
        return input_

    def write_files(self):
        for pfile in self.pfiles:
            pfile.write()
        return True

    def __find_dirs_in_subdirectories(self, subdirectory=''):
        if subdirectory:
            path = subdirectory
        else:
            path = os.path.dirname(__file__)
        dirs = []
        for root, dir, names in os.walk(path):
            for name in names:
                dirs.append(dir)
        return dirs

    def __find_files_in_subdirectories(self, subdirectory='',extension=None):
        if subdirectory:
            path = os.path.dirname(os.path.abspath(__file__))+'/'+subdirectory
        else:
            path = os.path.dirname(os.path.abspath(__file__))
        if not extension:
            extension=''
        files=[]
        for root, dirs, names in os.walk(path):
            for name in names:
                if name.endswith(extension) and not name.endswith('~'):
                    files.append(os.path.join(root, name))
        return files

    def __get_dir_tree_raw(self):
        dirs = self.__find_dirs_in_subdirectories(self.template_dir)
        return dirs

    def __get_file_tree_raw(self):
        return self.__find_files_in_subdirectories(self.template_dir, self.template_extension)

    def get_component_name(self):
        return self.comp_name

    def __get_filename_from_classname(self,classname):
        l = [e.lower() for e in re.findall('[A-Z][^A-Z]*',classname)] #Splits regarding to upper cases
        f = ''
        i = 0
        for i in range(len(l)):
            if len(l[i])==1 or i==0:
                f=f+l[i]
            else:
                f=f+'_'+l[i]
        return f

    def get_project_name(self):
        return self.project_name

    def get_filename(self):
        return self.filename

    def get_author(self):
        return self.author


    def __process_path(self,path):
        if not path[0]=='/':
            path = '/'+path
        if path[-1]=='/':
            return path[:-1]
        return path

    def get_project_path(self):
        return self.root_path+'/'+self.project_name

    def get_class_name(self):
        return self.classname
