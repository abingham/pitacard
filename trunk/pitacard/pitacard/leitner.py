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

from math import *
import random
import gtk, gtk.glade
import model

class Leitner:
    def __init__(self, gladefile, cards, bins=10):
        assert len(cards) > 0, 'No cards in deck supplier to Leitner review'
        
        self.cards = cards
        self.num_bins = bins

        xml = gtk.glade.XML(gladefile, 'ReviewDlg')
        self.dlg = xml.get_widget('ReviewDlg')
        self.next_button = xml.get_widget('next_button')
        self.correct_button = xml.get_widget('correct_button')
        self.wrong_button = xml.get_widget('wrong_button')
        self.front_text = xml.get_widget('front_text')
        self.back_text = xml.get_widget('back_text')

        self.dlg.resize(500,500)

        if len(self.cards) < 1: self.next_button.set_sensitive(False)
        self.correct_button.set_sensitive(False)
        self.wrong_button.set_sensitive(False)

        xml.signal_autoconnect({
            'on_next_button_clicked' :
            lambda x: self.flip_card(),
            'on_correct_button_clicked' :
            lambda x: self.answered(True),
            'on_wrong_button_clicked' :
            lambda x: self.answered(False)
            })

        # initialize view to first card
        self.show_next_card()

        self.dlg.run()
        self.dlg.destroy()

    def answered(self, correct):
        self.update_card(self.curr_card, correct)
        self.show_next_card()

    def flip_card(self):
        self.back_text.get_buffer().set_text(self.curr_card[model.BACK_IDX])
        self.correct_button.set_sensitive(True)
        self.wrong_button.set_sensitive(True)
        self.next_button.set_sensitive(False)
        
    def show_next_card(self):
        self.curr_card = self.get_next_card()
        self.front_text.get_buffer().set_text(self.curr_card[model.FRONT_IDX])
        self.back_text.get_buffer().set_text('')

        self.correct_button.set_sensitive(False)
        self.wrong_button.set_sensitive(False)
        self.next_button.set_sensitive(True)

    def have_cards(self):
        return len(self.cards) > 0

    def bin_value(self, bin):
        assert bin in range(self.num_bins), 'bin %d not in range (0,%d)' % (bin,self.num_bins)
        inv = self.num_bins - bin
        return 2**inv

    def get_next_card(self):
        # count cards w/ values
        sum = 0
        for card in self.cards:
            sum += self.bin_value(card[model.BIN_IDX])
            
        # rand in that range
        count = random.randint(0, sum - 1)
        
        # index into cards
        idx = 0
        bin_value = self.bin_value(self.cards[idx][model.BIN_IDX])
        while count - bin_value > 0:
            count -= bin_value
            idx += 1
            bin_value = self.bin_value(self.cards[idx][model.BIN_IDX])

        return self.cards[idx]

    def update_card(self, card, correct):
        if correct:
            new_bin = min(self.num_bins - 1,
                          card[model.BIN_IDX] + 1)
        else:
            new_bin = 0

        card[model.BIN_IDX] = new_bin
