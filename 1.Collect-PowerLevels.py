import ONS, os, sys

#================================================================================
def Collector_TL1():
  DEBUG = False
  ECHO  = False
  
  if "--debug" in sys.argv or "--DEBUG" in sys.argv:
    DEBUG = True
  if "--echo" in sys.argv or "--ECHO" in sys.argv:
    ECHO = True
    
  (USERNAME, PASSWORD, TL1PORT) = ONS.read_Settings()
  if os.path.exists("Hosts.txt"):
    hostFILE = "Hosts.txt"
  else:
    hostFILE = raw_input("Hosts Filename: ")
  hosts = ONS.read_HOSTS(hostFILE)
  if not hosts:
    userhost = raw_input("Host Name or IP (; to separate multiple ones): ")
    hosts = userhost.split(';')

  cmds = ["RTRV-EQPT::ALL:100;",
          "RTRV-LNK:::100;",
          "RTRV-LNKTERM::ALL:114;",
          "RTRV-OTS::ALL:100;",
          "RTRV-OCH::ALL:100;",
          "RTRV-PM-ALL::ALL:200::,,,,15-min,,;"]

  if (not hosts) or (not cmds):
    print "[ERROR] No hosts and/or commands can be found"
    raw_input()
    sys.exit(1)
      
  if not os.path.exists("Logs"):
    os.mkdir("Logs")
  i = 0
  print "[Collect TL1 Data]"
  for host in hosts:
    i += 1
    print "...[" + str(i) + "/" + str(len(hosts)) + "] Collecting from : " + host
    tmpHosts = ONS.findallIP(host)
    if len(tmpHosts) == 1 or len(tmpHosts) == 2:
      log = "Logs\\" + tmpHosts[0]+".log"
      if not os.path.exists(log):
        tn = ONS.connectTL1(host,TL1PORT,30,USERNAME,PASSWORD,log)
        if tn:
          tnCMD = ONS.cmdTL1(tn,cmds,log,DEBUG,ECHO)
          tnOUT = ONS.disconnectTL1(tn,host,log,USERNAME)
          if (not tnCMD):
            if os.path.exists(log):
              os.remove(log)

#================================================================================
def main():
  if os.path.exists("!!ERROR_HOSTS.txt"):
    os.remove("!!ERROR_HOSTS.txt")
  Collector_TL1()

  if not os.path.exists("!!ERROR_HOSTS.txt"):
    ONS.ZIP_LOGS("Logs/", "Logs.zip")
  else:
    print ""
    print "[ERROR] One or more nodes failed to be collected. Please run again..."
    raw_input()
    
#================================================================================
if __name__ == "__main__":
  main()
  