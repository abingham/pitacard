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

from pysqlite2 import dbapi2 as sqlite

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
