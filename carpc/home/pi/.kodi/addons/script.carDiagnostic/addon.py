#
#      Original by Brian Wallen [bwallen@gmail.com]
# 	   Updated & Modified by Andreas [thix@gmx.net]
#
#  This Program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2, or (at your option)
#  any later version.
#
#  This Program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this Program; see the file LICENSE.txt.  If not, write to
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#  http://www.gnu.org/copyleft/gpl.html
#
import gui
import sys

xbmc.log("PYTHON VERSION IS " + str(sys.version_info))

try:
    w = gui.obd2()
    w.doModal()
    del w

except Exception as e:
    xbmc.log("[script.cardiagnostic] - Didn't even load the GUI - " + str(e))
