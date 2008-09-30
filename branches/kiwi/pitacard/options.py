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

from string import lower
import gtk, gtk.glade
from model import *

def GetOpts(profmodel=False, borrowing=False):
    '''Gets the current in use options

       if borrowing == 'borrow', remove the line which has the current profile.
       Doing so is useful for displaying the list of options without showing the user this special exception profile and confusing them.
       As well as if you're editing the current options. Just remember to put it back, preferably as the first profile, when you're done.'''
    optdefaults = {
        NAME_PIDX : 'profile',
        CARDNUM_PIDX : 25,
        TYPE_I_PIDX : 1,
        TYPE_R_PIDX : 3,
        TYPE_N_PIDX : 1,
        SELECTSYS_PIDX : 0,
        SANDBOX_PIDX : 0,
        RENDERHTML_PIDX : 1,
        RVWLAYOUT_PIDX : 0
        }

    defaultprofile = []
    for i in optdefaults:
        '''makes a row with all the default values, except the name is __CURRENT__'''
        if i == NAME_PIDX:
            defaultprofile.append('CURRENT_')
        else:
            defaultprofile.append(optdefaults[i])

    currentprofile = 0

    try:
        profmodel[0]
    except NameError:
        '''If the profile model doesn't even exist, make it, and use the default options.'''
        profmodel = new_profile_model()
        currentprofile = defaultprofile
    except IndexError:
        '''if there are no profiles, use the default options.'''
        currentprofile = defaultprofile
    else:
        '''if there is a profile there, check them for the window and current profile, and if they're there, put them in front and accept no further ones. If they're not, create them from the default profile template.'''
        for i in profmodel:
            if i[0] == 'CURRENT_':
                currentprofile = i
                if borrowing == True:
                    del i                #haha, 'deli'? Get it? ... it's a joke... laugh...
                break
    if currentprofile == False:
        currentprofile = defaultprofile
    return currentprofile

