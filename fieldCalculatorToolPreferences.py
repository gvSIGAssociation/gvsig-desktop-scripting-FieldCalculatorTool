# encoding: utf-8

import gvsig
from gvsig.libs.formpanel import FormPanel, load_icon
from org.gvsig.andami.preferences import AbstractPreferencePage
from org.gvsig.tools import ToolsLocator
from java.util.prefs import Preferences
from org.gvsig.andami.preferences import StoreException
from java.awt import Color, SystemColor, Rectangle
from javax.swing import BorderFactory

from fcutils import readConfigFile
from fcutils import writeConfigFile

class FCTPanel(FormPanel):

  def __init__(self):
      self.prefs = readConfigFile() # dict of values
      FormPanel.__init__(self, gvsig.getResource(__file__, "fieldCalculatorToolPreferences.xml"))
      self.i18nManager = ToolsLocator.getI18nManager()
      self.lblOptionLimit.setText(self.i18nManager.getTranslation("limit_rows_in_memory"))
      self.chbNoLimit.setText(self.i18nManager.getTranslation("without_limit"))
      #self.lblIcon.setIcon(self.load_icon()
      self.lblExplanation.setText("<html>"+self.i18nManager.getTranslation("specifies_the_limit_rows_in_memory_when_the_program_eval_the_expression")+"</html>")

      # Init
      if self.prefs!=None:
        self.initializeDefaults()
      
  def initializeValues(self):
    self.prefs = readConfigFile()
    limit = self.prefs["limit_rows_in_memory"]
    if limit==-1:
      self.chbNoLimit.setSelected(True)
      self.txtLimit.setText(self.i18nManager.getTranslation("without_limit"))
    else:
      self.chbNoLimit.setSelected(False)
      self.txtLimit.setText(str(limit))

  def initializeDefaults(self):
    limit= self.prefs["limit_rows_in_memory"]
    if limit==-1:
      self.chbNoLimit.setSelected(True)
      self.txtLimit.setText(self.i18nManager.getTranslation("without_limit"))
    else:
      self.chbNoLimit.setSelected(False);
      self.txtLimit.setText(str(limit))

  def getLimitNumber(self):
    try:
      text = self.txtLimit.getText()
      numberLimit = int(text)
      return numberLimit
    except:
      return self.getNoLimitValue()
      
  def isNoLimit(self):
    return self.getNoLimitValue()
    
  def getNoLimitValue(self):
    return 500000
    
  def chbNoLimit_change(self,*args):
    if self.chbNoLimit.isSelected():
      self.txtLimit.setText(self.i18nManager.getTranslation("_no_limit_value"))
    else:
      self.txtLimit.setText(str(500000))
      
  def storeValues(self):
    try:
      if self.chbNoLimit.isSelected():
        limit=-1
        useNoLimit = True
      else:
        limit=int(self.txtLimit.getText())
        useNoLimit = False
    except Exception,ex:
      StoreException(self.i18nManager.getTranslation("limit_rows_in_memory")+ str(ex))
    writeConfigFile(limit, useNoLimit)

class FieldCalculatorToolPreferences(AbstractPreferencePage):
  def __init__(self):
      self.fctPanel = FCTPanel()

  def getID(self):
    return "FieldCalculatorToolPreferences"

  def getTitle(self):
    return  ToolsLocator.getI18nManager().getTranslation("limit_rows_in_memory")
    
  def getPanel(self):
    return self.fctPanel.asJComponent()
    
  def initializeValues(self):
    self.fctPanel.initializeValues()
    
  def initializeDefaults(self):
    self.fctPanel.initializeDefaults()
    
  def getIcon(self):
    return load_icon(gvsig.getResource(__file__,"images","expression-field-preferences.png"))
    
  def isValueChanged(self):
    return True
    
  def storeValues(self):
    self.fctPanel.storeValues()
  def setChangesApplied(self):
    self.setChanged(False)
  def isResizeable(self):
    return True

def test():
  print readConfigFile()
  limit = 100000
  useNoLimit = True
  writeConfigFile(limit, useNoLimit)
  print readConfigFile()

def main(*args):
  test()
  return
  l = FieldCalculatorToolPreferences()
  p = FCTPanel(None)
  p.showTool("Visual")
  print p.getPanel()
  pass