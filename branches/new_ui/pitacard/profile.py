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

class Profile:
    RANDOM_METHOD = 0
    LEITNER_METHOD = 1

    FORWARD_MODE = 0
    REVERSE_MODE = 1
    RANDOM_MODE  = 2

    def __init__(self):
        self.selection_method = Profile.LEITNER_METHOD
        self.sandbox = False
        self.render_html = False
        self.review_mode = Profile.FORWARD_MODE
