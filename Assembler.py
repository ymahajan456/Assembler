from Instruction import *
import re
import linecache
BigEndian = False
LittleEndian = True

class Assembler(object):
    def __init__(self, name = None, insTypes = [], insMaps = {}, endianness = BigEndian):
        self.name = name.upper()
        self.insTypes = list(set(insTypes))
        self.insList = [type.name.upper() for type in self.insTypes]
        self.insMaps = {}
        self.endianness = endianness
        for insSet in insMaps.keys():
            self.insMaps[insSet.upper()] = [ins.upper() for ins in insMaps[insSet]]
        
    def convInstruction(self, fetch):
        for i in range(len(self.insList)):
            if fetch[0].upper() in self.insMaps[self.insList[i]]:
                result = self.insTypes[i].generate(fetch)
                reqLen = ceil(len(result)/8)*8
                result = "".join(['0' for i in range(reqLen - len(result))]) + result
                if self.endianness == LittleEndian:
                    resultCopy = result
                    result = ""
                    for i in range(reqLen//8):
                        result =  resultCopy[8*i : 8 *(i+1)] + result
                return result
        print("Unknown Instruction", fetch)
                    
    def convASMfile(self, inFileName, outFileName, wordLen = 1):
        outFile = open(outFileName, 'w')
        inFile = open(inFileName, 'r')
        memoryIndex = 0
        startIndex = 0
        for line in inFile.read().split('\n'):
            commentIndex = line.find(';')
            if(commentIndex > -1):
                line = line[0:commentIndex]
            line = line.replace("  ", " ")
            if line:
                fetch = re.split(', | ', line)
                if(fetch[0].upper() == 'ORG'):
                    memoryIndex = int(eval(fetch[1]))
                    startIndex = memoryIndex
                    outFile.write('@' + str(memoryIndex) + '\n')
                else:
                    insOut = binStrToHexStr('0b' + self.convInstruction(fetch))[2:]
                    print(insOut)
                    for i in range(len(insOut)//(wordLen*2)):
                        outFile.write(str(memoryIndex) + " " + insOut[2*i:2*i+2] + '\n')
                        memoryIndex = memoryIndex + 1
        
        inFile.close()
        outFile.close()
        
    def rearrengeIns(self, inFileName, outFileName):
        outFile = open(outFileName, 'w')
        inFile = open(inFileName, 'r') 
        lineNumber = 1
        orgTuples = []
        orgTuples.insert(0,[0, 0, None])
        for line in inFile.read().split('\n'):
            line = line.replace("  ", " ")
            if line:
                if (line[0] == '@'):
                    orgTup = [int(eval(line[1:])), lineNumber, None]
                    orgTuples[-1][2] = lineNumber
                    orgTuples.append(orgTup)
            lineNumber = lineNumber + 1
        inFile.close()
        orgTuples[-1][2] = lineNumber
        orgTuples = sorted(orgTuples, key = lambda x: x[0])
        for i in range(len(orgTuples)):
            outFile.write('@' + str(orgTuples[i][0]) + '\n')
            for lineNo in range(orgTuples[i][1] + 1, orgTuples[i][2]):
                outFile.write(linecache.getline(inFileName, lineNo))
        outFile.close()
            
    def generateRecord(self,offset, data):
        #print("data", data)
        hexStr  = valToHexStr(len(data)//2,2)[2:] + valToHexStr(offset, 4)[2:] + '00' + data
        #print(hexStr)
        return ':' + hexStr + generateChecksumForIntelHex(hexStr)[2:] + "\n"
        
 
    def generateHexFile(self, inFileName, outFileName, wordLen, recordLen = 32):
        if (recordLen % wordLen):
            print("recordLen must be multiples of wordLen")
            return
        outFile = open(outFileName, 'w')
        inFile = open(inFileName, 'r')
        buffer = ""
        offset = 0
        memoryIndex = 0
        lineNo = 1
        for line in inFile.read().split('\n'): 
            if line:
                if (line[0] == '@'):
                    if buffer:
                        record = self.generateRecord(memoryIndex, buffer)
                        outFile.write(record)
                        buffer = ""
                        memoryIndex = memoryIndex + len(buffer)/ (2*wordLen)
                    offset = int(eval(line[1:]))
                    if offset < memoryIndex:
                        print("Address Overlap at line :", lineNo)
                        break
                    memoryIndex = offset
                else:
                    line = line.split(' ')[1]
                    buffer = buffer + line
                    while (len(buffer)//2 >= recordLen) :
                        record = self.generateRecord(memoryIndex, buffer[:2*recordLen])
                        outFile.write(record)
                        memoryIndex = memoryIndex + recordLen//wordLen
                        buffer = buffer = buffer[2*recordLen:]
            lineNo = lineNo + 1
        record = self.generateRecord(memoryIndex, buffer)
        outFile.write(record)
        outFile.write(":00000001FF\n")
        inFile.close()
        outFile.close()
        
if __name__ == '__main__' :
    opcodeMap = [((0,7),(0,7))]
    opcodes = {'ADD': 36, 'SUB' : 35, 'CMP' : 30}
    opcode = OpcodeField("opcode", opcodeMap, 7, 32, opcodes)
    
    rdMap = [((0,5),(7,12))]
    rd = BitField("RD", rdMap, 5, 32, False, 'x')
    
    immUMap = [((0,20),(12,32))]
    immU = BitField("immU", immUMap, 20, 32, True)
    
    UinpMap = {"opcode": 0, "rd": 1, "immU":2}
    U = InstructionType("U",32, [opcode, rd, immU], UinpMap)
    insMaps = {'U' : ['ADD', 'SUB', 'CMP']}
    assTest = Assembler('Test', [U], insMaps)
    assTest.convASMfile('testASM.txt', 'int.txt')
    assTest.rearrengeIns('int.txt', 'int2.txt')
    assTest.generateHexFile('int2.txt', 'chutiyap.hex', 4)
