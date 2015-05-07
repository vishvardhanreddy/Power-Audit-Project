import sys, os, re, time, ONS
from ONS_RTRV import find_EQPT
from ONS_RTRV import find_SHELF_SLOT_PORTNAME
from ONS_RTRV import read_EQPT
from ONS_RTRV import read_PORTNAME4TL1
from ONS_RTRV import link_LNK
from ONS_RTRV import link_LNKTERM
from ONS_RTRV import power_OTS
from ONS_RTRV import power_OCH
from ONS_RTRV import power_PM_ALL

LOGEXT = ".log"
REPORT = "Optical_Power_Levels.csv"

#================================================================================
def optical_power_level(EQPT,LINK,PORT,OTS,OCH,PM):
  try:
    outFile = open(REPORT,'w')
  except IOError:
    print "[ERROR] Cound't write file: " + REPORT
    return False
  outFile.write("TX NODE,TYPE,TX,TX EQPT,TX SHELF/ SLOT/ PORT,TX POWER (dBm),Difference (dB),RX POWER (dBm),RX NODE,RX,RX EQPT,RX SHELF/ SLOT/ PORT\n")

  POWERS = {}
  for i in LINK:
    (ANODE,TX,ZNODE,RX) = i
    if not ZNODE:
      ZNODE = ANODE
      
    TYPE = LINK[i][0]
    WLEN = LINK[i][1]
          
    #========== MATCHING EQPT
    TXEQPT = find_EQPT(ANODE,TX,EQPT)
    RXEQPT = find_EQPT(ZNODE,RX,EQPT)

    #========== MATCHING SHELF/SLOT/PORT/WAVELENGTH
    (TXSHELF,TXSLOT,TXPORT) = find_SHELF_SLOT_PORTNAME(ANODE,TX,EQPT,PORT)
    (RXSHELF,RXSLOT,RXPORT) = find_SHELF_SLOT_PORTNAME(ZNODE,RX,EQPT,PORT)

    if TXEQPT:
      TXPORT = TXSHELF+'/'+TXSLOT+'/'+TXPORT
      if len(TXSLOT) == 1:
        TXSORT = TXSHELF+'/0'+TXSLOT+'/'+TXPORT
      else:
        TXSORT = TXSHELF+'/'+TXSLOT+'/'+TXPORT
    else:
      TXPORT = ""
      TXSORT = "X"
    if RXEQPT:
      RXPORT = RXSHELF+'/'+RXSLOT+'/'+RXPORT
      if len(RXSLOT) == 1:
        RXSORT = RXSHELF+'/0'+RXSLOT+'/'+RXPORT
      else:
        RXSORT = RXSHELF+'/'+RXSLOT+'/'+RXPORT
    else:
      RXPORT = ""
      RXSORT = "X"
        
    if WLEN:
      TXPORT = TXPORT + " (" + WLEN + ")"
      RXPORT = RXPORT + " (" + WLEN + ")"
      
    #========== MATCHING OPTICAL POWER from OTS, OCH & PM
    if ANODE != ZNODE:  #===== HANDLE PPC POWER
      PPCTX = 'CHAN-'+'-'.join(TX.split('-')[1:])
      PPCRX = 'CHAN-'+'-'.join(RX.split('-')[1:])
    else:
      PPCTX = ''
      PPCRX = ''

    if (ANODE,TX) in OTS:         #===== OTS POWER
      TXPWR = OTS[ANODE,TX]
    elif (ANODE,TX,"TX") in OCH:  #===== NORMAL OCH POWER
      TXPWR = OCH[ANODE,TX,"TX"]
    elif (ANODE,TX) in OCH:       #===== OCH ADDPOWER
      TXPWR = OCH[ANODE,TX]
      if TXPWR.find('|||||ADDPOWER') != -1:
         TXPWR = TXPWR.replace('|||||ADDPOWER','')
         TXPORT = TXPORT + ' (ADD POWER)'
    elif (ANODE,PPCTX,"TX") in OCH: #===== PPC OCH POWER
      TXPWR = OCH[ANODE,PPCTX,"TX"]
    elif (ANODE,TX,"TX") in PM:   #===== PM-ALL POWER
      TXPWR = PM[ANODE,TX,"TX"]
    else:
      TXPWR = 'N/A'

    if (ZNODE,RX) in OTS:         #===== OTS POWER
      RXPWR = OTS[ZNODE,RX]
    elif (ZNODE,RX,"RX") in OCH:  #===== NORMAL OCH POWER
      RXPWR = OCH[ZNODE,RX,"RX"]
    elif (ZNODE,RX) in OCH:       #===== OCH ADDPOWER
      RXPWR = OCH[ZNODE,RX]
      if RXPWR.find('|||||ADDPOWER') != -1:
        RXPWR = RXPWR.replace('|||||ADDPOWER','')
        RXPORT = RXPORT + ' (ADD POWER)'
    elif (ZNODE,PPCRX,"RX") in OCH: #===== PPC OCH POWER
      RXPWR = OCH[ZNODE,PPCRX,"RX"]
    else:
      RXPWR = 'N/A'
      
    if TXPWR == 'N/A' or RXPWR == 'N/A':
      DELTA = 'N/A'
    else:
      DELTA = float(RXPWR) - float(TXPWR)
    
    if ANODE == ZNODE:
      ZNODE = ""
    POWERS[ANODE,TXSORT,ZNODE,RXSORT] = (ANODE,TYPE,TX,TXEQPT,TXPORT,ZNODE,RX,RXEQPT,RXPORT,TXPWR,RXPWR,str(DELTA))
  
  #========== FIND DC-TX to DC-RX
  for i in OTS:
    if len(i) == 3 and i[2] == "DCU" and OTS[i][0] != "N/A" and OTS[i][1] != "N/A":
      NODE = i[0]
      TX = i[1]+'-TX'
      RX = i[1]+'-RX'
      #========== MATCHING EQPT
      TXEQPT = find_EQPT(NODE,TX,EQPT)
      RXEQPT = find_EQPT(NODE,RX,EQPT)

      #========== MATCHING SHELF/SLOT/PORT
      (TXSHELF,TXSLOT,TXPORT) = find_SHELF_SLOT_PORTNAME(NODE,TX,EQPT,PORT)
      (RXSHELF,RXSLOT,RXPORT) = find_SHELF_SLOT_PORTNAME(NODE,RX,EQPT,PORT)

      if TXEQPT:
        TXPORT = TXSHELF+'/'+TXSLOT+'/'+TXPORT
      else:
        TXPORT = ""
      if RXEQPT:
        RXPORT = RXSHELF+'/'+RXSLOT+'/'+RXPORT
      else:
        RXPORT = ""

      DELTA = float(OTS[i][1])-float(OTS[i][0])
      POWERS[i[0],'M'+i[1],'M'+i[1]] = (NODE,"DC TX-to-RX",i[1]+'-TX',TXEQPT,TXPORT,'',i[1]+'-RX',RXEQPT,RXPORT,OTS[i][0],OTS[i][1],str(DELTA))
   
  for i in sorted(POWERS.keys()):
    #outFile.write(','.join(POWERS[i]) + '\n')
    outFile.write(POWERS[i][0]+','+POWERS[i][1]+','+POWERS[i][2]+','+POWERS[i][3]+','+POWERS[i][4]+','+POWERS[i][9]+','+POWERS[i][11]+','+POWERS[i][10]+','+POWERS[i][5]+','+POWERS[i][6]+','+POWERS[i][7]+','+POWERS[i][8]+'\n')
    
  outFile.close()
  return True
  
