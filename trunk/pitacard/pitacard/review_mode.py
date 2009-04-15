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

import gtk
import datetime, random
import pitacard.leitner, pitacard.model, pitacard.util

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

        pitacard.util.link_widgets(self.parent.xml,
                                   self,
                                   ['front_text_view',
                                    'back_text_view',
                                    'review_frame',
                                    'review_toolbar',
                                    'mainmenu_review',
                                    ])

        self.init_actions()
        self.init_menu()
        self.init_toolbar()

    def init_actions(self):
        self.action_group = gtk.ActionGroup('review_mode_action_group')

        actions = []
        actions.append(('show_action',
                        'show_action',
                        'Show',
                        'Show next card',
                        gtk.STOCK_OK,
                        's',
                        lambda x: self._show_answer()))
        actions.append(('correct_action',
                        'correct_action',
                        'Correct',
                        'Answer was correct',
                        gtk.STOCK_APPLY,
                        'c',
                        lambda x: self._answered(True)))
        actions.append(('incorrect_action',
                        'incorrect_action',
                        'Incorrect',
                        'Answer was incorrect',
                        gtk.STOCK_CANCEL,
                        'i',
                        lambda x: self._answered(False)))
        actions.append(('done_action',
                        'done_action',
                        'Done',
                        'End current review session',
                        gtk.STOCK_CLOSE,
                        'd',
                        lambda x: self._handle_done()))

        for action in actions:
            a = gtk.Action(action[1],
                           action[2],
                           action[3],
                           action[4])
            setattr(self, action[0], a)
            self.action_group.add_action_with_accel(a, action[5])
            a.set_accel_group(self.parent.accel_group)
            a.connect_accelerator()
            a.connect('activate', action[6])

    def init_menu(self):
        m = self.mainmenu_review.get_submenu()
        m.append(self.show_action.create_menu_item())
        m.append(self.correct_action.create_menu_item())
        m.append(self.incorrect_action.create_menu_item())
        m.append(self.done_action.create_menu_item())

    def init_toolbar(self):
        t = self.review_toolbar
        t.insert(self.show_action.create_tool_item(), -1)
        t.insert(self.correct_action.create_tool_item(), -1)
        t.insert(self.incorrect_action.create_tool_item(), -1)
        t.insert(gtk.SeparatorToolItem(), -1)
        t.insert(self.done_action.create_tool_item(), -1)

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
        self.back_text_view.get_buffer().set_text(self.curr_card[pitacard.model.BACK_CIDX])

        self.show_action.set_sensitive(False)
        self.correct_action.set_sensitive(True)
        self.incorrect_action.set_sensitive(True)

    def _answered(self, correct):
        assert not self.session is None
        assert not self.curr_card is None

        self.session.answered(correct)

        if correct:
            self.curr_card[pitacard.model.BIN_CIDX] = min(ReviewMode.cNumBins - 1,
                                                 self.curr_card[pitacard.model.BIN_CIDX] + 1)
        else:
            self.curr_card[pitacard.model.BIN_CIDX] = 0

        if self.session.finished:
            self._show_stats()
        else:
            self._show_next_card()

    def _show_stats(self):
        assert not self.session is None
        
        self.show_action.set_sensitive(False)
        self.correct_action.set_sensitive(False)
        self.incorrect_action.set_sensitive(False)

        self.back_text_view.get_buffer().set_text('')

        if self.session.total == 0:
            perc_correct = 100
        else:
            perc_correct = float(self.session.correct) / self.session.total * 100

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
        self.front_text_view.get_buffer().set_text(self.curr_card[pitacard.model.FRONT_CIDX])
        self.back_text_view.get_buffer().set_text('')

        self.show_action.set_sensitive(True)
        self.correct_action.set_sensitive(False)
        self.incorrect_action.set_sensitive(False)

    def _get_next_card(self):
        cards = self.parent.card_list.get_model()
        assert len(cards) > 0
        return cards[pitacard.leitner.next_card_index(cards, ReviewMode.cNumBins)]
        
