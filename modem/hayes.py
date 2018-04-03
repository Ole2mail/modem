'''
Created on 1 Apr 2018

@author: ole2
'''

import serial
import time
import const
from enum import Enum

class hayes(serial.Serial):
    '''
    classdocs
    in Dennis Hayes protocol if the answer is immediate
    timeout for unknown but possible arriving next character
    would depend on single character current speed delivery 
    and proposed for 10 times delay for single character
    also, extra time will require modem itself to "think" about: 
    
    0.1 sec + 1.0 sec / baud rate (bits per second) * 10.0 bits (per character) * 10.0 times
    example for 2400 baud rate:
    0.1 + 1.0 / 2400 * 10.0 * 10.0 ~ 0.14 sec
    the constants are adjusted for python based code
    '''

    const.MAX_BITS_PER_CHAR = 10.0
    const.PROPOSED_TIMES = 10.0
    # 0.1 sec works for all speed except 300 and 600 baud require 0.4
    const.THINKING_TIME = 0.1
    
    const.HayesWelcome = "AT"
    const.HayesCmdEnds = '\r'
    const.HayesWelcomeCmd = const.HayesWelcome + const.HayesCmdEnds

    responseLine = Enum("responseLine", "NONE CONNECT RING NOCARRIER BUSY")     
    HayesLineResponses = {"CONNECT":responseLine.CONNECT, 
                                "RING":responseLine.RING, "NO CARRIER":responseLine.NOCARRIER, 
                                "BUSY":responseLine.BUSY}
    
    responseCMD = Enum("responseCMD", "NONE OK ERROR")
    HayesCMDResponses = {"OK":responseCMD.OK, "ERROR":responseCMD.ERROR}
        
    def __init__(self, *args, **kwargs):
        '''
        Constructor
        '''
    
        self.read_timeout = 0
    
        super(hayes, self).__init__(*args, **kwargs)
        
    def open(self):
        serial.Serial.open(self)
        self.read_timeout = const.THINKING_TIME + 1.0 * const.MAX_BITS_PER_CHAR * const.PROPOSED_TIMES / super(hayes, self).baudrate 
        
    def read(self):    
        intermediate = ""
        quantity = super(hayes, self).in_waiting 
        while True:
            if quantity > 0:
                intermediate += super(hayes, self).read(quantity)
            else:
                # read_timeout is depends on port speed and
                # is estimated on port opening moment
                time.sleep(self.read_timeout) 
            quantity = super(hayes, self).in_waiting
            if quantity == 0:
                break
        # response parsing section
        stateCMDList = [self.responseCMD.NONE]
        stateCMDList.extend([v for k,v in self.HayesCMDResponses.items() if k in intermediate])
        # extracting last answer if the series happened
        self.stateCMD = stateCMDList[-1]
        stateLineList = [self.responseLine.NONE]
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
        super(hayes, self).write(command)
    
    def readAnswer(self, command=const.HayesWelcomeCmd):
        self.writeCMD(command)
        return self.read()

    # TODO: might require support for \r\n tails 
    # TODO: implement verification on mixed/lower cases: "at", "At", "aT"
    # TODO: implement special cases like: "+++" or "$", "A", "A/"
    def writeCMDDelayed(self, command=const.HayesWelcomeCmd, timeout=1):    
        if not command.startswith(const.HayesWelcome):
            command = const.HayesWelcomeCmd + command
        if not command.endswith(const.HayesCmdEnds):
            command += const.HayesCmdEnds
        super(hayes, self).write(command)
        time.sleep(timeout)
        
    # readAnswerDelayed method reserved only for substantial delayed answers
    # like: ATD, ATA, ATO, +++, etc.
    # don't stick with this method, git a try readAnswer first
    def readAnswerDelayed(self, command=const.HayesWelcomeCmd, timeout=1):
        self.writeCMDDelayed(command)
        time.sleep(timeout)
        return self.read()
    
    