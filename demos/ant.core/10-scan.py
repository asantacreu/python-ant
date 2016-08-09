"""
Extending on demo-04, re-implements the event callbackso we can parse the results of the scan.

"""

import sys
import time

from ant.core import driver
from ant.core import node
from ant.core import event
from ant.core import message
from ant.core.constants import *

from config import *

NETKEY = '\xB9\xA5\x21\xFB\xBD\x72\xC3\x45'

# A run-the-mill event listener
class ScanListener(event.EventCallback):
    def process(self, msg):
        if isinstance(msg, message.ChannelBroadcastDataMessage):
            if len(msg.payload) > 9:
                flagByte = ord(msg.payload[9])
                if flagByte == 0x80:
                    deviceNumberLSB = ord(msg.payload[10])
                    deviceNumberMSB	= ord(msg.payload[11])
                    deviceNumber = "{}".format(deviceNumberLSB + (deviceNumberMSB<<8))

                    deviceType = "{}".format(ord(msg.payload[12]))

                    print 'New Device Found: %s of type %s' % (deviceNumber,deviceType)

# Initialize
stick = driver.USB1Driver(SERIAL, log=LOG, debug=DEBUG)
antnode = node.Node(stick)
antnode.start()

# Setup channel
key = node.NetworkKey('N:ANT+', NETKEY)
antnode.setNetworkKey(0, key)
channel = antnode.getFreeChannel()
channel.name = 'C:HRM'
channel.assign('N:ANT+', CHANNEL_TYPE_TWOWAY_RECEIVE,0x01)
channel.setID(120, 0, 0)
channel.enableExtendedMessages(0x01)
channel.setSearchTimeout(TIMEOUT_NEVER)
channel.setPeriod(8070)
channel.setFrequency(57)
channel.open()

# Setup callback
# Note: We could also register an event listener for non-channel events by
# calling registerEventListener() on antnode rather than channel.
channel.registerCallback(ScanListener())

# Wait
print "Listening for HR monitor events (120 seconds)..."
time.sleep(120)

# Shutdown
channel.close()
channel.unassign()
antnode.stop()
