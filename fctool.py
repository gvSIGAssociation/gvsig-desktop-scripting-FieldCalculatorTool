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
import thread
from java.awt.event import ActionListener
from org.gvsig.app.project.documents.table import TableManager

import fieldCalculatorTool
reload(fieldCalculatorTool)
from fieldCalculatorTool import FieldCalculatorTool

class FieldCalculatorToolExtension(ScriptingExtension, ActionListener):
    def __init__(self):
      pass
      
    def canQueryByAction(self):
      return True
  
    def isEnabled(self,action):
      if gvsig.currentDocument(TableManager.TYPENAME)!=None:
        doc = gvsig.currentDocument(TableManager.TYPENAME).getMainWindow()
        return isinstance(doc, FeatureTableDocumentPanel)
      return False
      
      #window = PluginServices.getMDIManager().getActiveWindow()
      #if isinstance(window, FeatureTableDocumentPanel):
      #  columnSelected = window.getTablePanel().getTable().getSelectedColumnCount()
      #  if columnSelected > 0 and window.getModel().getStore().isEditing():
      #    return True
      #return False
      
    def isVisible(self,action):
      if gvsig.currentDocument(TableManager.TYPENAME)!=None:
        doc = gvsig.currentDocument(TableManager.TYPENAME).getMainWindow()
        return isinstance(doc, FeatureTableDocumentPanel)
      return False
      
    def execute(self,actionCommand, *args):
      self.store = gvsig.currentDocument().getFeatureStore()
      i18nManager = ToolsLocator.getI18nManager()
      
      name = i18nManager.getTranslation("_Field_Calculator_Tool")+ ": " + self.store.getName()
      self.taskStatus = ToolsLocator.getTaskStatusManager().createDefaultSimpleTaskStatus(name)
      windowManager = ToolsSwingLocator.getWindowManager()
      self.tool = FieldCalculatorTool(self.store)

      self.expBuilder = self.tool.getExpBuilder()
      self.expFilter = self.tool.getExpFilter()

      self.dialog = windowManager.createDialog(
                self.tool.asJComponent(),
                name,
                None, 
                WindowManager_v2.BUTTONS_APPLY_OK_CANCEL
      )
      self.dialog.addActionListener(self)
      self.dialog.show(WindowManager.MODE.WINDOW)
 
    def actionPerformed(self,*args):
        if self.dialog.getAction()==WindowManager_v2.BUTTON_CANCEL:
          return
        self.expBuilderExpression = self.expBuilder.getExpression()
        self.expFilterExpression = self.expFilter.get()
        table = gvsig.currentDocument(TableManager.TYPENAME)
        if table!=None:
          #selected = table.getMainWindow().getTablePanel().getTable().getSelectedColumnsAttributeDescriptor()
          #if len(selected)<1: return
          columnSelected = self.tool.getFieldName()
          thread.start_new_thread(self.process, (columnSelected, self.store, self.expBuilderExpression, self.expFilterExpression))

    def process(self, columnSelected, store, exp,  expFilter):
        if store.isEditing():
          commitingMode = False
        else:
          commitingMode = True
        ftype = store.getDefaultFeatureType()
        s =  ExpressionEvaluatorLocator.getManager().createSymbolTable()
        fst = DALLocator.getDataManager().createFeatureSymbolTable()
        s.addSymbolTable(fst)
        store.edit()
        if store.getSelection().getSize()==0:
          if expFilter.getPhrase() != "":
            fq = store.createFeatureQuery()
            fq.addFilter(expFilter)
            fq.retrievesAllAttributes()
            fset = store.getFeatureSet(fq)
          else:
            fset = store.getFeatureSet()
        else:
          fset = store.getSelection()
          
        try:
          self.taskStatus.setRangeOfValues(0, fset.getSize())
          self.taskStatus.setCurValue(0)
          self.taskStatus.setAutoremove(True)
          self.taskStatus.add()
          count = 0
          for f in fset:
            fst.setFeature(f)
            v = exp.execute(s) # value de la expression
            c = f.getEditable()
            c.set(columnSelected, v)
            fset.update(c)
            if commitingMode:
              if count % 100000==0:
                fset.commitChanges()
            count +=1
            self.taskStatus.setCurValue(count)
            #self.taskStatus.incrementCurrentValue()
          if commitingMode:
            store.finishEditing()
        except Exception, ex:
          if commitingMode:
            store.cancelEditing()
        finally:
          fset.dispose()
          self.taskStatus.terminate()
      
        
def main(*args):

  FieldCalculatorToolExtension().execute(None)