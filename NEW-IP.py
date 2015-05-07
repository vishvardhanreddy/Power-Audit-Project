import re, os
#================================================================================
def main():
  NODE = {}
  inFile = open('NEW_IP.csv','r')
  for line in inFile:
    line = re.sub('[\n\r]','',line)     # Remove newline & linefeed
    if not re.search(r'^$',line) and not re.search(r'^#',line):
      flds = line.split(',')
      oldNAME = flds[0]
      oldIP   = flds[1]
      newIP   = flds[3]
      newMASK = flds[4]
      newDR   = flds[5]      
      NODE[oldIP] = (newIP,newMASK,newDR)
  inFile.close()
    
  inFile  = open('Area5.csv','r')
  outFile = open('new.Area5.csv','w')
  for line in inFile:
    line = re.sub('[\n\r]','',line)     # Remove newline & linefeed
    if not re.search(r'^$',line) and not re.search(r'^#',line):
      flds = line.split(',')
      ORDER = flds[0]
      NAME  = flds[1]
      oldIP = flds[2]
      newIP = flds[3]
      if ORDER == 'ORDER' or newIP == 'N/A':
        outFile.write(line+'\n')
      elif oldIP:
        tmpStr = ','.join(NODE[oldIP])  
        outFile.write(ORDER+','+NAME+','+oldIP+','+tmpStr+'\n')
  inFile.close()
  outFile.close()
  
#================================================================================
if __name__ == "__main__":
  main()