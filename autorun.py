# encoding: utf-8

import gvsig

from org.gvsig.andami import PluginsLocator
from org.gvsig.app import ApplicationLocator
from addons.FieldCalculatorTool.fctool import FieldCalculatorToolExtension

from java.io import File
from org.gvsig.tools.swing.api import ToolsSwingLocator

from gvsig import getResource
from org.gvsig.tools import ToolsLocator
from addons.FieldCalculatorTool.fieldCalculatorToolPreferences import FieldCalculatorToolPreferences

from addons.FieldCalculatorTool.fieldCalculatorToolParameters import FieldCalculatorToolParameters

def selfRegister():
  application = ApplicationLocator.getManager()
  i18n = ToolsLocator.getI18nManager()

  icon_show = File(gvsig.getResource(__file__,"images", "fieldcalculator16x16.png")).toURI().toURL()

  iconTheme = ToolsSwingLocator.getIconThemeManager().getCurrent()
  iconTheme.registerDefault("scripting.field-calculator-tool", "action", "tools-field-calculator-tool", None, icon_show)
  
  extension = FieldCalculatorToolExtension()

  actionManager = PluginsLocator.getActionInfoManager()
  action_show = actionManager.createAction(
    extension, 
    "tools-field-calculator-tool", # Action name
    i18n.getTranslation("_Field_Calculator_Tool"), # Text
    "show", # Action command
    "tools-field-calculator-tool", # Icon name
    None, # Accelerator
    501100000, # Position 
    "_Field_Calculator_Tool" # Tooltip
  )
  action_show = actionManager.registerAction(action_show)
  application.addMenu(action_show, "Table/_Field_Calculator_Tool")
  application.addTool(action_show, "table_tools") #/ )#i18n.getTranslation("_Field_Calculator_Tool"))

def selfRegisterI18n():
  i18nManager = ToolsLocator.getI18nManager()
  i18nManager.addResourceFamily("text",File(getResource(__file__,"i18n")))

def selfRegisterPreferences():
  extensionPointsManager = ToolsLocator.getExtensionPointManager()
  ep = extensionPointsManager.add("AplicationPreferences", "")
  ep.append("fieldExpression", "",FieldCalculatorToolPreferences())

def selfRegisterPersistence():
  fctParameters = FieldCalculatorToolParameters()
  FieldCalculatorToolParameters.registerPersistence(fctParameters)
  
def main(*args):
  #print script, dir(script)
  script.registerDataFolder("FieldCalculatorTool")
  selfRegisterI18n()
  selfRegister()
  selfRegisterPreferences()
  selfRegisterPersistence()