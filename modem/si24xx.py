'''
Created on 1 Apr 2018

@author: ole2
'''
from modem.hayes import hayes
from enum import Enum

import time
import threading
import const

class si24xx(hayes):
    '''
    classdocs
    '''
    const.SI24XX_ASK = "?"
        
    const.SI24XX_MODE = "+FCLASS"
    const.SI24XX_MODE_DATA = "=0"
    const.SI24XX_MODE_VOICE = "=8"
    
    const.SI24XX_VOICE_LINE_SET = "+VLS"
    const.SI24XX_VOICE_LINE_INIT = "=0"
    const.SI24XX_VOICE_LINE_SI3000_SPK = "=13"    
    const.SI24XX_VOICE_LINE_SI3000_HST = "=15"    
    
    const.SI24XX_TONE_DURATION = "+VTD"
    const.SI24XX_TONE_OR_DTMF_GEN = "+VTS"
    
    const.SI24XX_HANGUP = "ATH"
    
    const.SI24XX_DLE = b'\x10'

    # 0.1 sec pause between read pull cycles
    const.SLEEPING_TIME = 0.1

    modemModes = Enum("modemModes", "NONE DATA VOICE")
    modemModeCurrent = modemModes.NONE

    responseVoice = Enum("responseVoice", "NONE DTMFSTART DTMFEND RING DTMF1 DTMF2 DTMF3 DTMF4 DTMF5 DTMF6 DTMF7 "
    "DTMF8 DTMF9 DTMF0 DTMFA DTMFB DTMFC DTMFD DTMFE DTMFF BUFOVER BUFUNDER FAXCALL DATACALL LINECUT LINEWIRED "
    "QUITE LOOP BUSY DIALTONE RINGING PARONHOOK PAROFFHOOK FAXORDATAANS DATAANS DRIFTNEG DRIFTPOS")
    
    si24xxVoiceResponses = {const.SI24XX_DLE+"/":responseVoice.DTMFSTART, const.SI24XX_DLE+"~":responseVoice.DTMFEND,
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

    # voice events discovery thread based loop
    def _readVoiceStateLoop(self):
        while True:
            quantity = super(hayes, self).in_waiting 
            if quantity == 0:
                time.sleep(const.SLEEPING_TIME)
                print "."
            else:
                print quantity
                
                incoming = super(si24xx, self).read()
                
                print incoming
                
                # response parsing section
                stateVoiceList = [self.responseVoice.NONE]
                stateVoiceList.extend([v for k,v in self.si24xxVoiceResponses.items() if k in incoming])
                # extracting voice state changes happened
                if self.modemModeCurrent == self.modemModes.VOICE:
                    while len(stateVoiceList) > 0:
                        self.stateVoice = stateVoiceList.pop(0)
                        time.sleep(const.SLEEPING_TIME)


    def __init__(self, params):
        '''
        Constructor
        '''
        self.stateVoice = self.responseVoice.NONE
        self.actionVoice = self.responseVoice.NONE
        
        super(si24xx, self).__init__(params)
        
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
    
    def initModeVoice(self, mode = const.SI24XX_VOICE_LINE_SI3000_SPK):
        self.writeCMD(const.SI24XX_MODE + const.SI24XX_MODE_VOICE)
        self.modemModeCurrent = self.modemModes.VOICE
        self.writeCMD(const.SI24XX_VOICE_LINE_SET + const.SI24XX_VOICE_LINE_INIT)
        self.writeCMD(const.SI24XX_VOICE_LINE_SET + mode)
        
    def dialModeVoice(self, number, pause=10):
        self.writeCMD(const.SI24XX_TONE_DURATION + "=" + str(pause))
        self.writeCMD(const.SI24XX_TONE_OR_DTMF_GEN + "=" + number)
        
    def hangupModeVoice(self):
        self.writeCMD(const.SI24XX_HANGUP)
     
    def resetMode(self):
        self.writeCMD(const.SI24XX_MODE + const.SI24XX_MODE_DATA)    
        self.modemModeCurrent = self.modemModes.DATA

        
        
        