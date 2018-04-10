'''
Created on 1 Apr 2018

@author: ole2
'''

from __future__ import print_function

from hayes import hayes
from enum import Enum

import time
import threading
import const

class si24xx(hayes):
    '''
    classdocs
    '''
    const.SI24XX_ASK = "?"
    
    const.SI24XX_RESET_MODEM = "Z"
        
    const.SI24XX_MODE = "+FCLASS"
    const.SI24XX_MODE_DATA = "=0"
    const.SI24XX_MODE_VOICE = "=8"
    
    const.SI24XX_VOICE_LINE_SET = "+VLS"
    const.SI24XX_VOICE_LINE_INIT_ONHOOK = "=0"
    const.SI24XX_VOICE_LINE_SI3000_SPK = "=13"    
    const.SI24XX_VOICE_LINE_SI3000_HST = "=15"    
    
    const.SI24XX_TONE_DURATION = "+VTD"
    const.SI24XX_TONE_OR_DTMF_GEN = "+VTS"
    
    const.SI24XX_HANGUP_DEFAULT = "ATH"
    
    const.SI24XX_DLE = b'\x10'

    mode = Enum("mode", "NONE DATA VOICE")

    responseVoice = Enum("responseVoice", "NONE DTMFSTART DTMFEND RING DTMF1 DTMF2 DTMF3 DTMF4 DTMF5 DTMF6 DTMF7 "
    "DTMF8 DTMF9 DTMF0 DTMFA DTMFB DTMFC DTMFD DTMFE DTMFF BUFOVER BUFUNDER FAXCALL DATACALL LINECUT LINEWIRED "
    "QUITE LOOP BUSY DIALTONE RINGING PARONHOOK PAROFFHOOK FAXORDATAANS DATAANS DRIFTNEG DRIFTPOS")
    
    si24xxVoiceResponses = {
        const.SI24XX_DLE+"/":responseVoice.DTMFSTART, const.SI24XX_DLE+"~":responseVoice.DTMFEND,
        const.SI24XX_DLE+"R":responseVoice.RING, const.SI24XX_DLE+"1":responseVoice.DTMF1,
        const.SI24XX_DLE+"2":responseVoice.DTMF2, const.SI24XX_DLE+"3":responseVoice.DTMF3,
        const.SI24XX_DLE+"4":responseVoice.DTMF4, const.SI24XX_DLE+"5":responseVoice.DTMF5,
        const.SI24XX_DLE+"6":responseVoice.DTMF6, const.SI24XX_DLE+"7":responseVoice.DTMF7,
        const.SI24XX_DLE+"8":responseVoice.DTMF8, const.SI24XX_DLE+"9":responseVoice.DTMF9,
        const.SI24XX_DLE+"A":responseVoice.DTMFA, const.SI24XX_DLE+"B":responseVoice.DTMFB,
        const.SI24XX_DLE+"C":responseVoice.DTMFC, const.SI24XX_DLE+"D":responseVoice.DTMFD,
        const.SI24XX_DLE+"E":responseVoice.DTMFE, const.SI24XX_DLE+"F":responseVoice.DTMFF,
        const.SI24XX_DLE+"o":responseVoice.BUFOVER, const.SI24XX_DLE+"u":responseVoice.BUFUNDER,
        const.SI24XX_DLE+"c":responseVoice.FAXCALL, const.SI24XX_DLE+"e":responseVoice.DATACALL,
        const.SI24XX_DLE+"h":responseVoice.LINECUT, const.SI24XX_DLE+"H":responseVoice.LINEWIRED,
        const.SI24XX_DLE+"q":responseVoice.QUITE, const.SI24XX_DLE+"l":responseVoice.LOOP,
        const.SI24XX_DLE+"b":responseVoice.BUSY, const.SI24XX_DLE+"d":responseVoice.DIALTONE,
        const.SI24XX_DLE+"r":responseVoice.RINGING, const.SI24XX_DLE+"p":responseVoice.PARONHOOK,
        const.SI24XX_DLE+"P":responseVoice.PAROFFHOOK, const.SI24XX_DLE+"a":responseVoice.FAXORDATAANS,
        const.SI24XX_DLE+"f":responseVoice.DATAANS, const.SI24XX_DLE+"(":responseVoice.DRIFTNEG,
        const.SI24XX_DLE+")":responseVoice.DRIFTPOS
        }
    
    responseActionState = Enum("responseActionState", "NONE RING FAXCALL DATACALL QUITE BUSY DIALTONE RINGING FAXORDATAANS DATAANS")
    
    si24xxVoiceActionStates = {
        responseVoice.RING:responseActionState.RING, responseVoice.FAXCALL:responseActionState.FAXCALL, responseVoice.DATACALL:responseActionState.DATACALL,
        responseVoice.QUITE:responseActionState.QUITE, responseVoice.BUSY:responseActionState.BUSY, responseVoice.DIALTONE:responseActionState.DIALTONE,
        responseVoice.RINGING:responseActionState.RINGING, responseVoice.FAXORDATAANS:responseActionState.FAXORDATAANS, responseVoice.DATAANS:responseActionState.DATAANS
        }
    
    def updateVoiceActionState(self, eventsList):
        if len(eventsList) > 0:
            iterState = iter(eventsList)
            for msg in iterState:
                key = self.si24xxVoiceActionStates.get(msg, self.responseActionState.NONE)
                if key != self.responseActionState.NONE:
                    # updating only if non-default (e.i. non-NONE)
                    self.stateVoiceAction = key
    
    responseLineState = Enum("responseLineState", "NONE LINECUT LINEWIRED LOOP DRIFTNEG DRIFTPOS")
    
    si24xxLineStates = {
        responseVoice.LINECUT:responseLineState.LINECUT, responseVoice.LINEWIRED:responseLineState.LINEWIRED,
        responseVoice.LOOP:responseLineState.LOOP, responseVoice.DRIFTNEG:responseLineState.DRIFTNEG, 
        responseVoice.DRIFTPOS:responseLineState.DRIFTPOS
        }
    
    def updateVoiceLineState(self, eventsList):
        if len(eventsList) > 0:
            iterState = iter(eventsList)
            for msg in iterState:
                key = self.si24xxLineStates.get(msg, self.responseLineState.NONE)
                if key != self.responseLineState.NONE:
                    # updating only if non-default (e.i. non-NONE)
                    self.stateVoiceLine = key
    
    responseParallelState = Enum("responseParallelState", "NONE PARONHOOK PAROFFHOOK")
    
    si24xxParallelStates = {
        responseVoice.PARONHOOK:responseParallelState.PARONHOOK, responseVoice.PAROFFHOOK:responseParallelState.PAROFFHOOK
        }
    
    def updateVoiceParallelState(self, eventsList):
        if len(eventsList) > 0:
            iterState = iter(eventsList)
            for msg in iterState:
                key = self.si24xxParallelStates.get(msg, self.responseParallelState.NONE)
                if key != self.responseParallelState.NONE:
                    # updating only if non-default (e.i. non-NONE)
                    self.stateVoiceParallel = key
    
    responseDTMFState = Enum("responseDTMFState", "NONE DTMFSTART DTMFEND")
    
    si24xxDTMFStates = {
        responseVoice.DTMFSTART:responseDTMFState.DTMFSTART, responseVoice.DTMFEND:responseDTMFState.DTMFEND
        }
    
    def updateVoiceDTMFState(self, eventsList):
        if len(eventsList) > 0:
            iterState = iter(eventsList)
            for msg in iterState:
                key = self.si24xxDTMFStates.get(msg, self.responseDTMFState.NONE)
                if key != self.responseDTMFState.NONE:
                    # updating only if non-default (e.i. non-NONE)
                    self.stateVoiceDTMF = key
    
    si24xxDTMFNumbers = {
        responseVoice.DTMF0:'0', responseVoice.DTMF1:'1', responseVoice.DTMF2:'2', responseVoice.DTMF3:'3', 
        responseVoice.DTMF4:'4', responseVoice.DTMF5:'5', responseVoice.DTMF6:'6', responseVoice.DTMF7:'7', 
        responseVoice.DTMF9:'8', responseVoice.DTMF9:'9', responseVoice.DTMFA:'A', responseVoice.DTMFB:'B', 
        responseVoice.DTMFC:'C', responseVoice.DTMFD:'D', responseVoice.DTMFE:'E', responseVoice.DTMFF:'F'
        }
    
    def updateVoiceDTMFSequence(self, eventsList):
        if len(eventsList) > 0:
            iterState = iter(eventsList)
            for msg in iterState:
                key = self.si24xxDTMFNumbers.get(msg, "")
                if key != "":
                    # appending only if non-default (e.i. non-NONE)
                    self.sequenceVoiceDTMF += key

    def resetVoiceDTMFSequence(self):
        self.sequenceVoiceDTMF = ""
        
    modemReceiving = False
    
    # voice events discovery thread based loop
    def _readVoiceStateLoop(self):
        import hexdump
        while self.alive == True:
                incoming = super(si24xx, self).read()
            
