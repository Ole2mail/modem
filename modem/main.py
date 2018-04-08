'''
Created on 31 Mar 2018

@author: ole2
'''

import hayesTests
import time

def main(args):
    hayesTests.simpleAnswerFromModem()
    hayesTests.slowAnswerFromModem()
    hayesTests.testVoiceInit()
    hayesTests.testVoiceStates()
    time.sleep(1)

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
