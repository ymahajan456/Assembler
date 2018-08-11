# Generate VHDL ROM File file for simulation 

from SupportFunctions import *

def convertHexfileToMemoryMap(inFileName, outFileName, wordLen):
    """ If word remains incomplete due to jump in record then zeros are appended
    to complete the last word """
    inFile = open(inFileName, 'r')
    outFile = open(outFileName, 'w')
    memoryIndex = 0
    previosRecordLen = 0
    previousStart = 0
    buffer = ""
    offset = 0
    lineNo = 1
    for record in inFile.read().split('\n'):    
        record = record.replace(" ", "")
        if record:
            if record[0] != ':':
                print("Error reading Hex file at line", lineNo)
                print("Ever record must start with ':'")
                return
            dataLen = int(eval('0x' + record[1:3]))
            offset = int(eval('0x' + record[3:7]))
            checkSum = generateChecksumForIntelHex(record[1:-2])
            if (len(record) - 11)//2 != dataLen:
                print("Error reading hex file at line", lineNo)
                print("Ambiguous record length.", datalen, )
                return
            if (checkSum[2:] != record[-2:]):
                print("Error reading hex file at line", lineNo)
                print("Checksum error")
                return
            if (record[7:9] != "00"):
                if record[7:9] == "01":
                    break
                else:
                    print("Unsupported record type :", record[7:9])
                    break
            # check for incomplete words
            if(offset != memoryIndex) and buffer:
                outFile.write(str(memoryIndex) + " " + buffer + "".join(['0' for i in range(2*wordLen - len(buffer))]) + '\n')
                buffer = ""
            memoryIndex = offset
            #print('line no', lineNo, 'memoryIndex', memoryIndex, 'offset', offset)
            recordStart = 9
            while((recordStart + wordLen*2) < (len(record) - 1)):
                #print((recordStart + wordLen*2) ,(len(record) - 1))
                outFile.write(str(memoryIndex) + " " + record[recordStart :recordStart + 2*wordLen -1] + '\n')
                recordStart = recordStart + 2*wordLen;
                memoryIndex = memoryIndex + 1
            buffer = buffer + record[recordStart:-2]
        lineNo = lineNo + 1
        #outFile.write('// ' + str(memoryIndex) + '\n')
    inFile.close()
    outFile.close()


def generateROMsimFromHexFile(inFileName, outFileName, addressLen, wordLen, 
                    outWordsCount = 2, ports = 1, memoryLen = None):

    convertHexfileToMemoryMap(inFileName, 'interFile.intr', wordLen)
    
def generateROMsimFromIntrFile(inFileName, outFileName, addressLen, wordLen, 
                    outWordsCount = 1, ports = 1, memoryLen = 128):
                    
    memoryLen = 2**(ceil(log2(memoryLen)))
    
    inFile = open(inFileName, 'r')
    outFile = open(outFileName, 'w')
    
    printStr = """library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.math_real.all;

entity ROM_SIM is
    generic(memory_len : integer := %d ;
            word_len : integer := %d ;
            address_len : integer := %d);
""" % (memoryLen, wordLen*8, addressLen)
    
    outFile.write(printStr)
    
        

    printStr = """
        address%d : in std_logic_vector(address_len -1 downto 0);
        data_out%d : out std_logic_vector(%d downto 0);
        rd%d_ena : in std_logic;""" 
        
    outFile.write("    port(")
    for i in range(ports):
        outFile.write(printStr %(i, i, 8*wordLen*outWordsCount - 1, i))
    outFile.write('\n        clk : std_logic);\n end entity;\n')
    
    printStr = """
architecture behave of ROM_SIM is
    type int_array is array(0 to memory_len-1) of integer;
    signal memory : int_array := (others => 0);
    """
    outFile.write(printStr)
    outFile.write('constant index_len : integer := integer(ceil(log2(real(memory_len))));\n')
    printStr = "    signal mem_index%d  : std_logic_vector(index_len-1 downto 0);\n"
    for i in range(ports):
        outFile.write(printStr %i)
    
    outFile.write('begin')
    
    dataStr = "std_logic_vector(to_unsigned(memory(to_integer(unsigned(mem_index%d)) + %d),word_len))"
    
    printStr = """
    mem_index%d <= address%d(index_len -1 downto 0);
    port%d : process(rd%d_ena, mem_index%d)
    begin
        data_out%d <= """
    for i in range(ports):
        outFile.write(printStr %(i, i, i, i, i, i))
        for j in range(outWordsCount - 1):
            outFile.write(dataStr %(i ,j))
            outFile.write(' & ')
        outFile.write(dataStr %(i ,outWordsCount - 1))
        outFile.write(';\n    end process;')
    outFile.write('\n\n\n')
    i = 0;
    for line in inFile.read().split('\n'):
        if line :
            if line[0] == '@':
                continue
            line = line.split(' ')
            outFile.write('    memory('+line[0]+') <= '+str(int(eval('0x' + line[1])))+';')
            i = i + 1
            if i==3:
                i = 0
                outFile.write('\n')
    outFile.write('\nend architecture;\n')
    inFile.close()
    outFile.close()
    
    
if __name__ == '__main__':
    convertHexfileToMemoryMap('chutiyap.hex', 'memMap1.txt', 4)
    generateROMsimFromIntrFile('memMap1.txt', 'ROM.vhd', 32, 4)
