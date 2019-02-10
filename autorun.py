# encoding: utf-8

import gvsig

from org.gvsig.andami import PluginsLocator
from org.gvsig.app import ApplicationLocator
from fctool import FieldCalculatorToolExtension

from java.io import File
from org.gvsig.tools.swing.api import ToolsSwingLocator

from gvsig import getResource
from org.gvsig.tools import ToolsLocator

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
    1009000000, # Position 
    "Field Calculator Tool" # Tooltip
  )
  action_show = actionManager.registerAction(action_show)
  application.addTool(action_show, i18n.getTranslation("_Field_Calculator_Tool"))

def selfRegisterI18n():
  i18nManager = ToolsLocator.getI18nManager()
  i18nManager.addResourceFamily("text",File(getResource(__file__,"i18n")))
  
def main(*args):
  selfRegisterI18n()
  selfRegister()