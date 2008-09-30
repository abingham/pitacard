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

from sqlite3 import dbapi2 as sqlite
import gtk
import model

#Below are the master field lists. If you change the treemodel's structure, these are the only things you need to edit for this file, the code will handle the rest (adding columns, etc.) but you MUST edit them accordingly.

profilefields = [
    #['fieldname', 'type', 'defaultvalue']
    ['name',         'text',    '\' \''],#A set of escaped quotations are included so that they show up for the SQL query, so its treated as a static string rather than a field to look for.
    ['cardnum',    'int',      '0'],
    ['cardtype_i',  'int',      '0'],
    ['cardtype_r',  'int',      '0'],
    ['cardtype_n', 'int',      '0'],
    ['select_sys',  'int',      '0'],
    ['sandbox',     'int',      '0'],
    ['renderhtml', 'int',      '0'],
    ['rvwlayout',    'int',      '0']
    ]

cardfields = [
    #['fieldname', 'type', 'defaultvalue']
    ['bin',      'int',   '0'       ],
    ['type',    'text', '\'I\''   ], #A set of escaped quotations are included so that they show up for the SQL query, so its treated as a static string rather than a field to look for.
    ['front',   'text', '\' \''   ],
    ['back',   'text', '\' \''   ]
    ]

def get_connection(dbname):
    return sqlite.connect(dbname,
                          detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)

def table_exists(cursor, table_name):
    cursor.execute('select tbl_name from sqlite_master where tbl_name="%s"' % table_name)
    list_tables = cursor.fetchall()
    if len(list_tables) == 1: return True
    else: return False

def create_tables(thecursor):

    if table_exists(thecursor, 'profiles'):
        thecursor.execute("drop table profiles")
    thecursor.execute("create table profiles(" + ', '.join([' '.join([x[0], x[1]]) for x in profilefields])  + ")")

    if table_exists(thecursor, 'cards'):
        thecursor.execute("drop table cards")
    thecursor.execute("create table cards(" + ', '.join([' '.join([x[0], x[1]]) for x in cardfields]) + ")")

def save(filename, cards, profiles):
    conn = get_connection(filename)
    thecursor = conn.cursor()
    create_tables(thecursor)

    for p in profiles:
        thecursor.execute('insert into profiles values(?,?,?,?,?,?,?,?,?)',
                       tuple([p[x] for x in range(0,len(profilefields))]))

    for c in cards:
        thecursor.execute('insert into cards values(?,?,?,?)',
                       tuple([c[x] for x in range(0,len(cardfields))]))

    conn.commit()

def load(filename):
    conn = get_connection(filename)
    thecursor = conn.cursor()
    rval = model.new_model()
    optval = model.new_profile_model()

    if table_exists(thecursor, 'profiles'):
        #Get the current table fields and where they go to.
        thecursor.execute("select * from profiles LIMIT 1")
        if thecursor.description == None:
            curfields = []
        else:
            curfields = [ x[0] for x in thecursor.description ] #find the columns in the table.
        for field in profilefields:    #for every field that should be in the table
            if field[0] in curfields:         #if its in the table as a column
                field[2] = field[0]   #we'll use that columns value. Otherwise the empty slate default for that column is used when loading the stack.

        #Get the data from the table
        thecursor.execute('SELECT ' + ', '.join([x[2] for x in profilefields ]) + ' FROM profiles')
        for row in thecursor.fetchall():
            optval.append(list(row))

    if table_exists(thecursor, 'cards'):
        #Get the current table fields and where they go to.
        thecursor.execute("select * from cards LIMIT 1")
        if thecursor.description == None:
            curfields = []
        else:
            curfields = [ x[0] for x in thecursor.description ] #find the columns in the table.
        for field in cardfields:    #for every field that should be in the table
            if field[0] in curfields:         #if its in the table as a column
                field[2] = field[0]   #we'll use that columns value. Otherwise the empty slate default for that column is used when loading the stack.

        #Get the data from the table
        thecursor.execute('SELECT ' + ', '.join([x[2] for x in cardfields ]) + ' FROM cards')
        for row in thecursor.fetchall():
            rval.append(list(row))
    return optval, rval
