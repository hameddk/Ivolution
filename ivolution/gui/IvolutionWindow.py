#!/usr/bin/env python
"""
.. module:: IvolutionWindow
   :platform: Unix, Windows, Mac
   :synopsis: Main Window of the Ivolution GUI designed to be supported by all platforms.

.. moduleauthor:: Julien Lengrand-Lambert <jlengrand@gmail.com>

"""

import wx
import wx.lib.newevent

import sys
import os
import logging
import webbrowser

from .. import get_data # used to load images and files

from .. import FaceParams
from .. import FacemovieThread

from ..util.Notifier import Observer
from ..util.Notifier import Observable

from IvolutionTemplate import IvolutionTemplate
from SettingsWindow import SettingsWindow


class IvolutionWindow(IvolutionTemplate, Observer, Observable):
    """
    Main Window of the Ivolution application
    """
    def __init__(self, parent, title):
        """
        Overrides init frame IvolutionTemplate
        """
        IvolutionTemplate.__init__(self, parent)
        Observer.__init__(self, "Interface")
        Observable.__init__(self)

        self.home_dir = os.path.expanduser("~")  # Defines home directory

        # Sets up logging capability
        self.my_logger = None
        #self.console_logger = None
        self.setup_logger()

        # Defines all our parameters neededfor the facemovie
        self.get_default_parameters()

        self.process_running = False
        self.facemovie = None

        img_fo = os.path.join(self.root_fo, get_data("media"))

        self.inputtextbox.SetLabel(self.in_fo)  # sets label to default input folder
        self.SetIcon(wx.Icon(os.path.join(img_fo, 'vitruve.ico'), wx.BITMAP_TYPE_ICO))  # Sets icon

        self.Show(True)  # Finally shows the frame

    def get_default_parameters(self):
        """
        """
        self.videospeedlistChoices = [u"slow", u"medium", u"fast"]
        self.gaugerange = 100
        self.root_fo = ""

        self.mode = "crop"  # type of video to be created
        self.sort = "name"  # how image files will be chronologically sorted
        self.speed = 1  # Speed of the movie
        self.param = "frontal_face"  # type of face profile to be searched for

        self.out_fo = os.path.join(self.home_dir, "Videos")  # default output folder
        self.in_fo = os.path.join(self.home_dir, "Pictures")  # default input folder

    # Overriding event handling methods
    def on_settings(self, event):
        settings = SettingsWindow(self)
        settings.Show(True)  # Finally show the frame

    def on_start(self, event):
        """
        User asks for starting the algorithm
        Sets all parameters and start processing
        """
        self.my_logger.debug("start pressed")

        if not self.process_running:  # start only if not already running
            # Empty list on screen
            self.filelist.DeleteAllItems()

            self.set_parameters()
            self.log_parameters()
            # Instantiating the facemovie
            self.facemovie = FacemovieThread.FacemovieThread(self.face_params)
            self.facemovie.subscribe(self)  # I want new information ! Subscribes to facemovie reports
            self.subscribe(self.facemovie)  # Subscribing facemovie to our messages

            self.facemovie.start()

            self.process_running = True
        else:
            #self.console_logger.error("Cannot start, process already running !")
            self.my_logger.error("Cannot start, process already running !")

    def on_stop(self, event):
        """
        User asks for stopping the algorithm
        Asks the FacemovieThread to terminate
        """
        self.my_logger.debug("Stop pressed")
        #self.console_logger.debug("Stop pressed")
        self.notify(["Application", ["STOP"]])  # Asking the Facemovie to stop
        self.process_running = False

        #self.on_exit(event) # Finally shuts down the interface

    def on_input(self, event):
        """
        Activated when a user clicks to choose its input location
        """
        self.inputdialog = wx.DirDialog(self, "Please choose your input directory", style=1, defaultPath=self.in_fo)

        if self.inputdialog.ShowModal() == wx.ID_OK:
            self.in_fo = self.inputdialog.GetPath()
            self.inputtextbox.SetLabel(self.in_fo)
        self.inputdialog.Destroy()

    def on_help(self, event):
        """
        Opens a browser and points to online help.
        """
        url = "http://jlengrand.github.com/FaceMovie/"
        webbrowser.open(url, new=2)  # in new tab if possible

    def on_about(self, event):
        """
        Displays the about box for Ivolution
        """
        description = """    Ivolution is a project aiming at helping you create videos of yourself over time.
Simply take pictures of yourself, Ivolution does everything else for you.

    Ivolution may be used for faces, but also profiles (to show women along pregnancy)
or full body (for people workouting).

    The only limitation comes from you !

Please not that Ivolution is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY.
"""

        licence = """Copyright (c) <2012>, <Julien Lengrand-Lambert>
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those
of the authors and should not be interpreted as representing official policies,
either expressed or implied, of the FreeBSD Project."""

        info = wx.AboutDialogInfo()

        img_fo = os.path.join("", get_data("media"))
        info.SetIcon(wx.Icon(os.path.join(img_fo, '441px-Da_Vinci_Vitruve_Luc_Viatour.jpg'), wx.BITMAP_TYPE_JPEG))
        info.SetName('Ivolution')
        info.SetVersion('0.6')
        info.SetDescription(description)
        info.SetCopyright('(C) 2012 Julien Lengrand-Lambert')
        info.SetWebSite('http://www.lengrand.fr')
        info.SetLicence(licence)
        info.AddDeveloper('Julien Lengrand-Lambert')
        info.AddDocWriter('Julien Lengrand-Lambert')
        info.AddArtist('Luc Viatour')
        info.AddTranslator('Julien Lengrand-Lambert')

        wx.AboutBox(info)

    def on_exit(self, event):
        """
        Called when the IvolutionWindow is closed, or File/Exit is called.
        """
        # Clean up code for saving application state should be added here.
        self.my_logger.debug("Exit pressed")

        if self.process_running == False:
            sys.exit(0)
        else:
            # shows dialog asking to stop first.
            dial = wx.MessageDialog(None, """Cannot exit while processing! Please press stop first.""",
                'Exclamation',
                wx.OK | wx.ICON_EXCLAMATION)
            dial.ShowModal()

    # system methods
    def get_current_mode(self):
        """
        """
        if self.cropmode.GetValue():
            mode = "crop"
        else:
            mode = "conservative"

        return mode

    def get_current_sort(self):
        """
        """
        if self.namemode.GetValue():
            sort = "name"
        else:
            sort = "exif"

        return sort

    def set_parameters(self):
        """
        Retrieves all parameters needed for the algorithm to run
        """
        # Instantiating the face_params object that will be needed by the facemovie
        self.out_fo += "/"
        par_fo = os.path.join(self.root_fo, get_data("haarcascades"))
        self.face_params = FaceParams.FaceParams(par_fo,
                                                 self.in_fo,
                                                 self.out_fo,
                                                 self.param,
                                                 self.sort,
                                                 self.mode,
                                                 self.speed)

    def log_parameters(self):
        self.my_logger.debug("#########")
        self.my_logger.debug("Settings:")
        self.my_logger.debug("input folder :   %s" % (self.in_fo))
        self.my_logger.debug("output folder :   %s" % (self.out_fo))

        self.my_logger.debug("Face Type :   %s" % (self.param))
        self.my_logger.debug("Speed chosen :   %s" % (self.speed))
        self.my_logger.debug("Mode chosen :   %s" % (self.mode))
        self.my_logger.debug("Sort method :   %s" % (self.sort))
        self.my_logger.debug("#########")

    def setup_logger(self):
        """
        Configures our logger to save error messages
        Start logging in file here
        """
        personal_dir = os.path.join(self.home_dir, ".ivolution")
        log_root = 'ivolution.log'
        log_file = os.path.join(os.path.expanduser(personal_dir), log_root)

        # create logger for  'facemovie'
        self.my_logger = logging.getLogger('IvolutionFile')

        self.my_logger.setLevel(logging.DEBUG)
        # create file handler which logs even debug messages

        #fh = logging.StreamHandler() #  uncomment here for console output
        fh = logging.FileHandler(log_file)

        fh.setLevel(logging.DEBUG)
        # create console handler with a higher log level
        #self.console_logger = logging.getLogger('ConsoleLog')
        #self.console_logger.setLevel(logging.DEBUG)  # not needed

        #ch = logging.StreamHandler()
        #ch.setLevel(logging.DEBUG) # not needed

        # add the handlers to the logger
        self.my_logger.addHandler(fh)

        self.my_logger.info("######")  # Separating different sessions

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # create formatter and add it to the handlers
        fh.setFormatter(formatter)
        #ch.setFormatter(formatter)

        #self.console_logger.addHandler(ch)

    def update(self, message):
        """
        Trigerred by FacemovieThread.
        Uses the Observer pattern to inform the user about the progress of the current job.
        """
        if len(message) == 3:
            # notifications
            ##self.console_logger.debug(message)
            self.my_logger.debug(message)

            if message[0] == "PROGRESS":  # progress bar
                # big steps performed
                wx.MutexGuiEnter()  # to avoid thread problems
                self.progressgauge.SetValue(self.gaugerange * float(message[2]))
                self.statusbar.SetStatusText(message[1], 0)
                wx.MutexGuiLeave()

                if float(message[2]) >= 1.0:  # 100% of process
                    self.my_logger.debug("Reached end of facemovie process")
                    ##self.console_logger.debug("Reached end of facemovie process")
                    self.process_running = False

            elif message[0] == "STATUS":  # status label
                if message[1] == "Error":
                    wx.MutexGuiEnter()  # to avoid thread problems
                    self.statusbar.SetStatusText("Error detected", 0)
                    self.progressgauge.SetValue(0)
                    wx.MutexGuiLeave()
                    self.process_running = False

                wx.MutexGuiEnter()  # to avoid thread problems
                self.statusbar.SetStatusText(message[1], 1)
                wx.MutexGuiLeave()
            elif message[0] == "FILEADD":
                item = wx.ListItem()
                item.SetText(message[1])
                wx.MutexGuiEnter()  # to avoid thread problems
                self.filelist.InsertItem(item)
                wx.MutexGuiLeave()
            elif message[0] == "FILEDONE":
                for i in range(self.filelist.GetItemCount()):
                    if message[1] == self.filelist.GetItemText(i):
                        if message[2] == 1:
                            color = "green"
                        else:
                            color = "red"
                        wx.MutexGuiEnter()  # to avoid thread problems
                        self.filelist.SetItemTextColour(i, color)
                        wx.MutexGuiLeave()

        elif len(message) > 1:  # system commands shall be ignored
            #self.console_logger.debug("Unrecognized command")
            self.my_logger.debug("Unrecognized command")
            #self.console_logger.debug(message)
            self.my_logger.debug(message)
