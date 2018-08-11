# Generic Assembler

from SupportFunctions import *

def checkEmptyFields(fields):
    emptyList = []
    for i in range(len(fields)):
        if not fields[i]:
            emptyList.append(i)
    return emptyList

class BitField(object): 
    def __init__(self, name = None, map = [], fidLen = 0, insLen = 0, signed = False, prefix = ""):
        self.name = name.upper()
        self.subfields = 0
        self.map = []
        self.oRange = []
        self.insLen = insLen
        self.fidLen = 0
        self.signed = signed
        self.setRanges(map, fidLen, insLen)
        self.prefix = prefix.upper()
        
    def setRanges(self, map, fidLen, insLen):
        if len(map):
            inFields = [field[0] for field in map]
            outFields = [field[1] for field in map]
            
            inCheck = [False for i in range(fidLen)]
            outCheck = [False for i in range(insLen)]
            
            correct = True
            for inField, outField in zip(inFields, outFields):
                if(len(range(inField[0], inField[1])) != len(range(outField[0], outField[1]))) and (len(range(inField[0], inField[1]))):
                    print("Field lengths are not appropriate for map", inField, "to", outField)
                    correct = False
                for i in range(inField[0], inField[1]):
                    if(inCheck[i]):
                        print("Input Field Conflict at bit",i, 'for', self.name)
                        correct = False
                    else:
                        inCheck[i] = True
                for i in range(outField[0], outField[1]):
                    if(outCheck[i]):
                        print("Instruction Field Conflict at bit",i, 'for', self.name)
                        correct = False
                    else:
                        outCheck[i] = True
                        
            eInList = checkEmptyFields(inCheck)
            if len(eInList):
                print("Input field is not assigned for ", eInList, "for field", self.name)
            if(correct):
                self.map = map
                self.subfields = len(map)
                self.oRange = [i for i in range(self.insLen) if outCheck[i]]
                self.fidLen = fidLen
                    
    def convertValue(self, value, signed = False):
        if type(value) is int:
            value = valToBinStr(value, self.fidLen)
        elif type(value) is str:
            value = self.removePrefix(value)
            if value[:2].upper() == '0X':
                value = hexStrToBinStr(value, self.fidLen, signed)
            elif value[:2].upper() == '0B':
                value = binStrToVal(value, signed)
                value = valToBinStr(value, self.fidLen)
            else :
                try:
                    value = int(value)
                    value = valToBinStr(value, self.fidLen)
                except:
                    print("Invalid value :", value)
        value = [val for val in value[2:]]   # remove '0b'
        value.reverse()
        return value
    
    def generate(self, value, insField, signed = False):
        value = self.convertValue(value, signed)
        for field in self.map:
            for i,j in zip(range(field[0][0], field[0][1]), range(field[1][0],field[1][1])):
                insField[j] = value[i]
                
    def removePrefix(self, value):
        if len(self.prefix):
            if value[:len(self.prefix)].upper() == self.prefix:
                return value[len(self.prefix):]
            else:
                print("Incorrect Prefix")
        return value
                
class OpcodeField(BitField):
    def __init__(self, name = None, map = [], fidLen = 0, insLen = 0, opcodes = None, signed = False):
        self.name = name.upper()
        self.subfields = 0
        self.map = []
        self.oRange = []
        self.fidLen = 0
        self.insLen = insLen
        self.signed = signed
        self.prefix = ""
        self.setRanges(map, fidLen, insLen)
        self.setOpcodes(opcodes)
        
        
    def setOpcodes(self, opcodes):
        self.opcodes = {}
        # No validation of anything
        self.addOpcodes(opcodes)
        
    def addOpcodes(self, opcodes):
        for ins in opcodes.keys():
            self.opcodes[ins.upper()] = self.convertValue(opcodes[ins])
            
    def generate(self, ins, insField):
        if ins.upper() not in self.opcodes.keys():
            print("Opcode is not defined for", ins)
            return
            
        value = self.opcodes[ins.upper()]
        for field in self.map:
            for i,j in zip(range(field[0][0], field[0][1]), range(field[1][0],field[1][1])):
                insField[j] = value[i]
                
    
if __name__ == '__main__':
    rjMap = [((11,12),(0,1)),((0,11),(1,12))]
    RJ = BitField(name = 'RJ',map = rjMap, fidLen = 12, insLen = 32)
    tmp = ['0' for i in range(32)]
    RJ.setValue(32, tmp, True)
    tmp.reverse()
    print(tmp)
    tmp = ['0' for i in range(32)]
    RJ.setValue('0xFF3', tmp, False)
    tmp.reverse()
    print(tmp)
    tmp = ['0' for i in range(32)]
    RJ.setValue('0b10111', tmp, True)
    tmp.reverse()
    print(tmp)
    
