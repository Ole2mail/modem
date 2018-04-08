'''
Created on 1 Apr 2018

@author: ole2
'''

from __future__ import print_function

import serial
import time
import threading
import const
from enum import Enum

class hayes(serial.Serial):
    '''
    classdocs
    in Dennis Hayes protocol if the answer is immediate
    timeout for unknown but possible arriving next character
    would depend on single character current speed delivery 
    and proposed for 50 times delay for single character
    also, extra time will require modem itself to "think" about: 
    
    0.01 sec + 1.0 sec / baud rate (bits per second) * 10.0 bits (per character) * 50.0 times
    example for 2400 baud rate:
    0.01 + 1.0 / 2400 * 10.0 * 50.0 ~ 0.010004 sec
    the constants are adjusted for python based code
    '''

    const.MAX_BITS_PER_CHAR = 10.0
    const.PROPOSED_TIMES = 50.0
    # 0.1 sec works for all speed except 300 and 600 baud require 0.03
    const.THINKING_TIME = 0.01
    
    const.HayesWelcome = "AT"
    const.HayesCmdEnds = '\r'
    const.HayesWelcomeCmd = const.HayesWelcome + const.HayesCmdEnds

    statesLine = Enum("statesLine", "NONE CONNECT RING NOCARRIER BUSY LINEINUSE NODIALTONE")     
    HayesLineResponses = {
        "CONNECT":statesLine.CONNECT, "RING":statesLine.RING, "NO CARRIER":statesLine.NOCARRIER, 
        "BUSY":statesLine.BUSY, "LINE IN USE":statesLine.LINEINUSE, "NO DIALTONE":statesLine.NODIALTONE
        }
    
    statesCMD = Enum("statesCMD", "NONE OK ERROR")
    HayesCMDResponses = {"OK":statesCMD.OK, "ERROR":statesCMD.ERROR}
        
    # command/line events discovery thread based loop
    # TODO: consider limiting incoming buffer max size
    def _readCMDStateLoop(self):
        while self.alive == True:
            quantity = super(hayes, self).in_waiting 
            if quantity == 0:
                if self.modemReceiving == True:
                    self.modemReceiving = False
                else:
                    # read_timeout is depends on port speed and
                    # is estimated on port opening moment
                    time.sleep(self.read_timeout) 
#                     print('s', end='')
            else:
                self.modemReceiving = True
                self.incoming += super(hayes, self).read(quantity)
#                 print('i', end='')
        
    def __init__(self, *args, **kwargs):
        '''
        Constructor
        '''
    
        self.stateCMD = self.statesCMD.NONE
        self.stateLine = self.statesLine.NONE
        self.read_timeout = 0
        self.incoming = ""
        # setting mode full buffer for receiving thread activation
        self.modemReceiving = True
    
        super(hayes, self).__init__(*args, **kwargs)
        
    def open(self):
        # opening port before reading
        serial.Serial.open(self)
        self.read_timeout = const.THINKING_TIME + 1.0 * const.MAX_BITS_PER_CHAR * const.PROPOSED_TIMES / super(hayes, self).baudrate 
        # start reading thread
        self.alive = True
        self.rxThread = threading.Thread(target=self._readCMDStateLoop)
        self.rxThread.daemon = True
        self.rxThread.start()
        # waiting for receiving thread starts
        while self.modemReceiving == True:
            # read_timeout is depends on port speed and
            # is estimated on port opening moment
            time.sleep(self.read_timeout) 

    def close(self):
        # stop reading thread
        self.alive = False
        self.rxThread.join()
        serial.Serial.close(self)
        
    def read(self): 
        intermediate = ""   
        while True:
            if self.modemReceiving == False and len(self.incoming) > 0:
                intermediate = self.incoming
                self.incoming = ""
#                 print('r', end='')
                break
            else:
                # read_timeout is depends on port speed and
                # is estimated on port opening moment
                time.sleep(self.read_timeout/2)                     
#                 print('S', end='')
        # response parsing section
        stateCMDList = [self.statesCMD.NONE]
        stateCMDList.extend([v for k,v in self.HayesCMDResponses.items() if k in intermediate])
        # extracting last answer if the series happened
        self.stateCMD = stateCMDList[-1]
        stateLineList = [self.statesLine.NONE]
        stateLineList.extend([v for k,v in self.HayesLineResponses.items() if k in intermediate])
        # extracting last answer if the series happened
        self.stateLine = stateLineList[-1]
        return intermediate
    
    # should work for most of the Hayes dialog cases
    # TODO: might require support for \r\n tails 
    # TODO: implement verification on mixed/lower cases: "at", "At", "aT"
    # TODO: implement special cases like: "+++" or "$", "A", "A/"
    def writeCMD(self, command=const.HayesWelcomeCmd):
        if not command.startswith(const.HayesWelcome):
            command = const.HayesWelcome + command
        if not command.endswith(const.HayesCmdEnds):
            command += const.HayesCmdEnds
        while self.modemReceiving == True:
            # blocking next command sending before the answer on previous been replied
            # otherwise there is potential risk the modem will interrupt previous command execution
            time.sleep(self.read_timeout)
        super(hayes, self).write(command)
    
    def readAnswer(self, command=const.HayesWelcomeCmd):
        self.writeCMD(command)
        return self.read()

    # readAnswerDelayed method reserved only for substantial delayed answers
    # like: ATD, ATA, ATO, ATZ, +++, etc.
    # don't stick with this method, git a try writeCMD first
    def writeCMDDelayed(self, command=const.HayesWelcomeCmd, timeout=1):    
        self.writeCMD(command)
        time.sleep(timeout)
        
    # readAnswerDelayed method reserved only for substantial delayed answers
    # like: ATD, ATA, ATO, +++, etc.
    # don't stick with this method, git a try readAnswer first
    def readAnswerDelayed(self, command=const.HayesWelcomeCmd, timeout=1):
        self.writeCMDDelayed(command)
        time.sleep(timeout)
        return self.read()
    
    