from BitField import *

class InstructionType(object):
    
    def __init__(self, name = None, insLen = 0, bitFields = [], inputMap = [], fetchLen = 0):
        self.name = name
        self.insLen = insLen
        self.fieldNames = []
        self.inputMap = {}
        self.fetchLen = fetchLen
        self.setBitFileds(bitFields)
        if not self.verifyBitFields():
            print("Invalid Bit fields")
            self.fieldNames = []
            self.bitFields = []
        self.setInputMap(inputMap)
        
    def addBitfields(self, bitFields):
        for field in bitFields:
            if (type(field) is BitField) or (type(field) is OpcodeField):
                self.bitFields.append(field)
                self.fieldNames.append(field.name.upper())
                
    def setBitFileds(self, bitFields):
        self.bitFields = []
        self.fieldNames = []
        self.addBitfields(bitFields)
        
    def verifyBitFields(self):
        bits = [bit for bit in range(self.insLen)]
        correct = True
        for field in self.bitFields:
            for bit in field.oRange:
                if bit not in bits:
                    print("There is conflict at bit", bit, 'for instruction', self.name)
                    correct = False
                else:
                    bits.remove(bit)
        if len(bits):
            print("Following Bits in instruction", self.name, 'are empty :', bits, 'for instruction', self.name)
        return correct
        
    def setInputMap(self, inputMap):
        # no checking length checking 
        for inp in inputMap.keys():
            if inp.upper() in self.fieldNames:
                self.inputMap[inp.upper()] = inputMap[inp]
            else:
                print("Bit-field", inp.upper(), "is not defined for instruction", self.name)
                
    
    def generate(self, parsedIns):
        insField = ['0' for i in range(self.insLen)]
        for i in range(len(self.fieldNames)):  # same order in fieldNames and bit-fields
            self.bitFields[i].generate(parsedIns[self.inputMap[self.fieldNames[i]]], insField)

        insField.reverse()
            
        return "".join(insField)
        
if __name__ == "__main__":
    opcodeMap = [((0,7),(0,7))]
    opcodes = {'ADD': 36}
    opcode = OpcodeField("opcode", opcodeMap, 7, 32, opcodes)
    
    rdMap = [((0,5),(7,12))]
    rd = BitField("RD", rdMap, 5, 32, False, 'r')
    
    immUMap = [((12,32),(12,32))]
    immU = BitField("immU", immUMap, 32, 32, True)
    
    UinpMap = {"opcode": 0, "rd": 1, "immU":2}
    U = InstructionType("U",32, [opcode, rd, immU], UinpMap)
    data = binStrToHexStr('0b' + U.generate(["ADD", 'r5', str(89<<12)]))
    print(data)
    