from Assembler import *
from GenerateROM import *
import sys, os, getopt
from optparse import OptionParser
from optparse import Option, OptionValueError
import pickle, errno

def genAssembler():
    opcodeMap = [((0,7),(0,7))]
    opcodeList = {
        'LUI'   : '0b0110111',  'ADDI'  : '0b0010011',
        'AUIPC' : '0b0010111',  'SLTI'  : '0b0010011',
        'JAL'   : '0b1101111',  'SLTIU' : '0b0010011',
        'JALR'  : '0b1100111',  'XORI'  : '0b0010011',
        'BEQ'   : '0b1100011',  'ORI'   : '0b0010011',
        'BNE'   : '0b1100011',  'ANDI'  : '0b0010011',
        'BLT'   : '0b1100011',  'SLLI'  : '0b0010011',
        'BGE'   : '0b1100011',  'SRLI'  : '0b0010011',
        'BLTU'  : '0b1100011',  'SRAI'  : '0b0010011',
        'BGEU'  : '0b1100011',  'ADD'   : '0b0110011',
        'LB'    : '0b0000011',  'SUB'   : '0b0110011',
        'LH'    : '0b0000011',  'SLL'   : '0b0110011',
        'LW'    : '0b0000011',  'SLT'   : '0b0110011',
        'LBU'   : '0b0000011',  'SLTU'  : '0b0110011',
        'LHU'   : '0b0000011',  'XOR'   : '0b0110011',
        'SB'    : '0b0100011',  'SRL'   : '0b0110011',
        'SH'    : '0b0100011',  'SRA'   : '0b0110011',
        'SW'    : '0b0100011',  'OR'    : '0b0110011',
        'AND'   : '0b0110011'}

    opcode = OpcodeField("opcode", opcodeMap, 7, 32, opcodeList)

    funct3Map = [((0,3),(12,15))]
    funct3List = {
        'ADDI'  : '0b000',
        'SLTIU' : '0b011',  'SLTI'  : '0b010',
        'JALR'  : '0b000',  'XORI'  : '0b100',
        'BEQ'   : '0b000',  'ORI'   : '0b110',
        'BNE'   : '0b001',  'ANDI'  : '0b111',
        'BLT'   : '0b100',  'SLLI'  : '0b001',
        'BGE'   : '0b101',  'SRLI'  : '0b101',
        'BLTU'  : '0b110',  'SRAI'  : '0b101',
        'BGEU'  : '0b111',  'ADD'   : '0b000',
        'LB'    : '0b000',  'SUB'   : '0b000',
        'LH'    : '0b001',  'SLL'   : '0b001',
        'LW'    : '0b010',  'SLT'   : '0b010',
        'LBU'   : '0b100',  'SLTU'  : '0b011',
        'LHU'   : '0b101',  'XOR'   : '0b100',
        'SB'    : '0b000',  'SRL'   : '0b101',
        'SH'    : '0b001',  'SRA'   : '0b101',
        'SW'    : '0b010',  'OR'    : '0b110',
        'AND'   : '0b111'}

    funct3 = OpcodeField('funct3', funct3Map, 3, 32, funct3List)

    funct7Map = [((0,7),(25,32))]
    funct7List = {
        'SLLI'  : '0b0000000',  'SLTU'  : '0b0000000',
        'SRLI'  : '0b0000000',  'XOR'   : '0b0000000',
        'SRAI'  : '0b0100000',  'SRL'   : '0b0000000',
        'ADD'   : '0b0000000',  'SRA'   : '0b0100000',
        'SUB'   : '0b0100000',  'OR'    : '0b0000000',
        'SLL'   : '0b0000000',  'AND'   : '0b0000000',
        'SLT'   : '0b0000000'}
        
    funct7 = OpcodeField('funct7', funct7Map, 7, 32, funct7List)

    rdMap = [((0,5),(7,12))]
    rd = BitField("RD", rdMap, 5, 32, False, 'x')

    rs1Map = [((0,5),(15,20))]
    rs1 = BitField("RS1", rs1Map, 5, 32, False, 'x')

    rs2Map = [((0,5),(20,25))]
    rs2 = BitField("RS2", rs2Map, 5, 32, False, 'x')

    shamtMAP = [((0,5),(20,25))]
    shamt = BitField('shamt', shamtMAP, 5, 32, False)

    immIMAP = [((0,12),(20,32))]
    immI = BitField('immI', immIMAP, 12, 32, True)

    immSMAP = [((0,5),(7,12)),((5,12),(25,32))]
    immS = BitField('immS', immSMAP, 12, 32, True)

    immBMAP = [((12,13),(31,32)),((5,11),(25,31)),((1,5),(8,12)),((11,12),(7,8))]
    immB = BitField('immB', immBMAP, 13, 32, True)

    immUMAP = [((12,32),(12,32))]
    immU = BitField('immU', immUMAP, 32, 32, True)

    immJMAP = [((20,21),(31,32)),((1,11),(21,31)),((11,12),(20,21)),((12,20),(12,20))]
    immJ = BitField('immJ', immJMAP, 21, 32, True)

    Umap = {'opcode' : 0, 'rd' : 1, 'immU' : 2}
    U = InstructionType("U", 32, [opcode, rd, immU], Umap)

    Jmap = {'opcode' : 0, 'rd' : 1, 'immJ' : 2}
    J = InstructionType("U", 32, [opcode, rd, immJ], Jmap)

    Rmap = {'opcode': 0, 'funct3': 0, 'funct7':0, 'rd': 1, 'rs1': 2, 'rs2':3}
    R = InstructionType("R", 32, [opcode, funct3, funct7, rd, rs1, rs2], Rmap)

    Imap ={'opcode':0, 'funct3':0, 'rd':1, 'rs1':2, 'immI':3}
    I = InstructionType('I', 32, [opcode, funct3, rd, rs1, immI], Imap)

    Smap = {'opcode':0, 'funct3':0, 'rs1':1, 'rs2':2, 'immS':3}
    S = InstructionType("S", 32, [opcode, funct3, rs1, rs2, immS], Smap)

    Bmap = {'opcode':0, 'funct3':0, 'rs1':1, 'rs2':2, 'immB':3}
    B = InstructionType("B", 32, [opcode, funct3, rs1, rs2, immB], Bmap)


    IRmap = {'opcode':0, 'funct3':0, 'funct7' : 0, 'rd':1, 'rs1':2, 'shamt':3}
    IR = InstructionType('IR', 32, [opcode, funct3, funct7, rd, rs1, shamt], IRmap)

    RISCVmap = {
        'U' : ['LUI', 'AUIPC'],
        'J' : ['JAL'],
        'I' : ['JALR', 'LB', 'LH', 'LW', 'LBU', 'LHU', 'ADDI', 'SLTI', 'SLTIU', 'XORI', 'ORI', 'ANDI'],
        'B' : ['BEQ', 'BNE', 'BLT', 'BGE', 'BLTU', 'BGEU'],
        'S' : ['SB', 'SH', 'SW'],
        'IR': ['SLLI', 'SRLI', 'SRAI'],
        'R' : ['ADD', 'SUB', 'SLL', 'SLT', 'SLTU', 'XOR', 'SRL', 'SRA', 'OR', 'AND']
    }

    RISCV = Assembler('RISCV', [U, J, I, S, B, IR, R], RISCVmap, LittleEndian)
    storeFile = open('RISCV.yo', 'wb')
    pickle.dump(RISCV,storeFile)
    storeFile.close()
    storeFile = open('RISCV.yo', 'rb')
    rs = pickle.load(storeFile)
    storeFile.close()


