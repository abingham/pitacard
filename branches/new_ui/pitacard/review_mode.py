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

import random
import leitner, model, util

class ReviewMode:
    cNumBins = 10

    def __init__(self, parent):
        self.parent = parent
        self.curr_card = None

        parent.xml.signal_autoconnect({
                'on_review_show_button_clicked' :
                    lambda x: self._show_answer(),
                'on_review_correct_button_clicked' :
                    lambda x: self._answered(True),
                'on_review_incorrect_button_clicked' :
                    lambda x: self._answered(False),
                #'on_review_done_button_clicked' :
                    #    lambda x: self.done
                })

        util.link_widgets(self.parent.xml,
                          self,
                          ['front_text_view',
                           'back_text_view',
                           ('review_show_button',      'show_button'),
                           ('review_correct_button',   'correct_button'),
                           ('review_incorrect_button', 'incorrect_button'),
                           ('review_correct_menu',     'correct_menu'),
                           ('review_incorrect_menu',   'incorrect_menu'),
                           ('review_show_menu',        'show_menu'),
                           ('review_done_menu',        'done_menu')
                           ])

    def start_review(self):
        self._show_next_card()

    def _show_answer(self):
        assert len(self.parent.card_list.get_model()) > 0
        self.back_text_view.get_buffer().set_text(self.curr_card[model.BACK_CIDX])

        self.show_button.set_sensitive(False)
        self.show_menu.set_sensitive(False)
        self.correct_button.set_sensitive(True)
        self.correct_menu.set_sensitive(True)
        self.incorrect_button.set_sensitive(True)
        self.incorrect_menu.set_sensitive(True)

    def _answered(self, correct):
        # TODO: Build up success stats

        assert not self.curr_card is None

        if correct:
            self.curr_card[model.BIN_CIDX] = min(ReviewMode.cNumBins - 1,
                                                 self.curr_card[model.BIN_CIDX] + 1)
        else:
            self.curr_card[model.BIN_CIDX] = 0

        self._show_next_card()

    def _show_next_card(self):
        if len(self.parent.card_list.get_model()) == 0:
            return

        self.curr_card = self._get_next_card()
        self.front_text_view.get_buffer().set_text(self.curr_card[model.FRONT_CIDX])
        self.back_text_view.get_buffer().set_text('')

        self.show_button.set_sensitive(True)
        self.show_menu.set_sensitive(True)
        self.correct_button.set_sensitive(False)
        self.correct_menu.set_sensitive(False)
        self.incorrect_button.set_sensitive(False)
        self.incorrect_menu.set_sensitive(False)

    def _get_next_card(self):
        cards = self.parent.card_list.get_model()
        assert len(cards) > 0
        return cards[leitner.next_card_index(cards, ReviewMode.cNumBins)]
        
