# Support Functions

from math import *
import os, errno

def silentremove(filename):
    try:
        os.remove(filename)
    except OSError as e: # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise # re-raise exception if a different error occurred

def hexStrToVal(hexStr, signed = False):
    val = eval(hexStr)
    if(signed):
        hexLen = len(hexStr.replace(' ','')) - 2
        posMax = 2**(4 * hexLen - 1)
        if val >= posMax:
            val = val - posMax * 2;
    return val

def binStrToVal(binStr, signed = False):
    val = eval(binStr)
    if(signed):
        binLen = len(binStr.replace(' ','')) - 2
        posMax = 2**(binLen - 1)
        if val >= posMax:
            val = val - posMax * 2;
    return val
    
def valToHexStr(num, length):
    return "{0:#0{1}X}".format((num+(1 << (4*length)))%(1 << (4*length)),length+2)
    
def valToBinStr(num, length):
    return "{0:#0{1}b}".format((num+(1 << length))%(1 << length),length+2)
    
def hexStrToBinStr(hexStr, length = None, signed = False):
    if not length:
        length = (len(hexStr)-2)*4
    return valToBinStr(hexStrToVal(hexStr, signed), length)

def binStrToHexStr(binStr, length = None, signed = False):
    if not length:
        length = ceil((len(binStr)-2)/4)
    return valToHexStr(binStrToVal(binStr, signed),length)
    
def generateChecksumForIntelHex(hexStr):
    if(len(hexStr)%2):
        print("Hex string with odd number of elements ")
        return
    sum = 0;
    for i in range(len(hexStr)//2):
        sum = sum + eval('0x' + hexStr[2*i : 2*i + 2])
    sum = ~(sum % 256) + 1
    return valToHexStr(sum, 2)
    
        
if __name__ == '__main__':
    print(hexStrToVal('0x45'))
    print(hexStrToVal('0xF5',True))
    print(binStrToVal('0x101110',True))
    print(hexStrToBinStr('0xfda',10,True))
    print(binStrToHexStr('0b10110', signed = True))
    