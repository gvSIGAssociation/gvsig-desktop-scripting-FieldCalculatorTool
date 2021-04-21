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
from org.gvsig.tools.dispose import DisposeUtils
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
from java.lang import Throwable
import os
import fieldCalculatorTool
reload(fieldCalculatorTool)
from fieldCalculatorTool import FieldCalculatorTool
from org.gvsig.app import ApplicationLocator

from fcutils import readConfigFile

from addons.FieldCalculatorTool.fieldCalculatorToolParameters import FieldCalculatorToolParameters

import java.lang.Exception
import java.lang.Throwable

from java.lang import Throwable

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

      #prefs = readConfigFile()
      self.tool = FieldCalculatorTool(self.store, self.taskStatus, defaultField)

      self.expBuilder = self.tool.getExpBuilder()
      self.expFilter = self.tool.getExpFilter()

      self.dialog = windowManager.createDialog(
                self.tool.asJComponent(),
                name,
                None, 
                WindowManager_v2.BUTTON_CANCEL|WindowManager_v2.BUTTON_APPLY
      )
      self.dialog.addActionListener(self)
      self.dialog.show(WindowManager.MODE.WINDOW)

      self.dialog.setButtonLabel(WindowManager_v2.BUTTON_CANCEL, i18nManager.getTranslation("_close"))
      columnSelectedDescriptor = self.tool.getFieldDescriptor()
      if columnSelectedDescriptor == None:
        self.dialog.setButtonEnabled(WindowManager_v2.BUTTON_APPLY, False)

      self.tool.setDialog(self.dialog)
 
    def actionPerformed(self,*args):
      # Action when cancel
      i18nManager = ToolsLocator.getI18nManager()
      if self.dialog.getAction()==WindowManager_v2.BUTTON_CANCEL:
        try:
          if self.working==True:
            return
          self.store.finishEditing()
          if self.editingMode:
            self.store.edit()
        except:
          pass
        return
      # Action with APPLY
      self.modeExitTool = False
      if self.dialog.getAction()==WindowManager_v2.BUTTON_APPLY:
        self.modeExitTool=True
        fctParameters = FieldCalculatorToolParameters()
        fctParameters.setName(self.tool.pickerField.getName())
        if self.tool.expBuilder.getExpression() != None:
          fctParameters.setExp(self.tool.expBuilder.getExpression().getPhrase())
          fctParameters.setComboFilterResults(self.tool.cmbTypeFilter.getSelectedIndex())
          if self.tool.expFilter.get() != None:
            fctParameters.setFilterResults(self.tool.expFilter.get().getPhrase())
          else:
            fctParameters.setFilterResults(None)
          try:
            if self.tool.history.size()==0:
              self.tool.history.add(fctParameters)
            else:
              lastElementHistory=self.tool.history.get(0) #COGE EL PRIMER ELEMENTO, NO EL ULTIMO
              if fctParameters.toString()!=lastElementHistory.toString():
                self.tool.history.add(fctParameters)
              else:
                logger("Same history", LOGGER_INFO)
          except java.lang.Throwable, ex:
            logger("Error add history", LOGGER_WARN, ex)
            raise ex
          except:
            ex = sys.exc_info()[1]
            logger("Error add history" + str(ex), gvsig.LOGGER_WARN, ex)
          finally:
            pass

            
      self.expBuilderExpression = self.expBuilder.getExpression()
      self.expFilterExpression = self.expFilter.get()

      # Checks if initial params are OK
      ## Expressions
      try:
        #if self.expBuilderExpression.getPhrase()!='':
        codeFilter = self.expBuilderExpression.getCode()
      except:
        ex = str(sys.exc_info()[1])
        info= i18nManager.getTranslation("_Not_valid_expression")
        mss = info+str(ex)
        #info = i18nManager.getTranslation("_Not_valid_expression")+": "+ex[40:95] + (ex[95:] and '..')
        logger(info, LOGGER_ERROR)
        self.taskStatus.restart()
        self.taskStatus.message(info)
        self.taskStatus.terminate()
        return
      ## Check validity of the Filter expression
      try: 
        if self.tool.getFilterType()==1:
         if self.expFilterExpression!=None:
           if not self.expFilterExpression.isPhraseEmpty():
             if not self.expFilterExpression.isEmpty():
               codeExp = self.expFilterExpression.getCode()
      except:
        ex = str(sys.exc_info()[1])
        mss= "Not valid filter expression: "+str(ex)
        info = i18nManager.getTranslation("_Not_valid_filter_expression")+": "+ex[40:95] + (ex[95:] and '..')
        logger(mss, LOGGER_ERROR)
        self.taskStatus.restart()
        self.taskStatus.message(info)
        self.taskStatus.terminate()
        return
      ##
      if self.document!=None:
        columnSelectedDescriptor = self.tool.getFieldDescriptor()
        useFilterType = self.tool.getFilterType()
        if self.working:
          return
        self.working = True # Control working thread
        prefs = readConfigFile()
        if prefs == None:
          self.writeConfigFile(100000, False)
        thread.start_new_thread(self.process, (columnSelectedDescriptor, self.store, self.expBuilderExpression, self.expFilterExpression, useFilterType, self.dialog, prefs))

    def process(self, columnSelectedDescriptor, store, exp,  expFilter, useFilterType, dialog, prefs):
      i18nManager = ToolsLocator.getI18nManager()
      dialog.setButtonEnabled(WindowManager_v2.BUTTON_APPLY, False)
      self.taskStatus.restart()
      # IF column is calculated:
      if columnSelectedDescriptor.isComputed():
        self.taskStatus.message(i18nManager.getTranslation("_Field_is_computed"))
        self.updateCalculatedField(columnSelectedDescriptor, store, exp)
      elif columnSelectedDescriptor.isReadOnly():
        logger("Field is read only and not computed", LOGGER_WARN)
        self.taskStatus.message(i18nManager.getTranslation("_Field_is_read_only_and_not_computed"))
        return
      else:
        self.updateRealField(columnSelectedDescriptor, store, exp,  expFilter, useFilterType, dialog, prefs)

      self.working = False
      self.taskStatus.terminate()
      dialog.setButtonEnabled(WindowManager_v2.BUTTON_OK, True)
      dialog.setButtonEnabled(WindowManager_v2.BUTTON_APPLY, True)

        
    def updateCalculatedField(self,columnSelectedDescriptor, store, exp):
      i18nManager = ToolsLocator.getI18nManager()
      try:
        self.taskStatus.setRangeOfValues(0, 1)
        self.taskStatus.setCurValue(0)
        self.taskStatus.add()
        
        #Process
        newComputed = DALLocator.getDataManager().createFeatureAttributeEmulatorExpression(store.getDefaultFeatureType(),exp)
        
        #Check if required field is himself
        for req in newComputed.getRequiredFieldNames():
          if req == columnSelectedDescriptor.getName():
            mss = i18nManager.getTranslation("_A_computed_field_can_not_have_itself_as_required_field_in_the_expression")
            self.taskStatus.message(mss)
            logger(mss, LOGGER_WARN)
            raise Throwable(mss)
        
        newFeatureType = gvsig.createFeatureType(store.getDefaultFeatureType())
        
        #DefaultEditableFeatureAttributeDescriptor
        efd = newFeatureType.getEditableAttributeDescriptor(columnSelectedDescriptor.getName())
        efd.setFeatureAttributeEmulator(newComputed)

        
        try:
          store.edit()
          store.update(newFeatureType)
          store.commit()
          self.taskStatus.incrementCurrentValue()
          self.taskStatus.message(i18nManager.getTranslation("_Computed_field_updated"))
        except:
          #store.cancelEditing()
          self.taskStatus.message(i18nManager.getTranslation("_Computed_field_calculation_has_some_errors"))
          logger("Not able change Emulatore Expression Attribute in Feature Type", LOGGER_ERROR)
      except:
        pass
      finally:
        if self.editingMode:
          try:
            store.edit()
          except:
            logger("Not able to put store into editing mode", LOGGER_ERROR) 

    def updateRealField(self,columnSelectedDescriptor, store, exp,  expFilter, useFilterType, dialog, prefs):
      i18nManager = ToolsLocator.getI18nManager()
      try:
        ftype = store.getDefaultFeatureType()
        s =  ExpressionEvaluatorLocator.getManager().createSymbolTable()
        fst = DALLocator.getDataManager().createFeatureSymbolTable()
        s.addSymbolTable(fst)
        store.edit()
        #store.beginComplexNotification() #beginEditingGroup("field-calculator-update")
        # Create fset
        if useFilterType==0:
          fset = store.getSelection()
          if store.getSelection().getSize()==0:
            logger("Selection is empty", LOGGER_WARN)
            self.taskStatus.message(i18nManager.getTranslation("_Selection_is_empty"))
            return
        elif useFilterType==1:
          if expFilter!=None and not expFilter.isPhraseEmpty() and not expFilter.isEmpty():
            fq = store.createFeatureQuery()
            fq.addFilter(expFilter)
            fq.retrievesAllAttributes()
            fset = store.getFeatureSet(fq)
          else:
            fset = store.getFeatureSet()
        else:
          fset = store.getFeatureSet()
        # set taskstatus
        self.taskStatus.setRangeOfValues(0, fset.getSize())
        self.taskStatus.setCurValue(0)
        self.taskStatus.add()
        
        # Limit of changes before commit
        limit = prefs["limit_rows_in_memory"]
        
        # Update features
        for f in fset:
          if self.taskStatus.isCancellationRequested():
            break
          fst.setFeature(f)
          v = exp.execute(s) # value de la expression
          c = f.getEditable()
          c.set(columnSelectedDescriptor.getName(), v)
          fset.update(c)
          #if commitingMode:
          if limit!=-1 and self.store.getPendingChangesCount() > limit:
              fset.commitChanges()
          #self.taskStatus.setCurValue(count)
          self.taskStatus.incrementCurrentValue()
        
      except:
        ex = sys.exc_info()[1]
        #ex.__class__.__name__, str(ex)
        logger("Exception updated features: "+str(ex), LOGGER_ERROR) 

      finally:
        #store.endEditingGroup()
        try:
          DisposeUtils.disposeQuietly(fset)
        except:
          logger("Not able to dispone fset", LOGGER_ERROR) 
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


def main(*args):

  FieldCalculatorToolExtension().execute(None)