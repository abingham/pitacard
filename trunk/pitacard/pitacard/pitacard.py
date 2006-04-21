# pitacard: A Leitner-method flashcard program
# Copyright (C) 2006 Austin Bingham
#
# This program is free software# you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation# either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY# without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program# if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# You can reach the author at:
#     austin.bingham@gmail.com

import gtk, gtk.glade
from save_file_mgr import *
import db, leitner
from model import *

def get_text(buffer):
    return buffer.get_text(buffer.get_start_iter(),
                           buffer.get_end_iter())

class UI(SaveFileMgr):
    def __init__(self, gladefile, config):
        SaveFileMgr.__init__(self)
        self.config = config

        self.gladefile = gladefile
        self.xml = gtk.glade.XML(self.gladefile, 'MainWindow')
        
        self.main_window = self.xml.get_widget('MainWindow')
        self.init_card_list()

        self.edit_card_button = self.xml.get_widget('edit_card_button')
        self.delete_card_button = self.xml.get_widget('delete_card_button')
        self.do_review_button = self.xml.get_widget('do_review_button')

        self.xml.signal_autoconnect({
            'on_add_card_button_clicked' :
            lambda x: self.add_card(),
            'on_edit_card_button_clicked' :
            lambda x: self.edit_selected_card(),
            'on_delete_card_button_clicked' :
            lambda x: self.delete_selected_card(),
            'on_do_review_button_clicked' :
            lambda x: self.do_review(),
            'on_save_menu_activate' :
            lambda x: self.save(),
            'on_save_as_menu_activate' :
            lambda x: self.save_as(),
            'on_open_menu_activate' :
            lambda x: self.open(),
            'on_quit_menu_activate' :
            lambda x: self.quit(),
            'on_leitner_log2_menu_activate' :
            lambda x: self.do_review(),
            'on_card_list_row_activated' :
            lambda v,p,c: self.edit_selected_card(),
            'on_card_list_cursor_changed' :
            lambda x: self.sync_ui()
            })

    def save_impl(self, filename):
        db.save(filename, self.card_list.get_model())
        return SaveFileMgr.OK

    def open_impl(self, filename):
        model = db.load(filename)
        self.card_list.set_model(model)
        self.connect_model()
        self.sync_ui()
        return SaveFileMgr.OK
        
    def init_card_list(self):
        self.card_list = self.xml.get_widget('card_list')

        col = gtk.TreeViewColumn('Bin')
        cell = gtk.CellRendererText()
        col.pack_start(cell, True)
        col.add_attribute(cell, 'text', BIN_IDX)
        col.set_sort_column_id(BIN_IDX)
        self.card_list.append_column(col)

        col = gtk.TreeViewColumn('Front')
        cell = gtk.CellRendererText()
        #cell.set_property('editable', True)
        #cell.connect('edited', self.front_edited)
        col.pack_start(cell, True)
        col.add_attribute(cell, 'text', FRONT_IDX)
        col.set_sort_column_id(FRONT_IDX)
        self.card_list.append_column(col)

        col = gtk.TreeViewColumn('Back')
        cell = gtk.CellRendererText()
        #cell.set_property('editable', True)
        #cell.connect('edited', self.back_edited)
        col.pack_start(cell, True)
        col.add_attribute(cell, 'text', BACK_IDX)
        col.set_sort_column_id(BACK_IDX)
        self.card_list.append_column(col)

        self.card_list.set_model(new_model())
        self.connect_model()

    def connect_model(self):
        model = self.card_list.get_model()
        model.connect('row-changed',
                      lambda m,p,i: self.deck_changed())
        model.connect('row-deleted',
                      lambda m,p: self.deck_changed())
        model.connect('row-inserted',
                      lambda m,p,i: self.deck_changed())

    def sync_ui(self):
        # only review if there is at least one card
        self.do_review_button.set_sensitive(len(self.card_list.get_model()) > 0)

        sel = self.card_list.get_selection()
        model,iter = sel.get_selected()

        # only edit or delete if there is a selected card
        self.edit_card_button.set_sensitive(not not iter)
        self.delete_card_button.set_sensitive(not not iter)

    def deck_changed(self):
        self.flag_change()
        self.sync_ui()

    def front_edited(self, cell, path, new_text):
        self.card_list.get_model()[path][FRONT_IDX] = new_text

    def back_edited(self, cell, path, new_text):
        self.card_list.get_model()[path][BACK_IDX] = new_text

    def add_card(self):
        xml = gtk.glade.XML(self.gladefile, 'CardEditorDlg')
        dlg = xml.get_widget('CardEditorDlg')
        combo = xml.get_widget('bin_combo')
        combo.set_active(0)
        front_buffer = xml.get_widget('front_text_view').get_buffer()
        back_buffer = xml.get_widget('back_text_view').get_buffer()

        response = dlg.run()

        bin = combo.get_active()
        front = get_text(front_buffer)
        back = get_text(back_buffer)
        dlg.destroy()

        self.card_list.get_model().append([bin,
                                           front,
                                           back])

    def edit_selected_card(self):
        sel = self.card_list.get_selection()
        model,iter = sel.get_selected()
        if not iter: return

        bin,front,back = model.get(iter,
                                   BIN_IDX,
                                   FRONT_IDX,
                                   BACK_IDX)

        xml = gtk.glade.XML(self.gladefile, 'CardEditorDlg')
        dlg = xml.get_widget('CardEditorDlg')
        
        combo = xml.get_widget('bin_combo')
        combo.set_active(bin)

        front_buffer = xml.get_widget('front_text_view').get_buffer()
        front_buffer.set_text(front)

        back_buffer = xml.get_widget('back_text_view').get_buffer()
        back_buffer.set_text(back)

        response = dlg.run()
        bin = combo.get_active()
        front = get_text(front_buffer)
        back = get_text(back_buffer)
        dlg.destroy()

        if not response == gtk.RESPONSE_OK: return

        model.set(iter,
                  BIN_IDX, bin,
                  FRONT_IDX, front,
                  BACK_IDX, back)

    def delete_selected_card(self):
        sel = self.card_list.get_selection()
        model,iter = sel.get_selected()
        if not iter: return

        dlg = gtk.MessageDialog(self.main_window,
                                False,
                                gtk.MESSAGE_QUESTION,
                                gtk.BUTTONS_YES_NO,
                                'Delete entry?')
        rslt = dlg.run()
        dlg.destroy()
        if rslt == gtk.RESPONSE_NO: return

        model.remove(iter)

    def do_review(self):
        l = leitner.Leitner_log2(self.gladefile,
                                 self.card_list.get_model())
