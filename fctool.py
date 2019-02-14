# encoding: utf-8

import gvsig
import sys
from gvsig.libs.formpanel import FormPanel
from gvsig import uselib
from java.awt import BorderLayout
from org.gvsig.scripting.app.extension import ScriptingExtension
from gvsig import commonsdialog
from org.gvsig.tools import ToolsLocator
from javax.swing import JFrame
from java.util.prefs import Preferences
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
from gvsig import logger
from gvsig import LOGGER_WARN,LOGGER_INFO,LOGGER_ERROR

import fieldCalculatorTool
reload(fieldCalculatorTool)
from fieldCalculatorTool import FieldCalculatorTool
from org.gvsig.app import ApplicationLocator

class FieldCalculatorToolExtension(ScriptingExtension, ActionListener):
    def __init__(self):
      self.working = False
      
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
      self.document = gvsig.currentDocument(TableManager.TYPENAME)
      
      if self.document==None:
        return
        
      i18nManager = ToolsLocator.getI18nManager()
      
      self.store = self.document.getFeatureStore()
      ## Previusly editing state
      if self.store.isEditing():
        self.editingMode = True
      else:
        self.editingMode = False
      ## Analyce pending changes
      if self.store.getPendingChangesCount() > 0:
        message = i18nManager.getTranslation("_info_confirm_dialog_field_calculator_commit_changes")
        title = ""
        optionType = commonsdialog.WARNING
        messageType = commonsdialog.WARNING
        msgid = "_field_calculator_save_pending_changes_at_finish"
        optionSave = ApplicationLocator.getManager().confirmDialog(message, title, optionType, messageType, msgid)
        if optionSave==commonsdialog.YES:
          pass
        else:
          logger("User changes are not commited and FieldCalculator will commit all this changes", LOGGER_WARN)
          return 
      ##
      
      name = i18nManager.getTranslation("_Field_Calculator_Tool")+ ": " + self.store.getName()
      self.taskStatus = ToolsLocator.getTaskStatusManager().createDefaultSimpleTaskStatus("")
      self.taskStatus.setAutoremove(True)
      windowManager = ToolsSwingLocator.getWindowManager()

      # Set first column option
      defaultField = None
      #table = gvsig.currentDocument(TableManager.TYPENAME)
      if self.document!=None:
        selected = self.document.getMainWindow().getTablePanel().getTable().getSelectedColumnsAttributeDescriptor()
        if len(selected)>=1:
          defaultField=selected[0].getName()
          
      # Open tool


      self.tool = FieldCalculatorTool(self.store, self.taskStatus, defaultField)

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
      # Action when cancel
      if self.dialog.getAction()==WindowManager_v2.BUTTON_CANCEL:
        try:
          store.finishEditing()
          if self.editingMode:
            store.edit()
        except:
          pass
        return
      # Action with OK or APPLY
      self.modeExitTool = False
      if self.dialog.getAction()==WindowManager_v2.BUTTON_OK:
        self.modeExitTool=True
      self.expBuilderExpression = self.expBuilder.getExpression()
      self.expFilterExpression = self.expFilter.get()

      try:
        if self.expBuilderExpression.getPhrase()!='' and self.expFilterExpression.getPhrase()!='':
          codeFilter = self.expBuilderExpression.getCode()
          codeExp = self.expFilterExpression.getCode()
      except Exception, ex:
        logger("Not valid expression"+str(ex), LOGGER_ERROR)
        return
      
      if self.document!=None:
        columnSelected = self.tool.getFieldName()
        useSelection = self.tool.getUseSelection()
        if self.working:
          return
        self.working = True
        thread.start_new_thread(self.process, (columnSelected, self.store, self.expBuilderExpression, self.expFilterExpression, useSelection, self.dialog))

    def process(self, columnSelected, store, exp,  expFilter, useSelection, dialog):
        self.taskStatus.restart()
        #dialog.setButtonEnabled(WindowManager_v2.BUTTON_CANCEL, False)
        dialog.setButtonEnabled(WindowManager_v2.BUTTON_OK, False)
        dialog.setButtonEnabled(WindowManager_v2.BUTTON_APPLY, False)
        try:
          ftype = store.getDefaultFeatureType()
          s =  ExpressionEvaluatorLocator.getManager().createSymbolTable()
          fst = DALLocator.getDataManager().createFeatureSymbolTable()
          s.addSymbolTable(fst)
          store.edit()
          # Create fset
          if useSelection:
            fset = store.getSelection()
            if store.getSelection().getSize()==0:
              logger("Selection is empty", LOGGER_WARN)
              return
          else:
            if expFilter.getPhrase() != "":
              fq = store.createFeatureQuery()
              
              fq.addFilter(expFilter)
              fq.retrievesAllAttributes()
              fset = store.getFeatureSet(fq)
            else:
              fset = store.getFeatureSet()
          
          # set taskstatus
          self.taskStatus.setRangeOfValues(0, fset.getSize())
          self.taskStatus.setCurValue(0)
          self.taskStatus.add()
          
          # Limit of changes before commit
          prefs = Preferences.userRoot().node("fieldExpressionOptions")
          limit = prefs.getInt("limit_rows_in_memory", -1)
          
          # Update features
          for f in fset:
            if self.taskStatus.isCancellationRequested():
              break
            fst.setFeature(f)
            v = exp.execute(s) # value de la expression
            c = f.getEditable()
            c.set(columnSelected, v)
            fset.update(c)
            #if commitingMode:
            if limit!=-1 and self.store.getPendingChangesCount() > limit:
                fset.commitChanges()
            #self.taskStatus.setCurValue(count)
            self.taskStatus.incrementCurrentValue()
          
        except Exception, ex:
          ex = sys.exc_info()[1]
          #ex.__class__.__name__, str(ex)
          logger("Exception updated features"+str(ex), LOGGER_ERROR) 

        finally:
          #DisposeUtils.disponseQuetly....(fset)
          fset.dispose()
          if self.modeExitTool:
            try:
              store.finishEditing()
            except:
              logger("Not able to save store changes", LOGGER_ERROR) 
              try:
                store.cancelEditing()
              except:
                logger("Not able to cancel editing", LOGGER_ERROR) 
            if self.editingMode:
              try:
                store.edit()
              except:
                logger("Not able to put store into editing mode", LOGGER_ERROR) 
          else:
            logger("Field Calculator Tool expression applied", LOGGER_INFO)
            if self.editingMode==False:
              try:
                store.finishEditing()
              except:
                logger("Not able to puto layer into editing again", LOGGER_ERROR) 
              
          self.taskStatus.terminate()
          #dialog.setButtonEnabled(WindowManager_v2.BUTTON_CANCEL, True)
          dialog.setButtonEnabled(WindowManager_v2.BUTTON_OK, True)
          dialog.setButtonEnabled(WindowManager_v2.BUTTON_APPLY, True)
          self.working = False
      
        
def main(*args):

  FieldCalculatorToolExtension().execute(None)