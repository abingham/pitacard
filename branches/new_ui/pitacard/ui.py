# pitacard: A Leitner-method flashcard program
# Copyright (C) 2006-2008 Austin Bingham, Nate Ross
#
# This program is free software you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; see the file LICENSE. If not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# You can reach the authors at:
#     austin.bingham@gmail.com
#     teal@mailshack.com

import os.path
import gtk, gtk.glade
import stackio, csvio
import review_mode, options, profile, save_file_mgr
from model import *

def get_text(buffer):
    return buffer.get_text(buffer.get_start_iter(),
                           buffer.get_end_iter())

class UI:
    def delete_event(self, widget, event, data=None):
            self.quit()
            return True

    def 

    def __init__(self, gladefile, cfg):
        self.config = cfg
        self.profile = profile.Profile()

        self.gladefile = gladefile
        self.xml = gtk.glade.XML(self.gladefile, 'main_window')

        widgets = ['main_window',
                   'edit_card_button',
                   'delete_card_button',
                   'do_review_button',
                   'edit_card_menu',
                   'delete_card_menu',
                   'review_menu',
                   'statusbar_left',
                   'statusbar_right',
                   'review_frame',
                   'card_list_frame',
                   'card_list',
                   'front_text_view',
                   'back_text_view',
                   'review_toolbar',
                   'edit_toolbar',
                   'mainmenu_cards',
                   'mainmenu_review',
                   'toolbar_socket',
                   'review_socket']

        for widget in widgets:
            setattr(self, widget, 
                    self.xml.get_widget(widget))

        self.main_window.connect("delete_event", self.delete_event)

        self.save_file_mgr = save_file_mgr.SaveFileMgr(self.main_window,
                                                       ('pitacard stack', '.stack'),
                                                       self.new_handler,
                                                       self.open_handler,
                                                       self.save_handler)
        self.save_file_mgr.change_signal.connect(self.sync_ui)
        
        if self.config.get('startup', 'preservegeom') == 'true':
            self.main_window.resize(int(self.config.get('startup', 'lastwidth')), int(self.config.get('startup', 'lastheight')))
            self.main_window.move(int(self.config.get('startup', 'lastposx')), int(self.config.get('startup', 'lastposy')))
        else:
            self.main_window.resize(500, 500)
            self.main_window.move(380, 150)

        self.init_card_list()

        self.xml.signal_autoconnect({
            'on_gpl_activate' :
            lambda x: self.gpldisplay(),
            'on_about_activate' :
            lambda x: self.about(),
            'on_review_menu_activate' :
            lambda x: self.enter_review_mode(),
            'on_do_review_button_clicked' :
            lambda x: self.enter_review_mode(),
            'on_review_done_button_clicked' :
            lambda x: self.enter_edit_mode(),
            'on_review_done_menu_activate' :
            lambda x: self.enter_edit_mode(),
            'on_save_menu_activate' :
            lambda x: self.save(),
            'on_save_as_menu_activate' :
            lambda x: self.save_as(),
            'on_new_menu_activate':
            lambda x: self.new(),
            'on_open_menu_activate' :
            lambda x: self.open(),
            'on_quit_menu_activate' :
            lambda x: self.quit(),
            'on_card_list_row_activated' :
            lambda v,p,c: self.edit_selected_card(),
            'on_card_list_cursor_changed' :
            lambda x: self.sync_ui()
            })

        self.editor = edit_mode.EditMode(self.xml)
        self.reviewer = review_mode.ReviewMode(self.xml, 
                                               lambda: self.card_list.get_model())

        self.sync_ui()

    def new(self):
        self.save_file_mgr.new()

    def new_handler(self):
        self.profile = profile.Profile()
        self.card_list.get_model().clear()
        self.connect_model()
        return save_file_mgr.SaveFileMgr.OK

    def save(self):
        self.save_file_mgr.save()

    def save_as(self):
        self.save_file_mgr.save_as()

    def save_handler(self, filename):
        stackio.save(filename, 
                     self.card_list.get_model(), 
                     self.profile)
        return save_file_mgr.SaveFileMgr.OK

    def open(self, filename=None):
        self.save_file_mgr.open(filename)

    def open_handler(self, filename):
        self.profile, model = stackio.load(filename)
        self.card_list.set_model(model)
        self.connect_model()
        return save_file_mgr.SaveFileMgr.OK
        
    def init_card_list(self):
        self.card_list = self.xml.get_widget('card_list')

        col = gtk.TreeViewColumn('Front')
        cell = gtk.CellRendererText()
        cell.set_fixed_height_from_font(1)
        col.pack_start(cell, True)
        col.add_attribute(cell, 'text', FRONT_CIDX)
        col.set_sort_column_id(FRONT_CIDX)
        self.card_list.append_column(col)

        col = gtk.TreeViewColumn('Back')
        cell = gtk.CellRendererText()
        cell.set_fixed_height_from_font(1)
        col.pack_start(cell, True)
        col.add_attribute(cell, 'text', BACK_CIDX)
        col.set_sort_column_id(BACK_CIDX)
        self.card_list.append_column(col)

        col = gtk.TreeViewColumn('Bin')
        cell = gtk.CellRendererText()
        col.pack_start(cell, True)
        col.add_attribute(cell, 'text', BIN_CIDX)
        col.set_sort_column_id(BIN_CIDX)
        self.card_list.append_column(col)

        col = gtk.TreeViewColumn('Type')
        cell = gtk.CellRendererText()
        #cell.set_property('fontstyle', 'italic')
        col.pack_start(cell, True)
        col.add_attribute(cell, 'text', TYPE_CIDX)
        col.set_sort_column_id(TYPE_CIDX)
        self.card_list.append_column(col)        

        self.card_list.set_model(new_model())
        self.connect_model()

    def connect_model(self):
        model = self.card_list.get_model()
        model.connect('row-changed',
                      lambda m,p,i: self.save_file_mgr.flag_change())
        model.connect('row-deleted',
                      lambda m,p: self.save_file_mgr.flag_change())
        model.connect('row-inserted',
                      lambda m,p,i: self.save_file_mgr.flag_change())

    def sync_ui(self):
        cardlen = len(self.card_list.get_model())
        if cardlen == 1:
            self.statusbar_right.set_label("1 Card")
        else:
            self.statusbar_right.set_label(str(cardlen) + " Cards")

        have_cards = cardlen > 0

        # only review if there is at least one card
        self.do_review_button.set_sensitive(have_cards)
        self.review_menu.set_sensitive(have_cards)

        sel = self.card_list.get_selection()
        model,iter = sel.get_selected()

        have_selected = not not iter
        # only edit or delete if there is a selected card
        self.edit_card_button.set_sensitive(have_selected)
        self.delete_card_button.set_sensitive(have_selected)

        self.edit_card_menu.set_sensitive(have_selected)
        self.delete_card_menu.set_sensitive(have_selected)

        if self.save_file_mgr.filename:
            file_status = os.path.basename(self.save_file_mgr.filename)
        else:
            file_status = ''

        if self.save_file_mgr.unsaved_changes:
            file_status += ' [unsaved]'

        self.statusbar_left.set_label(file_status.strip())

    #def deck_changed(self):
    #    self.save_file_mgr.flag_change()
    #    self.sync_ui()

    #def front_edited(self, cell, path, new_text):
    #    self.card_list.get_model()[path][FRONT_CIDX] = new_text

    #def back_edited(self, cell, path, new_text):
    #    self.card_list.get_model()[path][BACK_CIDX] = new_text

    def gpldisplay(self):
        xml = gtk.glade.XML(self.gladefile, 'GPLDlg')
        dlg = xml.get_widget('GPLDlg')
        dlg.set_transient_for(self.main_window)
        dlg.run()
        dlg.destroy()

    def about(self):
        xml = gtk.glade.XML(self.gladefile, 'AboutDlg')
        dlg = xml.get_widget('AboutDlg')
        dlg.set_transient_for(self.main_window)
        dlg.run()
        dlg.destroy()

    def enter_edit_mode(self):
        # TODO: Mode changes should do the menus too

        self.toolbar_socket.remove(self.review_toolbar)
        self.ui_socket.remove(self.review_frame)

        self.toolbar_socket.add(self.card_list_toolbar)
        self.toolbar_socket.add(self.card_list_frame)
        '''
        self.review_frame.hide()
        self.review_toolbar.hide()
        self.mainmenu_review.hide()

        self.card_list_frame.show()
        self.edit_toolbar.show()
        self.mainmenu_cards.show()
        '''

    def enter_review_mode(self):
        self.toolbar_socket.remove(self.card_list_toolbar)
        self.ui_socket.remove(self.card_list_frame)

        self.toolbar_socket.add(self.review_toolbar)
        self.ui_socket.add(self.review_frame)
        '''
        self.review_frame.show()
        self.review_toolbar.show()
        self.mainmenu_review.show()

        self.card_list_frame.hide()
        self.edit_toolbar.hide()
        self.mainmenu_cards.hide()
        '''

        self.reviewer.start_review()

    def quit(self):
        rslt = self.save_file_mgr.quit()
        if not save_file_mgr.SaveFileMgr.CANCEL == rslt:
            gtk.main_quit()
