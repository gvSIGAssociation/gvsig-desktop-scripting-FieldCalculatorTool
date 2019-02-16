# encoding: utf-8

import gvsig
from org.gvsig.scripting import ScriptingLocator
from ConfigParser import SafeConfigParser
import os

def getConfigFilePath():
  ap = ScriptingLocator.getManager().getDataFolder("FieldCalculatorTool").getAbsolutePath()
  configFile = os.path.join(ap, "configFCT.ini")
  return configFile
  
def readConfigFile():
  parser = SafeConfigParser()
  configFile = getConfigFilePath()
  if os.path.exists(configFile):
    parser.read(configFile) 
    items = dict(parser.items('preferences'))
    items["limit_rows_in_memory"] = int(items["limit_rows_in_memory"])
    value = items["without_limit"]
    if value=="True":
      items["without_limit"]= True
    else:
      items["without_limit"] = False
    return items
  else:
    writeConfigFile(100000, False)
    return readConfigFile()

def writeConfigFile(limit, useNoLimit):
  parser = SafeConfigParser()
  configFile = getConfigFilePath()
  parser.add_section('preferences')
  parser.set('preferences', 'limit_rows_in_memory', str(limit))
  parser.set('preferences', 'without_limit', str(useNoLimit))
  cfgfile = open(configFile,'w')
  parser.write(cfgfile)
  cfgfile.close()
  
def main(*args):

    #Remove this lines and add here your code

    print "hola mundo"
    pass
