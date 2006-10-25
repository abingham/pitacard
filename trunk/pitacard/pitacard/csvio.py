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

import gtk, csv
import model

def save(filename, cards, profiles):
    writer = csv.writer(open(filename, "wb"))

    for p in profiles:
        a = ['profile']
        a.extend(p)
        writer.writerow(a)

    for c in cards:
        a = ['card']
        a.extend(c)
        writer.writerow(a)

def compatibilitysave(filename, cards):
    writer = csv.writer(open(filename, "wb"), delimiter='\t')

    for c in cards:
        cardrow = [ c[model.FRONT_CIDX], c[model.BACK_CIDX] ]
        writer.writerow(cardrow)

def load(filename):
    rvals = []
    optvals = []
    for givendelimiter in [',', '\t']:
        reader = csv.reader(open(filename, "rb"), delimiter=givendelimiter)
        rval = model.new_model()
        optval = model.new_profile_model()
        for row in reader:
            if row[0] == "profile" and len(row) >=9 :
                try:
                    optval.append([
                        str(row[1]),
                        int(row[2]),
                        int(row[3]),
                        int(row[4]),
                        int(row[5]),
                        int(row[6]),
                        int(row[7]),
                        int(row[8]),
                        int(row[9])])
                except:
                    print "could not load the following row:", row
            elif row[0] == "card" and len(row) >= 5 :
                try:
                    rval.append([
                        int(row[1]),
                        str(row[2]),
                        str(row[3]),
                        str(row[4])])
                except:
                    print "could not load the following row:", row
            elif len(row) == 2:
                try:
                    '''it's probably a compatibility mode .csv file or a .csv from some other program. assume the first column is the front of the card and the second column is the back of the card.'''
                    if row[0] != '' or row[1] != '':
                        rval.append([
                            0,
                            'I',
                            str(row[0]),
                            str(row[1])])
                except:
                    print "could not load the following row:", row
        rvals.append(rval)
        optvals.append(optval)

    # Find which csv delimiter produced the most rows. Rows were only
    # created if there was more than one column in them, which would
    # require the delimiter to be present. A csv file which had more
    # lines with tab is more likely to use tab as a delimiter, because
    # in a CSV file with more than one column (which are the kinds of
    # file we're loading), the delimiter should be present in each row.
    # Whereas even if, say, another possible delimiter such as a comma,
    # was present in a lot of the lines, it's most likely that a comma
    # isn't present in each line, and even if they are, there would
    # have to be a certain amount of commas in each for it to count as
    # a line. A mis-step is only likely at all if a file is saved in
    # compatibility mode with just a few cards that have been crafted
    # carefully to screw up the delimitation.'''
    rval_sizes = [len(x) for x in rvals]
    optval_sizes = [len(x) for x in optvals]
    rows_found = [ rval_sizes[x] + optval_sizes[x] for x in range(0, len(rval_sizes)) ]
    sortingstack = rows_found[:]
    sortingstack.sort()
    if sortingstack[-1] == sortingstack[-2]:
        rval = rvals[1]
        optval = optvals[1]
    else:
        rval = rvals[rows_found.index(sortingstack[-1])]
        optval = optvals[rows_found.index(sortingstack[-1])]

    return optval, rval
