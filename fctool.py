# encoding: utf-8

import gvsig
from gvsig.libs.formpanel import FormPanel
from gvsig import uselib
from java.awt import BorderLayout
from org.gvsig.scripting.app.extension import ScriptingExtension

from org.gvsig.tools import ToolsLocator
from javax.swing import JFrame

from javax.swing import JPanel
from org.gvsig.fmap.dal import DataManager
from org.gvsig.fmap.dal.swing import DataSwingManager
from org.gvsig.tools.swing.api import ToolsSwingLocator
from org.gvsig.tools.swing.api.windowmanager import WindowManager
from org.gvsig.expressionevaluator.swing import ExpressionEvaluatorSwingLocator

from org.gvsig.app.project.documents.table import TableDocument
from org.gvsig.tools.swing.api.windowmanager import WindowManager_v2

from org.gvsig.app.project.documents.table.gui import FeatureTableDocumentPanel

from org.gvsig.andami import PluginServices

from org.gvsig.expressionevaluator import ExpressionEvaluatorLocator

from org.gvsig.fmap.dal import DALLocator

class FieldCalculatorToolExtension(ScriptingExtension):
    def __init__(self):
      pass
      
    def canQueryByAction(self):
      return True
  
    def isEnabled(self,action):
      window = PluginServices.getMDIManager().getActiveWindow()
      if isinstance(window, FeatureTableDocumentPanel):
        columnSelected = window.getTablePanel().getTable().getSelectedColumnCount()
        if columnSelected > 0 and window.getModel().getStore().isEditing():
          return True
      return False
      
    def isVisible(self,action):
      return isinstance(PluginServices.getMDIManager().getActiveWindow(), FeatureTableDocumentPanel)
      
    def execute(self,actionCommand, *args):
      builder = ExpressionEvaluatorSwingLocator.getManager().createJExpressionBuilder() #this.manager, this.config);
      #panel.setExpression(this.value);
      store = gvsig.currentDocument().getFeatureStore()
      builder.addSymbolTable(DataManager.FEATURE_SYMBOL_TABLE)
      swingManager = ExpressionEvaluatorSwingLocator.getManager()
      builder.addElement(
        swingManager.createElement(
            DataSwingManager.FEATURE_STORE_EXPRESSION_ELEMENT,
            builder,
            store
        )
      )
      windowManager = ToolsSwingLocator.getWindowManager()
      dialog = windowManager.createDialog(
                builder.asJComponent(),
                "Expression builder",
                None, 
                WindowManager_v2.BUTTONS_OK_CANCEL
      )
      dialog.show(WindowManager.MODE.DIALOG);
      if dialog.getAction()==WindowManager_v2.BUTTON_OK:
        exp = builder.getExpression()
      else: 
        return
         
      window = PluginServices.getMDIManager().getActiveWindow()
      if isinstance(window, FeatureTableDocumentPanel):
        selected = window.getTablePanel().getTable().getSelectedColumnsAttributeDescriptor()
        if len(selected)<1:
          return
  
        columnSelected = selected[0]
        ftype = store.getDefaultFeatureType()
  
        s =  ExpressionEvaluatorLocator.getManager().createSymbolTable()
        fst = DALLocator.getDataManager().createFeatureSymbolTable()
        s.addSymbolTable(fst)
        store.edit()
        fset = store.getFeatureSet()
        count = 0
        for f in fset:
          fst.setFeature(f)
          v = exp.execute(s) # value de la expression
          c = f.getEditable()
          c.set(columnSelected.getName(), v)
          fset.update(c)

def testApplyExpression():
    phrase = "3*3"
    exp = ExpressionEvaluatorLocator.getManager().createExpression()
    exp.setPhrase(phrase)
    
    store = gvsig.currentDocument().getFeatureStore()
    window = PluginServices.getMDIManager().getActiveWindow()
    if isinstance(window, FeatureTableDocumentPanel):
      selected = window.getTablePanel().getTable().getSelectedColumnsAttributeDescriptor()
      if len(selected)<1:
        return

      columnSelected = selected[0]
      ftype = store.getDefaultFeatureType()

      s =  ExpressionEvaluatorLocator.getManager().createSymbolTable()
      fst = DALLocator.getDataManager().createFeatureSymbolTable()
      s.addSymbolTable(fst)
      store.edit()
      fset = store.getFeatureSet()
      for f in fset:
        fst.setFeature(f)
        v = exp.execute(s) # value de la expression
        c = f.getEditable()
        c.set(columnSelected.getName(), v)
        fset.update(c)


    
      
      
    else:
      print "not"
     
      
        
def main(*args):

  FieldCalculatorToolExtension().execute(None)