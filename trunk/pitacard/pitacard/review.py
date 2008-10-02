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

#For report generation.
from __future__ import division
import md5
from time import time

#For other purposes.
from math import *
import random, gtk, gtk.glade, commands, webbrowser, logging
import htmltextview
import model

logger = logging.getLogger('pitacard.review')

class Review:
    def __init__(self, parentwindow, gladefile, cfg, cards_unsorted, profile, bins=10):
        
        assert len(cards_unsorted) > 0, 'No cards in deck supplier to Leitner review'
        self.cards_unsorted = cards_unsorted
        self.profile = profile
        self.config = cfg
        self.num_bins = bins
        
        # self.session is used to collect statistics about the current session. These statistics are displayed at the bottom of the window (cardnum) and in a collected report form. 'CARDHASHES' is a set which is used to count the number of unique cards used in a session. A card is md5 hex-hashed and added to the set. If the hash already exists in the set, nothing is added. That way the set increases by 1 for every _different_ card. 'STARTTIME' is obviously used to record timing. Later the time function is used again, and subtraction used to tell the difference.
        self.session = {'CARDNUM': 0, 'CARDHASHES': set(), 'CORRECT': 0, 'WRONG': 0, 'STARTTIME': time()}

        # assign handles
        xml = gtk.glade.XML(gladefile, 'ReviewWindow')
        self.window = xml.get_widget('ReviewWindow')
        self.window.set_transient_for(parentwindow)

        self.window.connect("delete_event", self.delete_event)
        self.makepanes(xml)
        self.next_button = xml.get_widget('next_button')
        self.correct_button = xml.get_widget('correct_button')
        self.wrong_button = xml.get_widget('wrong_button')
        self.statustext = xml.get_widget('Review - CurrCardnum')
        if self.profile[model.CARDNUM_PIDX] == 0:
            self.statustext.set_label('Reviewed: ' + str(self.session['CARDNUM']) + '\nLeft: ' + str('infinite'))
        else:
            self.statustext.set_label('Reviewed: ' + str(self.session['CARDNUM']) + '\nLeft: ' + str(self.profile[model.CARDNUM_PIDX] - self.session['CARDNUM']))


        if self.config.getboolean('startup', 'preservegeom'):
            self.window.resize(self.config.getint('appearance', 'rvwlastwidth'),
                               self.config.getint('appearance', 'rvwlastheight'))
            self.window.move(self.config.getint('appearance', 'rvwlastposx'),
                             self.config.getint('appearance', 'rvwlastposy'))
        else:
            self.window.resize(500, 500)
            self.window.move(480, 140)

        xml.signal_autoconnect({
            'on_show_button_clicked' :
            lambda x: self.show_answer(),
            'on_correct_button_clicked' :
            lambda x: self.answered(True),
            'on_wrong_button_clicked' :
            lambda x: self.answered(False),
            'on_end_review_clicked' :
            lambda x: self.delete_event()
            })

        #Sift through cards. Create new list linking to used ones.
        self.siftcards()

        if len(self.cards) < 1:
            logger.warning("no cards found.")
            #If there are no cards, yet the user opened the review window (possible if the user has only cards in their deck of a type that they've set not to use in options) nothing happens. Buttons don't work. Empty fields. That's all. I feel that telling the user why no cards show up would be superfluous.
            self.sensitize_buttons(False, False, False)
        else:
            # If there are cards in the card pool, initialize view to first card
            self.show_next_card()

    def makepanes(self, xml):
        vbox = xml.get_widget('review-viewboxes')
        labelhbox = xml.get_widget('review-toplabelbox')


        
        #Question box
        question_scroller = gtk.ScrolledWindow()
        question_scroller.set_shadow_type(gtk.SHADOW_IN)
        question_scroller.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        #Answer box
        answer_scroller = gtk.ScrolledWindow()
        answer_scroller.set_shadow_type(gtk.SHADOW_IN)
        answer_scroller.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        
        if self.profile[model.RENDERHTML_PIDX] == 1:
            #If we're rendering the cards HTML
            self.question_block = htmltextview.HtmlTextView()
            self.question_block.connect("url-clicked", self.url_cb)
            self.answer_block = htmltextview.HtmlTextView()
            self.answer_block.connect("url-clicked", self.url_cb)
        else:
            #If we're not rendering html
            self.question_block = gtk.TextView()
            self.question_block.set_wrap_mode(gtk.WRAP_WORD)
            self.answer_block = gtk.TextView()
            self.answer_block.set_wrap_mode(gtk.WRAP_WORD)
        question_scroller.add(self.question_block) #add the created view/textboxes.
        answer_scroller.add(self.answer_block)

        backlabel = gtk.Label("Back")	#We will position the word 'back' so it's put right next to the pane which actually displays the answer.
        backlabel.set_padding(15, 0)
        if self.profile[model.RVWLAYOUT_PIDX] == 0:
            #If we have Q and A hoz. to eachother
            paned = gtk.HPaned()
            labelhbox.pack_end(backlabel, False, False)
        else:
            #If we have Qbox on top of A
            paned = gtk.VPaned()
            vbox.pack_end(backlabel, False, False)
            backlabel.set_alignment(0.0, 0.5)
        backlabel.show()

        #Putting the scrollers into the panes, pack the panes.
        paned.pack1(question_scroller, True, False)
        paned.pack2(answer_scroller, True, False)
        paned.set_border_width(5)
        vbox.pack_start(paned)

        #show the pane and its scrollers and their textviews
        self.question_block.show()
        self.answer_block.show()
        question_scroller.show()
        answer_scroller.show()
        paned.show()

    def siftcards(self):
        siftedcards = []
        card_usequery = {}
        deckpos = 0
        def passer(*args):
            pass
        def userow(siftedcards, deckpos, cardrow):
            siftedcards.insert(deckpos, cardrow)
            deckpos += 1
        if self.profile[model.TYPE_I_PIDX] == 0:
            card_usequery['I'] = passer
        elif self.profile[model.TYPE_I_PIDX] > 0:
            card_usequery['I'] = userow
        if self.profile[model.TYPE_R_PIDX] == 0:
            card_usequery['R'] = passer
        elif self.profile[model.TYPE_R_PIDX] > 0:
            card_usequery['R'] = userow
        if self.profile[model.TYPE_N_PIDX] == 0:
            card_usequery['N'] = passer
        elif self.profile[model.TYPE_N_PIDX]  > 0:
            card_usequery['N'] = userow

        for i in self.cards_unsorted:
            if i[model.TYPE_CIDX] in model.cardtypes: #this is used solely so if the type has been screwed up through a change in a csv file, the app doesn't sweat it.
                card_usequery[i[model.TYPE_CIDX]](siftedcards, deckpos, i)
        self.cards = siftedcards

    def url_cb(view, object, url, event):
        '''handles the clicking of a link within an html-rendered textview'''
        webbrowser.open_new(url)

    def end_review(self):
        '''quits the review'''
        self.window.destroy()
        del self
    
    def displaytext(self, viewer, text):
        if self.profile[model.RENDERHTML_PIDX] == 1:
            viewer.display_html_replace("""
            <body xmlns='http://www.w3.org/1999/xhtml'>
            """ + str(text) + """
            </body>
                """)
        else:
            viewer.get_buffer().set_text(text)

    def answered(self, correct):
        self.update_card(self.curr_card, correct)
        
        #hash the card and deposit in a hash set. Later this set is used to determine how many of the reviewed cards were unique.
        hasher = md5.new()
        hasher.update(self.curr_card[model.FRONT_CIDX])
        hasher.update(self.curr_card[model.BACK_CIDX])
        hasher.update(self.curr_card[model.TYPE_CIDX])
        self.session['CARDHASHES'].add(hasher.hexdigest())
        
        self.session['CARDNUM'] += 1
        if self.profile[model.CARDNUM_PIDX] == 0:
            self.statustext.set_label('Reviewed: ' + str(self.session['CARDNUM']) + '\nLeft: ' + str('infinite'))
        else:
            self.statustext.set_label('Reviewed: ' + str(self.session['CARDNUM']) + '\nLeft: ' + str(self.profile[model.CARDNUM_PIDX] - self.session['CARDNUM']))

        if int(self.session['CARDNUM']) == int(self.profile[model.CARDNUM_PIDX]) and self.profile[model.CARDNUM_PIDX] != 0:
            self.generate_report()
        else:
            self.show_next_card()

    def show_answer(self):
        if self.questionside == 1:
            self.displaytext(self.answer_block, self.curr_card[model.BACK_CIDX])
        elif self.questionside == 2:
            self.displaytext(self.answer_block, self.curr_card[model.FRONT_CIDX])
        self.sensitize_buttons(False, True, True)
        
    def show_next_card(self):
        
        #CARD SELECTION METHOD
        if self.profile[model.SELECTSYS_PIDX] == 0:
            self.curr_card = self.get_next_card_leitner()
        elif self.profile[model.SELECTSYS_PIDX] == 1:
            self.curr_card = self.get_next_card_random()
        
        #CARD DISPLAYING METHOD
        if self.curr_card[model.TYPE_CIDX] == "I":
            # If this is a card with a question for the first side and an answer for the second side.
            if self.profile[model.TYPE_I_PIDX] == 1:
                questionformat=True
                self.questionside=1
        elif self.curr_card[model.TYPE_CIDX] == "R":
            questionformat=True
            if self.profile[model.TYPE_R_PIDX] == 1 or self.profile[model.TYPE_R_PIDX] == 2:
                self.questionside = self.profile[model.TYPE_R_PIDX]
            elif self.profile[model.TYPE_R_PIDX] == 3:
                self.questionside = random.randint(1,2)
        elif self.curr_card[model.TYPE_CIDX] == "N":
            #if this is a card without a question or answer, but instead both sides are immediately shown.
            if self.profile[model.TYPE_N_PIDX] == 1:
                questionformat=False
                self.questionside=1
        else:
            logger.error("Card type not recognized! Treating as an irreversible card.")
            questionformat=True
            self.questionside=1

        if self.questionside==1:
            self.displaytext(self.question_block, self.curr_card[model.FRONT_CIDX])
        elif self.questionside==2:
            self.displaytext(self.question_block, self.curr_card[model.BACK_CIDX])

        if questionformat==True:
            self.displaytext(self.answer_block, '')
            self.sensitize_buttons(True, False, False)
        else:
            self.displaytext(self.answer_block, self.curr_card[model.BACK_CIDX])
            self.sensitize_buttons(False, True, True)

    def sensitize_buttons(self, next=False, correct=False, wrong=False):
        self.correct_button.set_sensitive(correct)
        self.wrong_button.set_sensitive(wrong)
        self.next_button.set_sensitive(next)

    def have_cards(self):
        return len(self.cards) > 0

    def bin_value(self, bin):
        assert bin in range(self.num_bins), 'bin %d not in range (0,%d)' % (bin,self.num_bins)
        inv = self.num_bins - bin
        return 2**inv   #causes cards with a lower bin to be exponentially higher than those with a higher bin.

    def get_next_card_leitner(self):
        # count total bin number of all cards
        sum = 0
        for card in self.cards:
            sum += self.bin_value(card[model.BIN_CIDX])
            
        # rand in that total bin number
        count = random.randint(0, sum - 1)
        
        # index into cards
        idx = 0
        bin_value = self.bin_value(self.cards[idx][model.BIN_CIDX])
        while count - bin_value > 0:
            count -= bin_value
            idx += 1
            bin_value = self.bin_value(self.cards[idx][model.BIN_CIDX])
        return self.cards[idx]

    def get_next_card_random(self):
        # count cards w/ values
        idx = random.randint(0, (len(self.cards) - 1))
        return self.cards[idx]

    def update_card(self, card, correct):
        if correct:
            self.session['CORRECT'] += 1
            if self.profile[model.SANDBOX_PIDX] == 0:
                new_bin = min(self.num_bins - 1, card[model.BIN_CIDX] + 1)
        else:
            self.session['WRONG'] += 1
            if self.profile[model.SANDBOX_PIDX] == 0:
                new_bin = 0

        card[model.BIN_CIDX] = new_bin

    def generate_report(self):

        self.sensitize_buttons(False, False, False)
        self.displaytext(self.question_block, 'Review done. Generating report...')
        self.displaytext(self.answer_block, '')

        '''Fills the question window with a report of statistics gathered during the review session. Strings are added to the report list one by one and then the entire list is joined into a giant entry in the buffer.'''
        report = []

        report.append("-------------------")
        report.append("REPORT CARD")
        report.append("-------------------")
        report.append("")

        #CARD REPORT
        report.append("CARDS STUDIED:")
        report.append("You reviewed " + str(self.session['CARDNUM']) + " cards.")
        report.append("You answered " + str(self.session['CORRECT']) + " correctly. (" + str(self.session['CORRECT'] * 100 / self.session['CARDNUM'])[:4] + "%)")
        report.append("You answered " + str(self.session['CARDNUM'] - self.session['CORRECT']) + " incorrectly. (" + str((self.session['CARDNUM'] - self.session['CORRECT']) * 100 / self.session['CARDNUM'])[:4] + "%)")
        if len(self.session['CARDHASHES']) == 1:
            report.append("1 unique card was reviewed. The remaining " + str(len(self.session['CARDHASHES']) * 100 / self.session['CARDNUM'])[:4] + "%), the rest were repeats.")
        else:
            report.append( str(len(self.session['CARDHASHES'])) + " unique cards were reviewed. The remaining " + str(self.session['CARDNUM'] - len(self.session['CARDHASHES'])) + " were repeats")
        if len(self.cards) < len(self.cards_unsorted) and (self.profile[model.TYPE_I_PIDX] == 0 or self.profile[model.TYPE_R_PIDX] == 0 or self.profile[model.TYPE_N_PIDX]) == 0:
            bannedcards = []
            if self.profile[model.TYPE_I_PIDX] == 0:
                bannedcards.append("irreversable")
            if self.profile[model.TYPE_R_PIDX] == 0:
                bannedcards.append("reversable")
            if self.profile[model.TYPE_N_PIDX] == 0:
                bannedcards.append("notes")
            report.append("That means you've reviewed " + str(len(self.session['CARDHASHES']) * 100 / len(self.cards))[:4] + "% of pool of " + str(len(self.cards)) + " cards")
            report.append("You only reviewed out of a pool of " + str(len(self.cards)) + " cards, drawn from a stack of " + str(len(self.cards_unsorted)) + " cards, because you have decided not to view the following kinds of cards: " + ', '.join(bannedcards) + ".")
        else:
            report.append("That means you've reviewed " + str(len(self.session['CARDHASHES']) * 100 / len(self.cards))[:4] + "% of all your " + str(len(self.cards)) + " cards")
        report.append(" ")

        #TIME REPORT
        timediff = time() - self.session['STARTTIME']
        extension = ""
        if timediff >= 86400:
            extension = extension + str(int(timediff/ 86400))
            if  int(timediff/ 86400) == 1:
                        extension = extension + " day, "
            else:
                    extension = extension + " daus, "
        if int(timediff/ 3600 % 24) != 0:
                #exclude hours if sessiontime equals zero (whether that's from it being less than an hour or from it being within an hour past of an integer amount of days). If we wanted to allows include hours if the session took any amount longer than an hour, we'd use the same 'if' format that we do with days.
                extension = extension + str(int(timediff/ 3600 % 24))
                if int(timediff / 3600 % 24) == 1:
                        extension = extension + " hour, "
                else:
                        extension = extension + " hours, "
        if int(timediff / 60 % 60) != 0:
                #exclude minutes if sessiontime equals zero (whether that's from it being less than a minute or from it being within a 60 seconds past of an integer amount of hours). If we wanted to allows include minutes if the session took anywhere longer than a minute, we'd use the same 'if' format that we do with days.
                extension = extension + str(int(timediff/ 60 % 60))
                if int(timediff / 60 % 60) == 1:
                        extension = extension + " minute, "
                else:
                        extension = extension + " minutes, "
        if extension != "":
            #If more than the unit of seconds is being displayed...
            extension = extension + "and "
        report.append("SESSION TIME:")
        report.append("You've been studying for " + extension + str(int(timediff % 60)) + " seconds.")
        
        if self.profile[model.RENDERHTML_PIDX] == 1:
            self.displaytext(self.question_block, str("<br/> ".join(report)))
        else:
            self.displaytext(self.question_block, str("\n ".join(report)))
    
    def delete_event(self, object=None, event=None):
        width, height = self.window.get_size()
        posx, posy = self.window.get_position()
        self.config.set('appearance', 'rvwlastwidth', str(width))
        self.config.set('appearance', 'rvwlastheight', str(height))
        self.config.set('appearance', 'rvwlastposx', str(posx))
        self.config.set('appearance', 'rvwlastposy', str(posy))
        self.end_review()