if __name__ == '__main__':
    PROG = sys.argv[0]
    VERSION = '0.0.0'
    description = "RISC-V 32I instruction set assembly program to simulation ROM (VHDL)"
    
    parser = OptionParser(usage = 'Usage: python %prog <parameters>',
                            version = '%s %s' %(PROG, VERSION),
                            description = description)
                            
    parser.add_option('-i', '--input', action = 'store', dest = 'inFileName', type = 'string',
                        help = 'Name of assembly program file (or path)')
    parser.add_option('-o', '--output', action = 'store', dest = 'outFileName', type = 'string',
                        help = 'Name of VHDL ROM file (or path)')
    parser.add_option('-k', '--keep', action = 'store_true', dest = 'keepIntrFiles',
                        default = False, help = 'Keep Intermediate Files')
                        
    parser.add_option('-r', '--regen', action = 'store_true', dest = 'regen',
                        default = False, help = 'Regenerate assembler object')
                        
    if(len(sys.argv) == 1):
        parser.print_help()
        parser.print_version()
        sys.exit()
        
    (paras, argv) = parser.parse_args()
    
    if argv:
        print('** Error : Please check input parameters')
        sys.exit()
        
    if paras.regen:
        genAssembler()
    
    inFileName = paras.inFileName
    outFileName = paras.outFileName
    keepIntrFiles = paras.keepIntrFiles
    filename, file_extension = os.path.splitext(inFileName)
    
    if not inFileName:
        print("** Error : Please provide assembly file name")
        parser.print_help()
        parser.print_version()
        sys.exit()
        
    if not outFileName:
        outFileName = filename + '.vhd'
    
    intrFile1Name = filename + '_converted.txt'
    intrFile2Name = filename + '_rearenged.txt'
    hexFileName = filename + '.hex'
    
    storeFile = open('RISCV.yo', 'rb')
    assembler = pickle.load(storeFile)
    storeFile.close()
    
    assembler.convASMfile(inFileName, intrFile1Name)
    assembler.rearrengeIns(intrFile1Name, intrFile2Name)
    assembler.generateHexFile(intrFile2Name, hexFileName, 4)
    generateROMsimFromIntrFile(intrFile2Name, outFileName, 32, 1, 8)
    
    if not keepIntrFiles:
        silentremove(intrFile1Name)
        silentremove(intrFile2Name)
