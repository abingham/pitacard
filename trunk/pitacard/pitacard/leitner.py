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
        
        self.bins = [ [] for idx in range(bins) ]
        for card in cards:
            self.bins[card[model.BIN_IDX]].append(card)

        xml = gtk.glade.XML(gladefile, 'ReviewDlg')
        self.dlg = xml.get_widget('ReviewDlg')
        self.next_button = xml.get_widget('next_button')
        self.correct_button = xml.get_widget('correct_button')
        self.wrong_button = xml.get_widget('wrong_button')
        self.front_text = xml.get_widget('front_text')
        self.back_text = xml.get_widget('back_text')

        if len(cards) < 1: self.next_button.set_sensitive(False)
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
        for bin in self.bins:
            if len(bin) > 0: return True
        return False

    def get_next_card(self):
        assert self.have_cards(), 'No cards available'
        
        bin = self.get_bin()
        assert bin < len(self.bins), 'Bin out of range'
        while len(self.bins[bin]) < 1:
            bin = self.get_bin()
        assert len(self.bins[bin]) > 0, 'Bin has no cards'
        
        card_idx = random.randint(0, len(self.bins[bin]) - 1)
        return self.bins[bin][card_idx]

    def update_card(self, card, correct):
        old_bin = card[model.BIN_IDX]
        if correct:
            new_bin = old_bin + 1
        else:
            new_bin = 0

        if new_bin >= len(self.bins):
            new_bin = len(self.bins) - 1
        
        self.bins[old_bin].remove(card)
        card[model.BIN_IDX] = new_bin
        self.bins[new_bin].append(card)

class Leitner_log2(Leitner):
    def __init__(self, gladefile, model, bins=10):
        Leitner.__init__(self, gladefile, model, bins)

    def get_bin(self):
        """
        This calculates a new bin using a log2
        scale. That is, the likelihood that a bin
        will be chosen is equal to the sum of the likelihoods
        for higher-numbered bins.
        """
        num_bins = len(self.bins)
        inv = floor(log(random.randint(1,2**num_bins - 1),
                       2))
        bin = (num_bins - 1) - inv
        return int(bin)


               
