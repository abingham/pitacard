# pitacard: A Leitner-method flashcard program
# Copyright (C) 2006-2008 Austin Bingham
#
# This program is free software you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation either version 2
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

import random
import pitacard.model

def _bin_value(bin, num_bins):
    assert bin in range(num_bins), 'bin %d not in range (0,%d)' % (bin, num_bins)
    inv = num_bins - bin
    return 2**inv   #causes cards with a lower bin to be exponentially higher than those with a higher bin.

def next_card_index(cards, num_bins):
    if len(cards) < 1:
        return -1

    # count total bin number of all cards
    sum = 0
    for card in cards:
        sum += _bin_value(card[pitacard.model.BIN_CIDX], num_bins)
            
    # rand in that total bin number
    count = random.randint(0, sum - 1)
        
    # index into cards
    idx = 0
    bin_value = _bin_value(cards[idx][pitacard.model.BIN_CIDX], num_bins)
    while count - bin_value > 0:
        count -= bin_value
        idx += 1
        bin_value = _bin_value(cards[idx][pitacard.model.BIN_CIDX], num_bins)

    assert idx < len(cards)
    return idx