#================================================================================
def hasLOG(files):
  for file in files:
    if file.endswith(LOGEXT):
      return True
  return False
#================================================================================
def main():
  CLEAR = ""
  if len(sys.argv) == 2:
    if sys.argv[1] == "--noclear" or sys.argv[1] == "--NOCLEAR" :
      CLEAR = False
    if sys.argv[1] == "--clear" or sys.argv[1] == "--CLEAR" :
      CLEAR = True

  #===== FIND LOGS
  logFiles = []
  if os.path.exists("./Logs.zip"):
    ONS.UNZIP_LOGS("./", "Logs.zip")
    CLEAR = True
  elif os.path.exists("../1.Collector/Logs.zip"):
    ONS.UNZIP_LOGS("../1.Collector/", "Logs.zip")
    CLEAR = True

  if os.path.exists("./Logs") and hasLOG(os.listdir("./Logs")):
    logFolder = "./Logs"
    logFiles = os.listdir("./Logs")
  elif os.path.exists("../1.Collector/Logs") and hasLOG(os.listdir("../1.Collector/Logs")):
    logFolder = "../1.Collector/Logs"
    logFiles = os.listdir("../1.Collector/Logs")
  else:
    print "[ERROR] No log folder or files can be found"
    raw_input()
    sys.exit(1)

  hosts = []
  for file in logFiles:
    if file.endswith(LOGEXT):
      hosts.append(file.replace(LOGEXT, ""))

  #===== PROCESS LOGS
  print "[Process Logs Data]"
  i = 0
  for host in hosts:
    i += 1
    print "...[" + str(i) + "/" + str(len(hosts)) + "] Parsing : " + host
    ONS.LOG2CSV_TL1(logFolder+"/"+host+LOGEXT)
  print ""
  
  LINK = {}
  LINK.update(link_LNK("RTRV-LNK.csv"))
  LINK.update(link_LNKTERM("RTRV-LNKTERM.csv"))
  
  EQPT = read_EQPT("RTRV-EQPT.csv")
  PORT = read_PORTNAME4TL1(ONS.resource_path('Scripts\PortMapping.csv'))
  OTS  = power_OTS("RTRV-OTS.csv")
  OCH  = power_OCH("RTRV-OCH.csv")
  PM   = power_PM_ALL("RTRV-PM-ALL.csv")

  optical_power_level(EQPT,LINK,PORT,OTS,OCH,PM)
  
  #===== CREATING EXCEL REPORT
  if os.path.exists(REPORT):
    os.system('cscript ' + ONS.resource_path('Scripts/CSV2XLS-PowerLevel.vbs') + ' '+REPORT+' >NUL')
    #os.remove(REPORT)
    
  #===== CLEAN UP CSV FILES
  for file in os.listdir("./"):
    if file.endswith('.csv') and file.startswith('RTRV-'):
      os.remove(file)
  
  #===== CLEAN UP LOGS
  if CLEAR == "":
    print ""
    prompt = raw_input("...Do you want to clear all logs ([Y]/N)? ")
    if prompt == "" or prompt == "y" or prompt == "Y" or prompt == "yes" or prompt == "YES":
      CLEAR = True
    else:
      CLEAR = False

  if CLEAR:
    for file in logFiles:
      if os.path.exists(logFolder+"/"+file):
        os.remove(logFolder+"/"+file)
    os.rmdir(logFolder)
  
#================================================================================
if __name__ == "__main__":
  main()