import subprocess
import re
import time
import sys

import threading

from PyQt4.QtGui import QApplication
from PyQt4.QtCore import QUrl
from PyQt4.QtWebKit import *
from PyQt4 import QtGui, QtCore

POWER_MGMT_RE = re.compile(r'IOPowerManagement.*{(.*)}')

def display_status():
    output = subprocess.check_output(
        'ioreg -w 0 -c IODisplayWrangler -r IODisplayWrangler'.split())
    status = POWER_MGMT_RE.search(output).group(1)
    return dict((k[1:-1], v) for (k, v) in (x.split('=') for x in
                                            status.split(',')))

class StatusCheck( QtCore.QThread ):

    def __init__(self , qtapp):

        QtCore.QThread.__init__(self)

        self.qtapp = qtapp

    def run( self  ):

        self._time = 2

        while True:

            status = display_status()['CurrentPowerState']
            status = int( status )

            if status < 3:

                print 'Screen is off!'

                url = "html/index.html?status=1&time=" + str( self._time * 60 )
                print "url is now", url

                self.qtapp.emit( QtCore.SIGNAL("aa"), url )

                break ## stop loop, for demo only

            else:

                self._time += 1
                url = "html/index.html?status=0&time=" + str( self._time * 60 )
                print "url is now", url

                self.qtapp.emit( QtCore.SIGNAL("aa"), url )

            time.sleep( 10 )

            print "Looping"

class EnergyApp( QtGui.QWidget ):

    def __init__(self):
        super( EnergyApp , self).__init__()


        url = "html/index.html?status=0&time=" + str( 120 )

        self.web = QWebView()
        self.web.load( QUrl( url ) )

        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)

        hbox.addWidget( self.web )

        self.setLayout( hbox )

        self.setGeometry(500, 300, 500, 400 )
        self.setWindowTitle('Energy reminder')
        self.show()

        QtCore.QObject.connect( self, QtCore.SIGNAL("aa"), self.update )

    def update( self, url ):

        print "Loading", url

        self.web.load( QUrl( url ) )

app = QApplication(sys.argv)
view = EnergyApp()

status = StatusCheck( view )
status.start()

sys.exit(app.exec_())
