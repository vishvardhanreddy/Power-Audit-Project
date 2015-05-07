import sys, os, re, time, shutil, ONS
from Tkinter import Tk
from tkFileDialog import askopenfilename

LOGEXT = ".log"
INPUT  = "Optical_Power_Levels.csv"
OUTPUT = "CTP-Attenuator-DCU.csv"

DCU_LOSS = {'DCU-100':    2.1, 
            'DCU-350':    3,
            'DCU-450':    3.5,
            'DCU-550':    3.9,
            'DCU-750':    5,
            'DCU-950':    5.5,
            'DCU-1150':   6.2,
            'DCU-1350':   6.4,
            'DCU-1550':   7.2,
            'DCU-1950':   8.8,
            'DCU-E-200':  5.5,
            'DCU-E-350':  7,
            'DCU-L-300':  3,
            'DCU-L-600':  4.2,
            'DCU-L-700':  4.6,
            'DCU-L-800':  5,      
            'DCU-L-1000': 5.8,
            'DCU-L-1100': 6}
       
#================================================================================
def UPDATE_REPORT(INPUT,OUTPUT, DCUATT):
  try:
    inFile = open(INPUT,'r')
  except IOError:
    print "[ERROR] Cound't open file: " + INPUT
    return None
    
  try:
    outFile = open(OUTPUT,'w')
  except IOError:
    print "[ERROR] Cound't write file: " + OUTPUT
    return False

  for line in inFile:
    line = re.sub('[\n\r]','',line)     # Remove newline & linefeed
    flds = line.split(',')
    if flds[0] == 'TX NODE':
      outFile.write(line+',Attenuator/DCU,Loss (dB)\n')
    elif (flds[0],flds[4],flds[11]) in DCUATT:
      a = DCUATT[flds[0],flds[4],flds[11]].split('|')
      dbLoss = ''
      totalLoss = 0
      for i in range(len(a)):
        tmpLoss = ''
        if a[i].find('DCU') != -1:
          if a[i] in DCU_LOSS:
            totalLoss += DCU_LOSS[a[i]]
            tmpLoss = str(DCU_LOSS[a[i]])
          else:
            tmpLoss = 'ERROR'
        else:
          match = re.search(r'ATT-LC-(\d+)',a[i])
          if match: 
            totalLoss += int(match.group(1))
            tmpLoss = match.group(1)
        dbLoss = dbLoss + '|' + tmpLoss
      dbLoss = dbLoss.replace('|','',1)
      if flds[6] != 'N/A':
        tmpDelta = float(flds[6]) + totalLoss
        flds[6] = str(tmpDelta)
      outFile.write(','.join(flds)+','+DCUATT[flds[0],flds[4],flds[11]]+','+dbLoss+'\n')
    else:  
      outFile.write(line+'\n')
      
  outFile.close()
  inFile.close()
  return True

#================================================================================
def read_PACTCHCORD(filename):    
  DATA = {}
  try:
    inFile = open(filename,'r')
  except IOError:
    print "[ERROR] Cound't open file: " + filename
    return None

  for line in inFile:
    line = re.sub('[\n\r]','',line)     # Remove newline & linefeed
    if not re.search(r'^$',line) and not re.search(r'^#',line) and not re.search(r'^Name,',line):
      flds = line.split(',')
      if flds[0]:
        NODE = flds[0]
      
      A = ''
      Z = ''
      match = re.search(r'(Shelf Assembly|Chassis)\s(\d+).Slot\s(\d+)',flds[2])
      if match:
        PORT = flds[4]
        if PORT.find('SFP') != -1:
          PORT = PORT.replace('SFP','').split('_')[0]
          A = match.group(2) + '/' + match.group(3) + '-' + PORT + '/' + PORT
        else:
          A = match.group(2) + '/' + match.group(3) + '/' + flds[4]
      match = re.search(r'(Shelf Assembly|Chassis)\s(\d+).Slot\s(\d+)',flds[6])
      if match:
        PORT = flds[8]
        if PORT.find('SFP') != -1:
          PORT = PORT.replace('SFP','').split('_')[0]
          Z = match.group(2) + '/' + match.group(3) + '-' + PORT + '/' + PORT
        else:
          Z = match.group(2) + '/' + match.group(3) + '/' + flds[8]

      if flds[5].find('ATT') != -1:
        DATA[NODE,A,Z] = flds[5]
      
      if flds[3].find('DCU-') != -1 and flds[7].find('DCU-') == -1:
        inDCU = True
        DCU_Z = Z
        DCU = flds[3]
      if flds[3].find('DCU-') != -1 and flds[7].find('DCU-') != -1 and inDCU:
        DCU = DCU + "|" + flds[3]        
      if flds[3].find('DCU-') == -1 and flds[7].find('DCU-') != -1:
        inDCU = False
        DCU_A = A  
        DATA[NODE,DCU_A,DCU_Z] = DCU
        
  inFile.close()
  return DATA
  
#================================================================================
def main():
  #========== SELECT CTP PATCHCORD REPORT
  Tk().withdraw()
  filename = askopenfilename()
  if not filename or not filename.endswith('.xls'):
    print "[ERROR] no Excel file is selected"
    raw_input()
    sys.exit(1)
  
  if os.path.dirname(filename).replace('/','\\') != os.path.abspath('./'):
    DELFILE = True
    shutil.copy(filename,'./')
  else: 
    DELFILE = False
  
  filename = filename.split('/')[-1]
  #========== EXTRACT "PATCHCORD INSTALLATION VIEW"
  tabName = 'Patchcord installation view'
  os.system('cscript ' + ONS.resource_path('Scripts/XLS2CSV.vbs') + ' "'+filename+'" "'+tabName+ '" >NUL')
  
  DCUATT = read_PACTCHCORD(tabName+'.csv')
  if os.path.exists(tabName+'.csv'):
    os.remove(tabName+'.csv')
  if DELFILE:
    os.remove(filename)

  if not UPDATE_REPORT(INPUT,OUTPUT,DCUATT):
    raw_input()
    sys.exit(1)
  
  if os.path.exists(OUTPUT):
    os.system("cscript ./Scripts/CSV2XLS-PowerLevel.vbs " + OUTPUT)    
  if os.path.exists(OUTPUT):
    os.remove(OUTPUT)
 
#================================================================================
if __name__ == "__main__":
  main()