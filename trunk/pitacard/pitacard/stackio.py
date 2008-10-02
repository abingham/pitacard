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
import logging
import model, profile

logger = logging.getLogger('pitacard.stackio')

#Below are the master field lists. If you change the treemodel's structure, these are the only things you need to edit for this file, the code will handle the rest (adding columns, etc.) but you MUST edit them accordingly.

format_fields = [
    ['file_version', 'int']
    ]

profile_fields = [
    #['fieldname', 'type']
    ['selection_method', 'int'],
    ['sandbox',          'int'],
    ['render_html',      'int'],
    ['review_mode',      'int']
    ]

card_fields = [
    # ['fieldname', 'type']
    ['front', 'text'],
    ['back',  'text'],
    ['bin',   'int'],
    ['type',  'text']    
    ]

def get_connection(dbname):
    return sqlite.connect(dbname,
                          detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)

def table_exists(cursor, table_name):
    cursor.execute('select tbl_name from sqlite_master where tbl_name="%s"' % table_name)
    list_tables = cursor.fetchall()
    if len(list_tables) == 1: return True
    else: return False

def create_table(cursor, name, fields, recreate=True):
    if recreate and table_exists(cursor, name):
        cursor.execute('drop table %s' % name)
    cursor.execute('create table %s(' % name + ', '.join(['%s %s' % (f[0], f[1]) for f in fields])  + ")")

def create_tables(cursor):
    create_table(cursor, 'format', format_fields)
    create_table(cursor, 'profile', profile_fields)
    create_table(cursor, 'cards', card_fields)

def save(filename, cards, profile):
    conn = get_connection(filename)
    thecursor = conn.cursor()
    create_tables(thecursor)

    thecursor.execute('insert into format values(?)', ('0'))

    thecursor.execute('insert into profile values(?,?,?,?)',
                      (profile.selection_method,
                       int(profile.sandbox),
                       int(profile.render_html),
                       int(profile.review_mode)
                      ))

    for c in cards:
        thecursor.execute('insert into cards values(?,?,?,?)',
                       tuple([c[x] for x in range(0,len(card_fields))]))

    conn.commit()

class NoSuchTableError:
    pass
class NoSuchValueError:
    pass

def read_field(table, field, conn, default=None):
    cursor = conn.cursor()

    if not table_exists(cursor, table):
        if not default is None:
            return default
        raise NoSuchTableError

    try:
        cursor.execute('select %s from %s LIMIT 1' % (field, table))
    except sqlite.OperationalError:
        if not default is None:
            return default

    row = cursor.fetchone()
    if not row or len(row) != 1:
        if not default is None:
            return default
        raise NoSuchValueError
    return row[0]

def load(filename):
    '''
    returns profile, model
    '''
    conn = get_connection(filename)

    mdl = model.new_model()
    pfl = profile.Profile()

    # read file format info
    try:
        version = read_field('format', 'file_version', conn)
        logger.info('File version for %s: %d' % (filename, version))
    except NoSuchTableError:
        logger.warning('No format information exists in file %s.' % filename)
    except NoSuchValueError:
        logger.error('Invalid format info for %s' % filename)

    # read profile info
    if not table_exists(conn.cursor(), 'profile'):
        logger.warning('No profile information exists i nfile %s' % filename)
    else:
        pfl.selection_method = int(read_field('profile', 'selection_method', conn,
                                              pfl.selection_method))
        pfl.sandbox = bool(read_field('profile', 'sandbox', conn,
                                      pfl.sandbox))
        pfl.render_html = bool(read_field('profile', 'render_html', conn,
                                          pfl.render_html))
        pfl.review_mode = int(read_field('profile', 'review_mode', conn,
                                         pfl.review_mode))

    # read cards
    cursor = conn.cursor()
    if table_exists(cursor, 'cards'):
        cursor.execute('select ' + 
                       ','.join([f[0] for f in card_fields]) +
                       ' from cards')
        for row in cursor.fetchall():
            mdl.append(list(row))

    return pfl, mdl
