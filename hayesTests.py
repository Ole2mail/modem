'''
Created on 31 Mar 2018

@author: ole2
'''

from modem.hayes import hayes
from modem.si24xx import si24xx

import time
from time import sleep
from _curses import baudrate

def printHayesStates(modem):
    print
    print modem.stateCMD
    print modem.stateLine
    
def printSi24xxStates(modem):
    print
    print modem.stateModem
    print modem.stateVoiceAction
    print modem.stateVoiceLine
    print modem.stateVoiceParallel
    print modem.stateVoiceDTMF

def simpleAnswerFromModem():
    port = hayes('/dev/ttyUSB0', baudrate=230400) #115200)
    printHayesStates(port)
    
    answer = port.readAnswer("i7")        
    print answer
    printHayesStates(port)
    
    answer = port.readAnswer("ATi6")        
    print answer
    printHayesStates(port)
    
    port.close()
    
def slowAnswerFromModem():
    port = hayes('/dev/ttyUSB0')
    printHayesStates(port)
    
    answer = port.readAnswerDelayed("H", 1)        
    print answer
    printHayesStates(port)
    
    answer = port.readAnswerDelayed("ATA", 20)
    print answer
    printHayesStates(port)
    
    port.close()
    
def testVoiceInit():    
    modem = si24xx('/dev/ttyUSB0', baudrate=230400)
    printHayesStates(modem)
    printSi24xxStates(modem)
    
    modem.resetModem()
    modem.initModeVoice()
    modem.offhookModeVoice()
    sleep(1)
    printHayesStates(modem)
    printSi24xxStates(modem)
    
    modem.close()

def testVoiceStates():
    modem = si24xx('/dev/ttyUSB0')
    printHayesStates(modem)
    printSi24xxStates(modem)
    
    modem.resetModem()
    modem.resetMode()
    printHayesStates(modem)
    printSi24xxStates(modem)
    
    modem.initModeVoice()
    printHayesStates(modem)
    printSi24xxStates(modem)
    
    print "waiting modem to enter VOICE mode"
    while modem.stateModem != modem.mode.VOICE:
        time.sleep(0.1)
    printHayesStates(modem)
    printSi24xxStates(modem)
    
    modem.offhookModeVoice()
    printHayesStates(modem)
    printSi24xxStates(modem)
    
    print "waiting modem to detect DIAL TONE"
    while modem.responseActionState != modem.responseVoice.DIALTONE:
        printSi24xxStates(modem)
        time.sleep(1)
    printHayesStates(modem)
    printSi24xxStates(modem)
    
    modem.dialModeVoice("1,0,4")
    printHayesStates(modem)
    printSi24xxStates(modem)
    
    print "waiting modem to detect RING-back"
    while modem.responseActionState != modem.responseVoice.RINGING:
#     while modem.stateVoice != modem.responseVoice.QUITE:
        time.sleep(0.1)
    printHayesStates(modem)
    printSi24xxStates(modem)
    
    time.sleep(2)

    print "hanging-up the modem"    
    modem.hangupModeVoice()
    printHayesStates(modem)
    printSi24xxStates(modem)
    
    modem.resetMode()
    printHayesStates(modem)
    printSi24xxStates(modem)
    
    modem.close()
