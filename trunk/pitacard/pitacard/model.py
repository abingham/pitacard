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

import gtk

BIN_CIDX = 2
TYPE_CIDX = 3
FRONT_CIDX = 0
BACK_CIDX = 1

cardtypes = [ 'I', 'R', 'N' ]   #This list is used for two functions: to translate the string that is actually put into the ListStore for type into a position on a combobox, and to be a list of the different values put into the type ListStore for the purpose of shortening card sifting functions (such as the one in 'Review').

def new_model():
    return gtk.ListStore(str, # front
                         str, # back
                         int, # bin
			 str) # type

NAME_PIDX = 0		#name
CARDNUM_PIDX = 1	#cardnum.
TYPE_I_PIDX = 2 	#options for irreversable cards.
TYPE_R_PIDX = 3 	#options for reversable cards.
TYPE_N_PIDX = 4 	#options for notes. 
SELECTSYS_PIDX = 5      #options as to whether use leitner method or random method. Leitner: Cards in a lower bin are exponentially more likely to be reviewed than those in a higher bin. Random: Bin doesn't matter. Cards are picked randomly. In both modes, bin # is affected by answer. Random just doesn't make use of it.
SANDBOX_PIDX = 6
RENDERHTML_PIDX = 7 	#whether to render the text as HTML or not.
RVWLAYOUT_PIDX = 8      #which way the review boxes should be set up.

def new_profile_model():
    return gtk.ListStore(str, #NAME
                         int, #CARDNUM
			 int, #CARDTYPE_I
			 int, #CARDTYPE_R
			 int, #CARDTYPE_N
                         int, #SELECTSYS
                         int, #SANDBOX
			 int, #RENDERHTML
                         int) #RVWLAYOUT
