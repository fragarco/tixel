#!/usr/bin/env python
"""
Tixel - Sprite Editor for Amstrad CPC.

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation in its version 3.

This program is distributed in the hope that it will be useful
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
"""

import views
import controllers


class TixelApp:
    """
    The application object owns the main view and the controller that
    binds it to the data model.
    """
    view: views.TixelView
    controller: controllers.TixelController

    def __init__(self) -> None:
        self.view = views.TixelView()
        self.controller = controllers.TixelController(self.view)

    def mainloop(self) -> None:
        self.view.mainloop()


if __name__ == "__main__":
    TixelApp().mainloop()
