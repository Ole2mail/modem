'''
Created on 31 Mar 2018

@author: ole2
'''

from modem.hayes import hayes
from modem.si24xx import si24xx

import time

def simpleDialogWithModem():
    port = hayes('/dev/ttyUSB0')
    port.write("AT\r")
    
    answer = port.read()
    print answer
    
    port.close()
    
def simpleAnswerFromModem():
    port = hayes('/dev/ttyUSB0', baudrate=230400) #115200)
    
    answer = port.readAnswer("ATi6")
    print answer
#     print port.stateCMDList
    print port.stateCMD
    print port.stateLine
    
    port.close()
    
def slowAnswerFromModem():
    port = hayes.hayes('/dev/ttyUSB0')
    
    answer = port.readAnswerDelayed("ATA", 20)
    print answer
    
    port.close()
    
def testVoiceInit():    
    modem = si24xx('/dev/ttyUSB0')
    modem.initModeVoice()
    
    print modem.stateVoice
    
    modem.close()

def testVoiceStates():
    modem = si24xx('/dev/ttyUSB0')
    time.sleep(1)
    modem.hangupModeVoice()
    time.sleep(1)
    modem.resetMode()
    time.sleep(1)
    
    print modem.stateVoice
    
    modem.initModeVoice()
    
    while modem.modemModeCurrent != modem.modemModes.VOICE:
        time.sleep(0.1)
    
    print modem.stateVoice
    
    while modem.stateVoice != modem.responseVoice.DIALTONE:
        time.sleep(0.1)
    
    modem.dialModeVoice("1,0,4")
    
    while modem.stateVoice != modem.responseVoice.RINGING:
#     while modem.stateVoice != modem.responseVoice.QUITE:
        time.sleep(0.1)
        
    print modem.stateVoice
    
    time.sleep(2)
    
    modem.hangupModeVoice()
    time.sleep(1)
    
    print modem.stateVoice
    
    modem.resetMode()
    time.sleep(1)
    
    modem.close()