#                 hexdump.dump(incoming, sep=":")
#                 print
#                 print(incoming)
                
                # response parsing section
                stateVoiceList = [self.responseVoice.NONE]
                stateVoiceList.extend([v for k,v in self.si24xxVoiceResponses.items() if k in incoming])
                # extracting voice state changes happened
                if self.stateModem == self.mode.VOICE:
                    self.updateVoiceActionState(stateVoiceList)
                    self.updateVoiceLineState(stateVoiceList)
                    self.updateVoiceParallelState(stateVoiceList)
                    self.updateVoiceDTMFState(stateVoiceList)
                    self.updateVoiceDTMFSequence(stateVoiceList)

    def __init__(self, *args, **kwargs):
        '''
        Constructor
        '''
        self.stateModem = self.mode.NONE 
        self.stateVoiceAction = self.responseActionState.NONE
        self.stateVoiceLine = self.responseLineState.NONE
        self.stateVoiceParallel = self.responseParallelState.NONE
        self.stateVoiceDTMF = self.responseDTMFState.NONE
        self.sequenceVoiceDTMF = ""
        
        super(si24xx, self).__init__(*args, **kwargs)
        
    def open(self):
        hayes.open(self)
        # start reading thread
        self.alive = True
        self.rxThread = threading.Thread(target=self._readVoiceStateLoop)
        self.rxThread.daemon = True
        self.rxThread.start()
        
    def close(self):
        # stop reading thread
        self.alive = False
        self.rxThread.join()
        hayes.close(self)
        
    def initModeVoice(self):
        self.writeCMDDelayed(const.SI24XX_MODE + const.SI24XX_MODE_VOICE, 1)
        self.stateModem = self.mode.VOICE
        self.writeCMD(const.SI24XX_VOICE_LINE_SET + const.SI24XX_VOICE_LINE_INIT_ONHOOK)
        
    def offhookModeVoice(self, mode = const.SI24XX_VOICE_LINE_SI3000_SPK):
        self.writeCMD(const.SI24XX_VOICE_LINE_SET + mode)
        
    def dialModeVoice(self, number, pause=10):
        self.writeCMD(const.SI24XX_TONE_DURATION + "=" + str(pause))
        self.writeCMD(const.SI24XX_TONE_OR_DTMF_GEN + "=" + str(number))
        
    def dialDigitModeVoice(self, digit, pause=10):
        self.writeCMD(const.SI24XX_TONE_DURATION + "=" + str(pause))
        self.writeCMD(const.SI24XX_TONE_OR_DTMF_GEN + "=" + str(digit))
        
    def dialPauseModeVoice(self, pause):
        self.writeCMD(const.SI24XX_TONE_OR_DTMF_GEN + "=[0,0," + str(pause) + "]")
        
    def hangupModeVoice(self):
        self.writeCMDDelayed(const.SI24XX_VOICE_LINE_SET + const.SI24XX_VOICE_LINE_INIT_ONHOOK, 1)
     
    def resetMode(self):
        self.writeCMDDelayed(const.SI24XX_MODE + const.SI24XX_MODE_DATA, 1)    
        self.stateModem = self.mode.DATA
        
    def resetModem(self):
        self.writeCMDDelayed(const.SI24XX_HANGUP_DEFAULT, 1)
        self.writeCMDDelayed(const.SI24XX_RESET_MODEM, 3)
        self.stateModem = self.mode.NONE

        
        
        