# pitacard: A Leitner-method flashcard program
# Copyright (C) 2006 Austin Bingham
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

from pysqlite2 import dbapi2 as sqlite
import gtk
import model

def get_connection(dbname):
    return sqlite.connect(dbname,
                          detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)

def table_exists(cursor, table_name):
    cursor.execute('select tbl_name from sqlite_master where tbl_name="%s"' % table_name)
    list_tables = cursor.fetchall()
    if len(list_tables) == 1: return True
    else: return False

def create_tables(cursor):
    if not table_exists(cursor, 'cards'):
        cursor.execute("""
        create table cards(
        bin int,
        front text,
        back text)
        """)

def save(filename, cards):
    conn = get_connection(filename)
    cursor = conn.cursor()
    create_tables(cursor)
    cursor.execute('delete from cards')

    for c in cards:
        cursor.execute('insert into cards values(?,?,?)',
                       (c[model.BIN_IDX],
                        c[model.FRONT_IDX],
                        c[model.BACK_IDX]))

    conn.commit()

def load(filename):
    conn = get_connection(filename)
    cursor = conn.cursor()
    rval = model.new_model()
    if table_exists(cursor, 'cards'):
        cursor.execute('select * from cards')
        for row in cursor.fetchall():
            rval.append([row[0], row[1], row[2]])

    return rval

