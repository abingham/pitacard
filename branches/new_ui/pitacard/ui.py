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
import pitacard, pitacard.edit_mode, pitacard.review_mode, pitacard.profile, pitacard.save_file_mgr, pitacard.util

def get_text(buffer):
    return buffer.get_text(buffer.get_start_iter(),
                           buffer.get_end_iter())

class UI:
    def delete_event(self, widget, event, data=None):
            self.quit()
            return True

    def __init__(self, gladefile):
        self.profile = pitacard.profile.Profile()

        self.gladefile = gladefile
        self.xml = gtk.glade.XML(self.gladefile, 'main_window')

        pitacard.util.link_widgets(self.xml,
                                   self,
                                   ['card_list',
                                    'delete_card_button',
                                    'delete_card_menu',
                                    'do_review_button',
                                    'edit_card_button',
                                    'edit_card_menu',
                                    'edit_frame',
                                    'edit_toolbar',
                                    'mainmenu_cards',
                                    'mainmenu_review',
                                    'main_window',
                                    'review_frame',
                                    'review_menu',
                                    'review_toolbar',
                                    'statusbar_left',
                                    'statusbar_right',
                                    ])

        self.accel_group = gtk.AccelGroup()
        self.main_window.add_accel_group(self.accel_group)

        self.main_window.connect("delete_event", self.delete_event)

        self.save_file_mgr = pitacard.save_file_mgr.SaveFileMgr(self.main_window,
                                                                ('pitacard stack', '.stack'),
                                                                self.new_handler,
                                                                self.open_handler,
                                                                self.save_handler)
        self.save_file_mgr.change_signal.connect(self.sync_ui)
        
        if pitacard.conf.get('startup', 'preservegeom') == 'true':
            self.main_window.resize(int(pitacard.conf.get('startup', 'lastwidth')), int(pitacard.conf.get('startup', 'lastheight')))
            self.main_window.move(int(pitacard.conf.get('startup', 'lastposx')), int(pitacard.conf.get('startup', 'lastposy')))
        else:
            self.main_window.resize(500, 500)
            self.main_window.move(380, 150)

        self.xml.signal_autoconnect({
                'on_gpl_activate' :
                    lambda x: self.gpldisplay(),
                'on_about_activate' :
                    lambda x: self.about(),
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
                })

        self.editor = pitacard.edit_mode.EditMode(self)
        self.reviewer = pitacard.review_mode.ReviewMode(self) 

        self.enter_edit_mode()
        self.sync_ui()

    def new(self):
        self.save_file_mgr.new()

    def new_handler(self):
        self.profile = pitacard.profile.Profile()
        self.card_list.get_model().clear()
        return pitacard.save_file_mgr.SaveFileMgr.OK

    def save(self):
        self.save_file_mgr.save()

    def save_as(self):
        self.save_file_mgr.save_as()

    def save_handler(self, filename):
        stackio.save(filename, 
                     self.card_list.get_model(), 
                     self.profile)
        return pitacard.save_file_mgr.SaveFileMgr.OK

    def open(self, filename=None):
        self.save_file_mgr.open(filename)

    def open_handler(self, filename):
        self.enter_edit_mode()
        
        self.profile, model = stackio.load(filename)
        self.card_list.get_model().clear()
        for row in model:
            self.card_list.get_model().append(row)
        return pitacard.save_file_mgr.SaveFileMgr.OK
        
    def sync_ui(self):
        cardlen = len(self.card_list.get_model())
        if cardlen == 1:
            self.statusbar_right.set_label("1 Card")
        else:
            self.statusbar_right.set_label(str(cardlen) + " Cards")

        have_cards = cardlen > 0

        # TODO: mode-specific ui-syncing should be moved into the
        # mode implementations

        # only review if there is at least one card
        self.editor.do_review_action.set_sensitive(have_cards)

        # only edit or delete if there is a selected card
        self.editor.edit_action.set_sensitive(have_cards)
        self.editor.delete_action.set_sensitive(have_cards)

        if self.save_file_mgr.filename:
            file_status = os.path.basename(self.save_file_mgr.filename)
        else:
            file_status = ''

        if self.save_file_mgr.unsaved_changes:
            file_status += ' [unsaved]'

        self.statusbar_left.set_label(file_status.strip())

        self.editor.sync_ui()

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
        self.reviewer.exit_mode()
        self.editor.enter_mode()

    def enter_review_mode(self):
        self.editor.exit_mode()
        self.reviewer.enter_mode()
        self.reviewer.start_review()

    def quit(self):
        rslt = self.save_file_mgr.quit()
        if not pitacard.save_file_mgr.SaveFileMgr.CANCEL == rslt:
            gtk.main_quit()
