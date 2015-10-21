#!/usr/bin/env python
# Antoine Hoarau <hoarau.robotics@gmail.com>
__version__="1.4.0"

from pkg_creator_tools import *
import gtk, gobject

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

