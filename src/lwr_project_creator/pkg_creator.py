#!/usr/bin/env python
# Antoine Hoarau <hoarau.robotics@gmail.com>
__version__ = "1.3.0"

import gtk, gobject
import os, pwd, sys, time
from collections import defaultdict
import webbrowser
import argparse
import re
import textwrap
FILE_MARKER = '<files>'

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
    def __init__(self,root_path,project_name,classname,author=''):
        assert isinstance(root_path,str)
        assert isinstance(project_name,str)
        assert isinstance(author,str)
        assert os.path.isdir(root_path)


        self.template_dir = 'template'
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

        files_path_to_open = self.__get_file_tree_raw()
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


class LWRComponentAssistant(gtk.Assistant):
    def __init__(self):
        self.fgen = None
        gtk.Assistant.__init__(self)
        self.set_title('LWR CMake Project Creator v'+__version__)
        self.connect('prepare', self.__prepare_page_cb)
        self.scrolled_window = None

        self.connect('close', self.cb_close)

        self.connect("cancel", self.cb_close)

        self.connect("apply", self.cb_apply)

        self.component_count = 1

        self.__add_page_intro()

        self.__add_page_component()

        self.__add_page_confirm()

        self.set_default_size(400, 400)

        self.show()


    def main(self):
        gtk.main()
        self.clean_tmp_files()
    def __prepare_page_cb(self, widget, page):
        if page == self.page_confirm:
            if self.scrolled_window != None:
                self.page_confirm.remove(self.scrolled_window)
            treeview_confirm = self.__create_component_treeview()
            self.scrolled_window = gtk.ScrolledWindow()
            self.scrolled_window.add_with_viewport(treeview_confirm)
            self.scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
            self.page_confirm.pack_start(self.scrolled_window, expand=True)
            self.page_confirm.show_all()

    def __add_page_intro(self):
     # First page
        vbox = gtk.VBox(False, 4)
        vbox.set_border_width(4)

        label = gtk.Label("\nThis assistant will help you generate a new LWR project using the new CMake integration.\nIn the following page, you will get to specify the components that you need to create.\n")
        label.set_line_wrap(True)
        vbox.pack_start(label, True, True, 0)

        table = gtk.Table(4, 2, True)
        table.set_row_spacings(4)
        table.set_col_spacings(4)

        # Author
        label = gtk.Label("Author :")
        table.attach(label, 0, 1, 0, 1)
        self.author_entry = gtk.Entry()
        self.author_entry.set_text(get_username())
        table.attach(self.author_entry, 1, 2, 0, 1)

        # Project name # should be LWRens, LWRuta etc
        label = gtk.Label("Project Name :")
        table.attach(label, 0, 1, 1, 2)
        self.entry = gtk.Entry()
        self.entry.set_text("rtt_lwr_demo")
        table.attach(self.entry, 1, 2, 1, 2)
        self.entry.connect('changed', self.changed_comp_name_cb)

        vbox.pack_start(table, True, False, 0)

        # File chooser
        table.attach(gtk.Label("Root folder :"), 0, 1, 3, 4)
        #table.attach(gtk.Label(""), 0, 3, 3, 4)
        self.file_chooser = gtk.FileChooserButton('Select a folder')
        home = get_home_dir()
        self.file_chooser.set_filename(home)
        self.file_chooser.set_action(gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
        table.attach(self.file_chooser, 1, 2, 3, 4)
        vbox.show_all()

        self.append_page(vbox)
        self.set_page_title(vbox, 'LWR CMake Project Creator')
        self.set_page_type(vbox, gtk.ASSISTANT_PAGE_CONTENT)

        self.set_page_complete(vbox, True)
    def delete_event(self, widget, event, data=None):
        return False

    def destroy(self, widget, data=None):
        gtk.main_quit()

    def changed_comp_name_cb(self,entry):
        entry_text = entry.get_text()
        entry.set_text(format_comp_name(entry_text))
        return

    def edited_class_name_cb(self, cell, path, new_text, model ):
        model[path][0] = format_class_name(new_text)
        return

    def prio_edited_cb(self, renderer, path, new_text):
        itr = self.store.get_iter( path )
        self.store.set_value( itr, 1, new_text )

    def toggled_cb(self, cell, path_str, model):
        # get toggled iter
        iter = model.get_iter_from_string(path_str)
        toggle_item = model.get_value(iter, 2)

        # do something with the value
        toggle_item = not toggle_item

        # set new value
        model.set(iter, 2, toggle_item)

    def add_button_cb(self, widget):
        self.store.append(('Controller%d'%self.component_count, "public RTTLWRAbstract"))
        self.component_count += 1

    def delete_button_cb(self, widget):
        try:
            if len(self.store) > 1:
                path, column = self.treeview.get_cursor()
                iter = self.store.get_iter(path)
                self.store.remove(iter)
        except: pass

    def on_float_edited(self, widget, path, value):
        self.store[path][1] = float(value)

    def __add_page_component(self):
        vbox = gtk.VBox(False, 4)
        vbox.set_border_width(4)

        # Create buttons
        hbbox = gtk.HButtonBox()
        hbbox.set_layout(gtk.BUTTONBOX_END)
        hbbox.set_spacing(4)

        add_button = gtk.Button(stock=gtk.STOCK_ADD)
        add_button.connect('clicked', self.add_button_cb)
        delete_button = gtk.Button(stock=gtk.STOCK_DELETE)
        delete_button.connect('clicked', self.delete_button_cb)

        hbbox.add(add_button)
        hbbox.add(delete_button)

        vbox.pack_end(hbbox, False, False, 0)

        # Create model for combo
        #self.prio_combo_model = gtk.ListStore(gobject.TYPE_STRING)
        #for p in control_priority_list:
        #    self.prio_combo_model.append([p])

        # Create the model
        self.store = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
        self.store.append(('ControllerTest', "public RTTLWRAbstract"))

        # Create treeview
        self.treeview = gtk.TreeView(self.store)

        # Create cell renderers
        self.cellrenderer_name = gtk.CellRendererText()
        self.cellrenderer_name.set_property('editable', True)
        self.cellrenderer_name.connect('edited', self.edited_class_name_cb,self.store)

        self.cellrenderer_prio = gtk.CellRendererText()
        self.cellrenderer_prio.set_property('editable', False)
        #self.cellrenderer_prio.connect('edited', self.on_float_edited)

        #self.cellrenderer_ec = gtk.CellRendererToggle()
        #self.cellrenderer_ec.set_property('activatable', True)
        #self.cellrenderer_ec.connect('toggled', self.toggled_cb, self.store)

        # Create columns
        self.column_name = gtk.TreeViewColumn("Class Name", self.cellrenderer_name, text=0)
        self.column_name.set_resizable(True)
        self.column_name.set_expand(True)

        self.column_prio = gtk.TreeViewColumn("Inherits from", self.cellrenderer_prio)
        self.column_prio.set_resizable(True)
        self.column_prio.set_expand(True)
        self.column_prio.add_attribute(self.cellrenderer_prio, "text", 1)


        self.treeview.append_column(self.column_name)
        self.treeview.append_column(self.column_prio)

        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.add_with_viewport(self.treeview)
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        vbox.pack_start(scrolled_window, True, True, 0)
        vbox.show_all()

        self.append_page(vbox)
        self.set_page_title(vbox, 'Your Component Class Name')
        self.set_page_type(vbox, gtk.ASSISTANT_PAGE_CONTENT)

        self.set_page_complete(vbox, True)

    def __get_project_name(self):
        return self.entry.get_text()

    def __get_author(self):
        return self.author_entry.get_text()

    def __get_components_info(self):
        return [(row[0], row[1]) for row in self.store]

    def __get_components_class_names(self):
        names = []
        for row in self.store:
            name = row[0]
            names.append(name)
        return names

    def __get_components_control_priorities(self):
        names = []
        for row in self.store:
            name = row[1]
            names.append(name)
        return names


    def __get_components_name(self):
        names = []
        for row in self.store:
            name = row[0]
            names.append(name)
        return names


    def __get_root_dir(self):
        return self.file_chooser.get_filename()


    def __create_store(self,main_dict,store,it=None):
        for key, value in main_dict.items():
            if key == FILE_MARKER:
                if value:
                    for v in value:
                        store.append(it,[str(v)])
            else:
                it_next = store.append(it,[str(key)])
                if isinstance(value, dict):
                    self.__create_store(value,store,it_next)
                else:
                    store.append(it_next,[str(key)])

    def clean_tmp_files(self):
        try:
            for pfile in self.fgen.pfiles:
                pfile.remove_tmp_file()
        except: pass

    def __on_row_activated(self, tview, index, user_data):
        assert isinstance(tview,gtk.TreeView)
        assert isinstance(user_data,gtk.TreeViewColumn)
        model = tview.get_model()
        path_to_file=''
        for i in range(1,len(index)+1):
            path_to_file =path_to_file+'/'+ model[index[:i]][0]

        print(path_to_file)
        for pfile in self.fgen.pfiles:
            assert isinstance(pfile,ProcFile)
            if path_to_file == pfile.f_out_path:
                f_name = path_to_file.split('/')[-1]
                pfile.write_tmp(f_name)
                pfile.open_tmp()

    def __create_component_treeview(self):
        root_dir = self.__get_root_dir()
        project_name = self.__get_project_name()
        class_name = self.__get_components_class_names()
        control_priority = self.__get_components_control_priorities()
        author = self.__get_author()
        print(root_dir,project_name,class_name,control_priority,author)
        self.fgen=ProjGenerator(root_dir,project_name,class_name,author)

        input_ = self.fgen.get_list_of_files_out()


        main_dict = create_dict_tree(input_)

        store = gtk.TreeStore(gobject.TYPE_STRING)
        self.__create_store(main_dict, store, None)

        # Create treeview
        treeview = gtk.TreeView(store)
        treeview.connect("row-activated", self.__on_row_activated)
        cellrenderer_name = gtk.CellRendererText()
        column_name = gtk.TreeViewColumn("Project", cellrenderer_name, text=0)
        treeview.append_column(column_name)
        treeview.expand_all()

        return treeview

    def __add_page_confirm(self):
        self.page_confirm = gtk.VBox(False, 4)

        label = gtk.Label()
        label.set_markup("The following project will be generated.")
        label.set_line_wrap(True)
        self.page_confirm.pack_end(label, expand=False)
        self.page_confirm.show_all();

        self.append_page(self.page_confirm)
        self.set_page_title(self.page_confirm, "Confirm and Create CMake Project")
        self.set_page_type(self.page_confirm, gtk.ASSISTANT_PAGE_CONFIRM)
        self.set_page_complete(self.page_confirm, True)

    def cb_close(self, widget):
        gtk.main_quit()

    def cb_apply(self, widget):
        self.fgen.write_files()
        return

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
        | Author : Antoine Hoarau <hoarau.robotics@gmail.com                       |
        ----------------------------------------------------------------------------

        """),epilog='Maintainer: Antoine Hoarau <hoarau.robotics AT gmail DOT com>')


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
        fgen=ProjGenerator(root_dir,project_name,class_name,author)
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
            print("lwr_create_pkg: error: File exists: "+os.getcwd()+project_name+"/CMakeLists.txt")

    else:
        ## Gui interface
        win = LWRComponentAssistant()
        win.main()

if __name__ == '__main__':
    main(sys.argv)
    exit(0)
