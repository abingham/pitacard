# pitacard: A Leitner-method flashcard program
# Copyright (C) 2006 Austin Bingham, Nate Ross
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
import review, options, configmanage
from save_file_mgr import *
from model import *

def get_text(buffer):
    return buffer.get_text(buffer.get_start_iter(),
                           buffer.get_end_iter())

class UI:

    def delete_event(self, widget, event, data=None):
            self.quit()
            return True

    def __init__(self, gladefile, config):
        self.config = config
        self.profmodel = new_profile_model()

        self.gladefile = gladefile
        self.xml = gtk.glade.XML(self.gladefile, 'MainWindow')

        self.main_window = self.xml.get_widget('MainWindow')
        self.main_window.connect("delete_event", self.delete_event)

        self.save_file_mgr = SaveFileMgr(self.main_window,
                                         ('pitacard stack', '.stack'),
                                         self.new_handler,
                                         self.open_handler,
                                         self.save_handler)
        
        if self.config.readvalue('startup', 'preservegeom') == 'true':
            self.main_window.resize(int(self.config.readvalue('startup', 'lastwidth')), int(self.config.readvalue('startup', 'lastheight')))
            self.main_window.move(int(self.config.readvalue('startup', 'lastposx')), int(self.config.readvalue('startup', 'lastposy')))
        else:
            self.main_window.resize(500, 500)
            self.main_window.move(380, 150)

        self.init_card_list()

        self.edit_card_button = self.xml.get_widget('edit_card_button')
        self.delete_card_button = self.xml.get_widget('delete_card_button')
        self.do_review_button = self.xml.get_widget('do_review_button')

        self.edit_card_menu = self.xml.get_widget('edit_card_menu')
        self.delete_card_menu = self.xml.get_widget('delete_card_menu')
        self.review_menu = self.xml.get_widget('review_menu')

        self.bookmarks_list = self.xml.get_widget('bookmarks_menu')
        self.sync_bookmarks()
        self.status_filename = self.xml.get_widget('MainWindow - Status - Filename')
        self.status_cardcount = self.xml.get_widget('MainWindow - Status - Cardcount')

        self.xml.signal_autoconnect({
            'on_gpl_activate' :
            lambda x: self.gpldisplay(),
            'on_about_activate' :
            lambda x: self.about(),
            'on_startup_settings_activate':
            lambda x: self.startup_settings(),
            'on_do_options_button_clicked' :
            lambda x: self.options(),
            'on_options_menu_activate' :
            lambda x: self.options(),
            #'on_fav_menu_activate' :
            ###lambda x: self.addfav(),
            'on_add_card_button_clicked' :
            lambda x: self.add_card(),
            'on_add_card_menu_activate' :
            lambda x: self.add_card(),
            'on_edit_card_button_clicked' :
            lambda x: self.edit_selected_card(),
            'on_edit_card_menu_activate' :
            lambda x: self.edit_selected_card(),
            'on_delete_card_button_clicked' :
            lambda x: self.delete_selected_card(),
            'on_delete_card_menu_activate' :
            lambda x: self.delete_selected_card(),
            'on_review_menu_activate' :
            lambda x: self.do_review(),
            'on_do_review_button_clicked' :
            lambda x: self.do_review(),
            'on_save_menu_activate' :
            lambda x: self.save_file_mgr.save(),
            'on_save_as_menu_activate' :
            lambda x: self.save_file_mgr.save_as(),
            'on_new_menu_activate':
            lambda x: self.save_file_mgr.new(),
            'on_open_menu_activate' :
            lambda x: self.save_file_mgr.open(),
            'on_quit_menu_activate' :
            lambda x: self.quit(),
            'on_card_list_row_activated' :
            lambda v,p,c: self.edit_selected_card(),
            'on_card_list_cursor_changed' :
            lambda x: self.sync_ui()
            })

    def new_handler(self):
        self.profmodel.clear()
        self.card_list.get_model().clear()
        self.connect_model()
        self.status_filename.set_label('Unsaved')
        self.sync_ui()
        return SaveFileMgr.OK

    def save_handler(self, filename):
        stackio.save(filename, self.card_list.get_model(), self.profmodel)
        self.sync_ui()
        return SaveFileMgr.OK

    def open_handler(self, filename):
        self.profmodel, model = stackio.load(filename)
        self.card_list.set_model(model)
        self.connect_model()
        self.sync_ui()
        return SaveFileMgr.OK
        
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
                      lambda m,p,i: self.deck_changed())
        model.connect('row-deleted',
                      lambda m,p: self.deck_changed())
        model.connect('row-inserted',
                      lambda m,p,i: self.deck_changed())

    def sync_ui(self):
        cardlen = len(self.card_list.get_model())
        if cardlen == 1:
            self.status_cardcount.set_label("1 Card")
        else:
            self.status_cardcount.set_label(str(cardlen) + " Cards")
        
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
            self.status_filename.set_label(self.save_file_mgr.filename.split("/")[-1])
        else:
            self.status_filename.set_label('')

        if self.save_file_mgr.filename:
            title = 'PitaCard - %s' % os.path.basename(self.save_file_mgr.filename)
            if self.save_file_mgr.unsaved_changes:
                title += '*'
            self.main_window.set_title(title)
            print title

    def deck_changed(self):
        self.save_file_mgr.flag_change()
        self.sync_ui()

    def front_edited(self, cell, path, new_text):
        self.card_list.get_model()[path][FRONT_CIDX] = new_text

    def back_edited(self, cell, path, new_text):
        self.card_list.get_model()[path][BACK_CIDX] = new_text

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


    def startup_settings(self):
        settings_window = configmanage.StartupSettings(self)

    def options(self):
        opt_window = options.OptGUI(self.main_window, self.gladefile,
                                        self.profmodel)

    def sync_bookmarks(self):
        for d in self.bookmarks_list.get_children():
            self.bookmarks_list.remove(d)
            del d
        addbookmark = gtk.MenuItem('_Add Bookmark', True)
        addbookmark.connect('activate', self.addfav)
        separator = gtk.SeparatorMenuItem()
        self.bookmarks_list.append(addbookmark)
        self.bookmarks_list.append(separator)
        addbookmark.show()
        separator.show()

        newbookmarks = self.config.readvalue('bookmarks')
        if len(newbookmarks)>0:
            i=0
            self.leafmenuitem = {}
            for leaf in newbookmarks:
                
                #make menu item.
                self.leafmenuitem[i] = gtk.MenuItem(leaf, False)
                self.leafmenuitem[i].path = newbookmarks[leaf]
                self.leafmenuitem[i].num = 0    #this number is used to count selections. One selection, that is, moving the mouse over an object, does nothing, but the second, which can only occur with a click, opens the favorite.
                self.leafmenuitem[i].connect('select', self.fav_select)
                self.leafmenuitem[i].connect('deselect', self.fav_deselect)
                self.bookmarks_list.append(self.leafmenuitem[i])
                self.leafmenuitem[i].show()

                #submenu
                submenu = gtk.Menu()
                editthis = gtk.MenuItem('edit bookmark', False)
                deletethis = gtk.MenuItem('delete bookmark', False)
                editthis.connect_object('activate', self.editfav, self.leafmenuitem[i])
                deletethis.connect_object('activate', self.delfav, self.leafmenuitem[i])
                submenu.append(editthis)
                submenu.append(deletethis)
                editthis.show()
                deletethis.show()
                self.leafmenuitem[i].set_submenu(submenu)
                i +=1

    def fav_select(self, favorite):
        try:
            str(favorite.num)
        except:
            favorite.num = 0
        favorite.num +=1
        if favorite.num == 2:
            self.open(favorite.path)
            
    def fav_deselect(self, favorite):
        favorite.num = 0

    def editfav(self, favorite):
       bookmark_window = configmanage.BookmarkEditor(self, favorite.get_child().get_label(), favorite.path)
       bookmark_window.window.connect('destroy', lambda w: self.sync_bookmarks())

    def addfav(self, junkobject=None):
        if self.filename != None:
            bookmark_window = configmanage.BookmarkEditor(self, self.filename.split("/")[-1], self.filename)
            bookmark_window.window.connect('destroy', lambda w: self.sync_bookmarks())

    def delfav(self, favorite):
        self.config.writevalue({'bookmarks':{favorite.get_child().get_label(): 'del'}})
        self.sync_bookmarks()

    def add_card(self):
        xml = gtk.glade.XML(self.gladefile, 'CardEditorDlg')
        dlg = xml.get_widget('CardEditorDlg')
        dlg.set_transient_for(self.main_window)
        bincombo = xml.get_widget('bin_combo')
        cardtypecombo = xml.get_widget('type_combo')
        bincombo.set_active(0)
        cardtypecombo.set_active(0)
        front_buffer = xml.get_widget('front_text_view').get_buffer()
        back_buffer = xml.get_widget('back_text_view').get_buffer()

        response = dlg.run()

        bin = bincombo.get_active()
        cardtype = cardtypes[cardtypecombo.get_active()]
        front = get_text(front_buffer)
        back = get_text(back_buffer)
        dlg.destroy()

        if not response == gtk.RESPONSE_OK: return
        if front == "" and back == "": return

        model = self.card_list.get_model()
        iter = model.append([front,
                             back,
                             bin,
                             cardtype])
        self.card_list.set_cursor(model.get_path(iter))
        self.save_file_mgr.flag_change()

    def edit_selected_card(self):
        sel = self.card_list.get_selection()
        model,iter = sel.get_selected()
        if not iter: return

        bin,cardtype,front,back = model.get(iter,
                                   BIN_CIDX,
                                   TYPE_CIDX,
                                   FRONT_CIDX,
                                   BACK_CIDX)

        xml = gtk.glade.XML(self.gladefile, 'CardEditorDlg')
        dlg = xml.get_widget('CardEditorDlg')
        dlg.set_transient_for(self.main_window)
        
        bincombo = xml.get_widget('bin_combo')
        bincombo.set_active(bin)

        cardtypecombo = xml.get_widget('type_combo')
	cardtypecombo.set_active(cardtypes.index(cardtype))

        front_buffer = xml.get_widget('front_text_view').get_buffer()
        front_buffer.set_text(front)

        back_buffer = xml.get_widget('back_text_view').get_buffer()
        back_buffer.set_text(back)

        response = dlg.run()
        bin = bincombo.get_active()
        cardtype = cardtypes[cardtypecombo.get_active()]
        front = get_text(front_buffer)
        back = get_text(back_buffer)
        dlg.destroy()

        if not response == gtk.RESPONSE_OK: return
        if front == "" and back == "": return

        model.set(iter,
                  BIN_CIDX, bin,
                  FRONT_CIDX, front,
                  BACK_CIDX, back,
                  TYPE_CIDX, cardtype)

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
        profile = options.GetOpts(self.profmodel, False)
        l = review.Review(self.main_window,
                            self.gladefile,
                            self.config,
                            self.card_list.get_model(),
			    profile)

    def quit(self):
        rslt = self.save_file_mgr.quit()
        if not SaveFileMgr.CANCEL == rslt:
            gtk.main_quit()
