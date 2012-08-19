#!/usr/bin/env python
"""
.. module:: IvolutionWindow
   :platform: Unix, Windows, Mac
   :synopsis: Main Window of the Ivolution GUI designed to be supported by all platforms.

.. moduleauthor:: Julien Lengrand-Lambert <jlengrand@gmail.com>

"""

import wx
import os
import logging

from AboutDialog import AboutDialog


class IvolutionWindow(wx.Frame):
    """
    Main Window of the Ivolution application
    """
    def __init__(self, parent, title):
        """
        Overrides init frame wx.Frame
        """
        wx.Frame.__init__(self, parent, title=title, size=(200, 100))

        # Sets up logging capability
        self.my_logger = None
        self.console_logger = None
        self.setup_logger()

        #self.control = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        #self.CreateStatusBar()  # A Statusbar in the bottom of the window

        # Creating the main grid
        self.maingrid = self.setup_maingrid()

        # Creating the menubar.
        self.menubar = self.setup_menubar()

        # Creating the status bar
        # self.statusbar = self.setup_statusbar()

    # GUI set up

    def setup_maingrid(self):
        """
        Defines the main grid that will be used as layout in the window.
        """
        maingrid = wx.FlexGridSizer(4, 1, vgap=0, hgap=0)
        return maingrid



    # def setup_statusbar(self):
    #     """
    #     Sets up all elements of the status bar
    #     """

    def setup_filemenu(self):
        """
        Sets up all elements of the file menu
        """
        file_menu = wx.Menu()

        # Sets up the About menu item
        menuAbout = file_menu.Append(wx.ID_ABOUT, "About", " Information about this program")
        self.Bind(wx.EVT_MENU, self.on_about, menuAbout)

        file_menu.AppendSeparator()

        # Sets up the Exit menu item
        menuExit = file_menu.Append(wx.ID_EXIT, "Exit", " Terminate the program")
        self.Bind(wx.EVT_MENU, self.on_exit, menuExit)

        return file_menu

    def setup_menubar(self):
        """
        """
        # Creating the menubar.
        menuBar = wx.MenuBar()

        filemenu = self.setup_filemenu()

        menuBar.Append(filemenu, "&File")  # Adding the "filemenu" to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.
        self.Show(True)
        return menuBar

    # Events Handling
    def on_about(self, event):
        """
        Displays the about box for Ivolution
        TODO : Create the About Window
        """
        about = AboutDialog(self, "Ivolution")
        about.ShowModal()  # Show it
        about.Destroy()  # finally destroy it when finished.
        # A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
        # dlg = wx.MessageDialog(self, "Ivolution", "About Ivolution", wx.OK)
        # dlg.ShowModal()  # Show it
        # dlg.Destroy()  # finally destroy it when finished.
        print "About !"

    def on_exit(self, event):
        """
        Called when the IvolutionWindow is closed, or File/Exit is called.
        """
        self.Close(True)  # Close the frame.

    def setup_logger(self):
        """
        Configures our logger to save error messages
        Start logging in file here
        """
        personal_dir = "~/.ivolution"
        log_root = 'fm.log'
        log_file = os.path.join(os.path.expanduser(personal_dir), log_root)

        # create logger for  'facemovie'
        self.my_logger = logging.getLogger('FileLog')

        self.my_logger.setLevel(logging.DEBUG)
        # create file handler which logs even debug messages

        #fh = logging.StreamHandler()
        fh = logging.FileHandler(log_file)

        fh.setLevel(logging.DEBUG)
        # create console handler with a higher log level
        self.console_logger = logging.getLogger('ConsoleLog')
        self.console_logger.setLevel(logging.DEBUG)  # not needed

        ch = logging.StreamHandler()
        #ch.setLevel(logging.DEBUG) # not needed

        # add the handlers to the logger
        self.my_logger.addHandler(fh)

        self.my_logger.info("######")  # Separating different sessions

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # create formatter and add it to the handlers
        fh.setFormatter(formatter)
        #ch.setFormatter(formatter)

        self.console_logger.addHandler(ch)

if __name__ == "__main__":
    app = wx.App(False)
    frame = IvolutionWindow(None, "Ivolution Window")
    app.MainLoop()  # Runs application