class OptGUI:
    def __init__(self, parentwindow, gladefile, profmodel):
        self.gladefile = gladefile
        self.profmodel = profmodel				#create a link copy for variable scoping convenience.
        self.profcurr = new_profile_model()
        self.profcurr.insert(0, GetOpts(self.profmodel, True))	#this is the profile model changed whenever an option in the window is changed.
        self.profcurr.insert(1, self.profcurr[0])		#think of this as a backup of the original options, to be reinstituted if cancel is pressed.

        xml = gtk.glade.XML(self.gladefile, 'ReviewOptionsWindow')
        self.window = xml.get_widget('ReviewOptionsWindow')
        self.window.set_transient_for(parentwindow)

        self.create_gui_handles(xml)
        self.make_gui_connections()
        self.load_profile_into_gui()

    def create_gui_handles(self, xml):
        """Connect python objects to each Gobject of the window from which data must be received or which must be modified depending on data."""

        # BOTTOM-LEFT BUTTONS
        self.window.selectprofile = xml.get_widget('Options - SelectProfile')
        self.window.loadprofile = xml.get_widget('Options - ProfileLoad')
        self.window.saveprofile = xml.get_widget('Options - ProfileSave')
        self.window.favprofile = xml.get_widget('Options - ProfileMakeDefault')
        self.window.deleteprofile = xml.get_widget('Options - ProfileDelete')

        # SET BOTTOM-LEFT BUTTONS' INITIAL SENSITIVITY
        self.window.loadprofile.set_sensitive(False)
        self.window.favprofile.set_sensitive(False)
        self.window.deleteprofile.set_sensitive(False)

        # BOTTOM-RIGHT BUTTONS
        self.window.ok = xml.get_widget('Options - OK')
        self.window.cancel = xml.get_widget('Options - Cancel')

        # MAIN PAGE
        self.window.cardnum = xml.get_widget('Options - Cardnum - Spin Button')
        self.window.ctpi0 = xml.get_widget('Options - Card Types - Irreversable - Do Not Use')
        self.window.ctpi1 = xml.get_widget('Options - Card Types - Irreversable - Side1')
        self.window.ctpr0 = xml.get_widget('Options - Card Types - Reversable - Do not use')
        self.window.ctpr1 = xml.get_widget('Options - Card Types - Reversable - Side1')
        self.window.ctpr2 = xml.get_widget('Options - Card Types - Reversable - Side2')
        self.window.ctpr3 = xml.get_widget('Options - Card Types - Reversable - Both')
        self.window.ctpn0 = xml.get_widget('Options - Card Types - Notes - Do not use')
        self.window.ctpn1 = xml.get_widget('Options - Card Types - Notes - Show both immediately')
        
        self.window.selectsys0 = xml.get_widget('Options - SelectSys - Leitner')
        self.window.selectsys1 = xml.get_widget('Options - SelectSys - Random')
        
        self.window.sandbox = xml.get_widget('Options - SandboxMode - Button')
        
        self.window.renderhtml = xml.get_widget('Options - Appearance - Interpret HTML')
        self.window.rvwlayout = xml.get_widget('Options - Appearance - RvwLayout')

    def make_gui_connections(self):
        """Assign actions to take at certain signals from certain gObjects.

            Example: assigning the click of a radio button to a function that (with certain specified parameters) will change the value of the CURRENT_ profile accordingly."""

        #'Name this profile' field.
        self.window.selectprofile.set_model(self.profmodel)
        self.window.selectprofile.set_text_column(0)
        self.window.selectprofile.connect("changed", lambda w: self.test_profile_exists())

        #'Load this profile' button.
        self.window.loadprofile.connect("clicked", lambda w: self.loadprofile())

        #'Save this profile' button.
        self.window.saveprofile.connect("clicked", lambda w: self.saveprofile())

        #'Make this profile the default' button
        self.window.favprofile.connect("clicked", lambda w: self.makedefault())

        #'Delete this profile' button.
        self.window.deleteprofile.connect("clicked", lambda w: self.deleteprofile())

        #'ok' button
        self.window.ok.connect("clicked", lambda w: self.endbutton(True))

        #'cancel' button
        self.window.cancel.connect("clicked", lambda w: self.endbutton(False))

        #'How many cards?' spinner.
        self.window.cardnum.connect("value_changed", lambda w: self.modprofile(CARDNUM_PIDX, self.window.cardnum.get_value_as_int()))

        #'Irreversable Cards' options.
        self.window.ctpi0.connect("pressed", lambda w: self.modprofile(TYPE_I_PIDX, 0))
        self.window.ctpi1.connect("pressed", lambda w: self.modprofile(TYPE_I_PIDX, 1))

        #'Reversable Cards' options.
        self.window.ctpr0.connect("pressed", lambda w: self.modprofile(TYPE_R_PIDX, 0))
        self.window.ctpr1.connect("pressed", lambda w: self.modprofile(TYPE_R_PIDX, 1))
        self.window.ctpr2.connect("pressed", lambda w: self.modprofile(TYPE_R_PIDX, 2))
        self.window.ctpr3.connect("pressed", lambda w: self.modprofile(TYPE_R_PIDX, 3))

        #'Note Cards' options.
        self.window.ctpn0.connect("pressed", lambda w: self.modprofile(TYPE_N_PIDX, 0))
        self.window.ctpn1.connect("pressed", lambda w: self.modprofile(TYPE_N_PIDX, 1))

        #'Selection System' options.
        self.window.selectsys0.connect("pressed", lambda w: self.modprofile(SELECTSYS_PIDX, 0))
        self.window.selectsys1.connect("pressed", lambda w: self.modprofile(SELECTSYS_PIDX, 1))

        #'Sandbox Mode' check button
        self.window.sandbox.connect("toggled", lambda w: self.modprofile(SANDBOX_PIDX, self.window.sandbox.get_active()))
        
        #'Render HTML' check button.
        self.window.renderhtml.connect("toggled", lambda w: self.modprofile(RENDERHTML_PIDX, self.window.renderhtml.get_active()))

        #'Render HTML' check button.
        self.window.rvwlayout.connect("toggled", lambda w: self.modprofile(RVWLAYOUT_PIDX, self.window.rvwlayout.get_active()))

    def load_profile_into_gui(self):
        """Sync the values selected in the options window with the values which have been loaded into the CURRENT_ profile."""
        windowopts = self.profcurr[0]	# The creation of the windowopts variable is simply for shortening the name used to reference the option list that should be currently displayed in the window.
        if windowopts[CARDNUM_PIDX] < 0:	# If the cardnum value is a negative number, flip it to make it a positive one.
            windowopts[CARDNUM_PIDX] = (windowopts[CARDNUM_PIDX] * 1)
        self.window.cardnum.set_value(windowopts[CARDNUM_PIDX])	#Make the cardnum spinner reflect the CURRENT_ cardnum value, as loaded from the profile, or as already present from the default profile or last options edit.

        if not (windowopts[TYPE_I_PIDX] >= 0 and windowopts[TYPE_I_PIDX] <= 1):
            windowopts[TYPE_I_PIDX] = optdefaults[TYPE_I_PIDX]
        if windowopts[TYPE_I_PIDX] == 0:
            self.window.ctpi0.set_active(True)
        elif windowopts[TYPE_I_PIDX] == 1:
            self.window.ctpi1.set_active(True)

        if not (windowopts[TYPE_R_PIDX] >= 0 and windowopts[TYPE_R_PIDX] <= 3):
            windowopts[TYPE_R_PIDX] = optdefaults[TYPE_R_PIDX]
        if windowopts[TYPE_R_PIDX] == 0:
            self.window.ctpr0.set_active(True)
        elif windowopts[TYPE_R_PIDX] == 1:
            self.window.ctpr1.set_active(True)
        elif windowopts[TYPE_R_PIDX] == 2:
            self.window.ctpr2.set_active(True)
        elif windowopts[TYPE_R_PIDX] == 3:
            self.window.ctpr3.set_active(True)

        if not (windowopts[TYPE_N_PIDX] >= 0 and windowopts[TYPE_N_PIDX] <= 1):
            windowopts[TYPE_N_PIDX] = optdefaults[TYPE_N_PIDX]
        if windowopts[TYPE_N_PIDX] == 0:
            self.window.ctpn0.set_active(True)
        elif windowopts[TYPE_N_PIDX] == 1:
            self.window.ctpn1.set_active(True)
        
        if not (windowopts[SELECTSYS_PIDX] >= 0 and windowopts[SELECTSYS_PIDX] <= 1):
            windowopts[SELECTSYS_PIDX] = optdefaults[SELECTSYS_PIDX]
        if windowopts[SELECTSYS_PIDX] == 0:
            self.window.selectsys0.set_active(True)
        elif windowopts[TYPE_N_PIDX] == 1:
            self.window.selectsys1.set_active(True)

        if not (windowopts[SANDBOX_PIDX] >= 0 and windowopts[SANDBOX_PIDX] <= 1):
            windowopts[SANDBOX_PIDX] = optdefaults[SANDBOX_PIDX]
        if windowopts[SANDBOX_PIDX] == 0:
            self.window.sandbox.set_active(False)
        elif windowopts[SANDBOX_PIDX] == 1:
            self.window.sandbox.set_active(True)
            
        if not (windowopts[RENDERHTML_PIDX] >= 0 and windowopts[RENDERHTML_PIDX] <= 1):
            windowopts[RENDERHTML_PIDX] = optdefaults[RENDERHTML_PIDX]
        if windowopts[RENDERHTML_PIDX] == 0:
            self.window.renderhtml.set_active(False)
        elif windowopts[RENDERHTML_PIDX] == 1:
            self.window.renderhtml.set_active(True)

        if not (windowopts[RVWLAYOUT_PIDX] >= 0 and windowopts[RVWLAYOUT_PIDX] <= 1):
            windowopts[RVWLAYOUT_PIDX] = optdefaults[RVWLAYOUT_PIDX]
        if windowopts[RVWLAYOUT_PIDX] == 0:
            self.window.rvwlayout.set_active(False)
        elif windowopts[RVWLAYOUT_PIDX] == 1:
            self.window.rvwlayout.set_active(True)

    def modprofile(self, key, value):
        self.profcurr[0][key] = value

    def saveprofile(self):
        if self.window.selectprofile.get_active_text() == '':
            return
        namedprofile = self.test_profile_exists()	#look for a profile by that name
        if namedprofile == False:				#If there is no profile by that name, create a new  row with that name.
            newprofile = list(self.profcurr[0])
            newprofile[NAME_PIDX] = self.window.selectprofile.get_active_text()
            self.profmodel.append(newprofile)
        else:						#If a row object was returned by that name, change the values of that row object
            for i in range(0, len(namedprofile)):
                if i == NAME_PIDX:
                    namedprofile[i] = self.window.selectprofile.get_active_text()
            else:
                    namedprofile[i] = list(self.profcurr[0])[i]
        #Because the profile exists now, activate the profile load/default/delete buttons to compensate for new profiles who's status is not autodetected because they have just been changed, without the selectprofile field's text being changed.
        self.show_profile_ops(True)

    def loadprofile(self):
        namedprofile = self.test_profile_exists()
        clonedprofile = list(namedprofile)
        clonedprofile[NAME_PIDX] = 'CURRENT_'
        del self.profcurr[0]
        self.profcurr.insert(0, clonedprofile)
        self.load_profile_into_gui()

    def makedefault(self):
        print "Hockey"

    def deleteprofile(self):
        namedprofile = self.test_profile_exists()
        self.profmodel.remove(namedprofile.iter)
        self.show_profile_ops(False)

    def test_profile_exists(self):
        profilename = self.window.selectprofile.get_active_text()
        for i in self.profmodel:
            if lower(i[NAME_PIDX]) == lower(profilename):
                self.show_profile_ops(True)
                return i
                break
        else:
            self.show_profile_ops(False)
            return False

    def show_profile_ops(self, bool=True):
        self.window.loadprofile.set_sensitive(bool)
        self.window.favprofile.set_sensitive(bool)
        self.window.deleteprofile.set_sensitive(bool)

    def endbutton(self, keepchanges=True):
        if keepchanges==True:
            self.profcurr[1] = list(self.profcurr[0])
        self.profmodel.insert(0, self.profcurr[1])
        self.window.destroy()
        del self
