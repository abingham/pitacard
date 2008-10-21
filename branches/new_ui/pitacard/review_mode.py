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

import datetime, random
import leitner, model, util

class Settings:
    '''
    settings that apply to all reviews. These are referred to
    in all reviews, and generally control the behavior of
    the review.
    '''
    def __init__(self,
                 max_count = None,
                 max_time = None):
        self.max_count = max_count
        self.max_time = max_time # minutes
        # TODO: Permitted bins

class Session:
    '''
    This represents a per-review set of data. It basically tracks
    review statistics, elapsed time, and other data that needs
    to be reset for each review.
    '''
    def __init__(self, settings):
        self.settings = settings
        self.total = 0
        self.correct = 0
        self.start_time = 0
        self.stats_displayed = False

    def _elapsed_time(self):
        return datetime.datetime.now() - self.start_time

    def _is_finished(self):
        if not self.max_count is None:
            if self.total >= self.max_count:
                return True

        if not self.max_time is None:
            if self.elapsed_time >= datetime.timedelta(minutes=self.max_time):
                return True

    def reset(self):
        self.total = 0
        self.correct = 0
        self.start_time = datetime.datetime.now()
        self.stats_displayed = False

    def answered(self, correct):
        self.total += 1
        if correct:
            self.correct += 1

    max_count = property(lambda s: s.settings.max_count)
    max_time = property(lambda s: s.settings.max_time)
    finished = property(_is_finished)
    elapsed_time = property(_elapsed_time)

    
class ReviewMode:
    cNumBins = 10

    def __init__(self, parent):
        self.parent = parent
        self.curr_card = None

        self.settings = Settings()
        self.session = Session(self.settings)

        parent.xml.signal_autoconnect({
                'on_review_show_button_clicked' :
                    lambda x: self._show_answer(),
                'on_review_correct_button_clicked' :
                    lambda x: self._answered(True),
                'on_review_incorrect_button_clicked' :
                    lambda x: self._answered(False),
                'on_review_done_button_clicked' :
                    lambda x: self._handle_done(),
                'on_review_done_menu_activate':
                    lambda x: self._handle_done(),
                })

        util.link_widgets(self.parent.xml,
                          self,
                          ['front_text_view',
                           'back_text_view',
                           'review_frame',
                           'review_toolbar',
                           'mainmenu_review',
                           ('review_show_button',      'show_button'),
                           ('review_correct_button',   'correct_button'),
                           ('review_incorrect_button', 'incorrect_button'),
                           ('review_correct_menu',     'correct_menu'),
                           ('review_incorrect_menu',   'incorrect_menu'),
                           ('review_show_menu',        'show_menu'),
                           ('review_done_menu',        'done_menu')
                           ])

    def enter_mode(self):
        self.review_frame.show()
        self.review_toolbar.show()
        self.mainmenu_review.show()

    def exit_mode(self):
        self.review_frame.hide()
        self.review_toolbar.hide()
        self.mainmenu_review.hide()

    def start_review(self):
        self.session.reset()
        self._show_next_card()

    def _handle_done(self):
        if not self.session.stats_displayed:
            self._show_stats()
        else:
            self.parent.enter_edit_mode()

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
        assert not self.session is None
        assert not self.curr_card is None

        self.session.answered(correct)

        if correct:
            self.curr_card[model.BIN_CIDX] = min(ReviewMode.cNumBins - 1,
                                                 self.curr_card[model.BIN_CIDX] + 1)
        else:
            self.curr_card[model.BIN_CIDX] = 0

        if self.session.finished:
            self._show_stats()
        else:
            self._show_next_card()

    def _show_stats(self):
        assert not self.session is None
        
        self.show_button.set_sensitive(False)
        self.show_menu.set_sensitive(False)
        self.correct_button.set_sensitive(False)
        self.correct_menu.set_sensitive(False)
        self.incorrect_button.set_sensitive(False)
        self.incorrect_menu.set_sensitive(False)

        self.back_text_view.get_buffer().set_text('')

        if self.session.total == 0:
            perc_correct = 100
        else:
            perc_correct = self.session.correct / self.session.total * 100

        self.front_text_view.get_buffer().set_text('''Total answered: %s
Total correct: %s
Percent correct: %s 
Study time: %s
''' % (self.session.total, 
       self.session.correct, 
       perc_correct,
       self.session.elapsed_time.seconds / 60.0))

        self.session.stats_displayed = True

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
        
