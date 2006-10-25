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
from os import access

def cant_access(checkpath, accesstype=4, parent=None, custom_message=None):
    '''Can be used to check if a file exists or check a file's permissions for a specific kind of access and giving an error message if not.
       Access kind can be given in text or Posix number variant.
       This is solely for creating errormessages.
       Testing that is only required for code should use the much more economical os.access alone.

       returns TRUE if that path cannot be accessed in that way. Returns FALSE if the path can be accessed in that way.'''

    accesslist = [
        'exists',
        'execute',
        'write',
        'write-execute',
        'read',
        'read-execute',
        'read-write',
        'full'
    ]


    if type(accesstype) == type('str'):
        #convert the string to its number equivalent
        try:
            accesstype = accesslist.index(lower(accesstype))
        except:
           try:
                accesstype = int(accesstype)
           except:
               print "error! Permissions keyword " + accesstype + " not valid!"

    try:
        accesslist[accesstype]
    except:
        print "error! Permissions number not valid! Single digit integer from 0-7 only!"

    if access(checkpath, accesstype):
        return False
    else:
        if custom_message != None:
                errormessage = custom_message
        elif accesstype == 0:
            '''if this function is being used to test if a file exists:'''
            errormessage = str("Error! " + checkpath + " does not exist!")
        else:
            '''if this function is being used to test if a file exists, but rather, check its permissions:'''
            errormessage = str("Error: You do not have " + accesslist[accesstype] + " access to " + checkpath)

        if parent != 'stdout':
            couldnotwrite = gtk.MessageDialog(None,
                                                False,
                                                gtk.MESSAGE_ERROR,
                                                gtk.BUTTONS_CLOSE,
                                                errormessage)
            couldnotwrite.set_transient_for(parent)
            couldnotwrite.run()
            couldnotwrite.destroy()
        else:
            print errormessage

        return True
