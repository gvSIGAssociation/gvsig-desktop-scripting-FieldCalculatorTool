# encoding: utf-8

import gvsig
from gvsig.libs.formpanel import FormPanel
from org.gvsig.expressionevaluator.swing import ExpressionEvaluatorSwingLocator
from java.awt import BorderLayout
from org.gvsig.fmap.dal.swing import DALSwingLocator
from org.gvsig.fmap.dal.swing import DataSwingManager
from org.gvsig.fmap.dal import DataManager
from org.gvsig.tools import ToolsLocator
from gvsig import logger
from gvsig import LOGGER_WARN,LOGGER_INFO,LOGGER_ERROR
from org.gvsig.fmap.dal import DALLocator
from javax.swing import ButtonGroup
from javax.swing.event import ChangeListener
from org.gvsig.tools.swing.api import ToolsSwingLocator
from java.lang import Object

from java.awt.event import ActionListener
from org.gvsig.tools.swing.api.bookmarkshistory import ActionEventWithCurrentValue
from addons.FieldCalculatorTool.fieldCalculatorToolParameters import FieldCalculatorToolParameters
from org.gvsig.expressionevaluator import ExpressionEvaluatorLocator

from org.gvsig.tools.swing.api import ListElement

from org.gvsig.tools.swing.api.windowmanager import WindowManager_v2


class TypeFilterCombo(Object):
  def __init__(self, name, filterType):
    self.name = name
    self.filterType = filterType
  def getName(self):
    return self.name
  def getFilterType(self):
    return self.filterType
  def toString(self):
    return self.getName()
    
class SelectionRadioChangeListener(ChangeListener):
  def __init__(self, lblSelection):
    self.lblSelection = lblSelection
  def stateChanged(self,changEvent):
    aButton = changEvent.getSource()
    aModel = aButton.getModel()
    selected = aModel.isSelected()
    self.lblSelection.setEnabled(selected)

class PickerRadioChangeListener(ChangeListener):
  def __init__(self, lblFilter, picker):
    self.lblFilter = lblFilter
    self.picker = picker
  def stateChanged(self,changEvent):
    aButton = changEvent.getSource()
    aModel = aButton.getModel()
    selected = aModel.isSelected()
    self.picker.setEnabled(selected)
    self.lblFilter.setEnabled(selected)

class BookmarksAndHistoryListener(ActionListener):
  def __init__(self, fieldCalculatorToolPanel):
    self.fieldCalculatorToolPanel = fieldCalculatorToolPanel

  def actionPerformed(self, event):
    if event.getID()== ActionEventWithCurrentValue.ID_GETVALUE: #GETVALUE, save parameters
      logger("GETVALUE", LOGGER_INFO)
      actualParams = self.fieldCalculatorToolPanel.fetch()
      event.setCurrentValue(actualParams)

    elif event.getID()== ActionEventWithCurrentValue.ID_SETVALUE: #SETVALUE, load parameters
      logger("SETVALUE", LOGGER_INFO)
      if event.getCurrentValue() == None:
        return
      try:
        oldParams = event.getCurrentValue()
        #searchParams = event.getCurrentValue().getCopy()
      except:
        logger("Not been able to clone export parameters", LOGGER_WARN)
        return
      self.fieldCalculatorToolPanel.clear()
      self.fieldCalculatorToolPanel.put(oldParams)

class FieldCalculatorTool(FormPanel):
  def __init__(self, store, taskStatus=None, defaultField=None):
    FormPanel.__init__(self,gvsig.getResource(__file__,"fieldCalculatorTool.xml"))
    self.store = store
    self.taskStatus = taskStatus
    self.dialog=None
    ## Prepare bind taskTool
    if taskStatus!=None:
      self.fcTaskStatus = ToolsSwingLocator.getTaskStatusSwingManager().createJTaskStatus()
      self.fcTaskStatus.setShowRemoveTaskButton(False)
      self.fcTaskStatus.bind(self.taskStatus)
    else:
      self.fcTaskStatus = None
    i18nManager = ToolsLocator.getI18nManager()
    
    # Update
    self.lblField.setText(i18nManager.getTranslation("_update_field"))
    self.lblObsoleteWarning.setText(i18nManager.getTranslation(self.lblObsoleteWarning.getText()))
    
    # Expression
    ## Sample feature
    sampleFeature = None
    try:
      sampleFeature = store.getFeatureSelection().first()
      if sampleFeature == None:
        sampleFeature = store.first()
    except:
      logger("Not able to create Sample Feature for FieldCalculatorTool", LOGGER_WARN)
    
    ## Set builder
    self.expBuilder = ExpressionEvaluatorSwingLocator.getManager().createJExpressionBuilder()
    if sampleFeature!=None:
      dataManager = DALLocator.getDataManager()
      featureSymbolTable = dataManager.createFeatureSymbolTable()
      featureSymbolTable.setFeature(sampleFeature);
      self.expBuilder.getConfig().setPreviewSymbolTable(featureSymbolTable.createParent())
      
    self.expBuilderStore = DALSwingLocator.getSwingManager().createFeatureStoreElement(self.store)
    self.expBuilder.getConfig().addElement(self.expBuilderStore)

    #swingManager = ExpressionEvaluatorSwingLocator.getManager()
    #element = swingManager.createElement(
    #            DataSwingManager.FEATURE_STORE_EXPRESSION_ELEMENT,
    #            self.expBuilder,
    #            self.store)
    #self.expBuilder.addElement(element)
    
    # Task status
    if self.fcTaskStatus!=None:
      self.pnlTaskStatus.setLayout(BorderLayout())
      self.pnlTaskStatus.add(self.fcTaskStatus.asJComponent())
      self.pnlTaskStatus.updateUI()

    # Filter picker
    self.expFilter = ExpressionEvaluatorSwingLocator.getManager().createExpressionPickerController(self.txtExp, self.btnExp)
        
    #swingManager = ExpressionEvaluatorSwingLocator.getManager()
    #element = swingManager.createElement(
    #            DataSwingManager.FEATURE_STORE_EXPRESSION_ELEMENT,
    #            self.expFilter,
    #            self.store)
    #self.expFilter.addElement(element)

    self.expFilterStore = DALSwingLocator.getSwingManager().createFeatureStoreElement(self.store)
    self.expFilter.getConfig().addElement(self.expFilterStore)
    #self.expFilterStore.setFeatureStore(self.store)
    
    # Combo filter type 
    options = {
               0:i18nManager.getTranslation("_use_selection"),
               1:i18nManager.getTranslation("_use_filter"),
               2:i18nManager.getTranslation("_use_all")
               }
    for op in options:
      self.cmbTypeFilter.addItem(TypeFilterCombo(options[op],op))
    
    if self.store.getSelection().getSize()!=0:
      self.cmbTypeFilter.setSelectedIndex(0)
    else:
      self.cmbTypeFilter.setSelectedIndex(2)

    # Combo picker field
    #self.cmbField.addItem(None)
    self.pickerField = DALSwingLocator.getSwingManager().createAttributeDescriptorPickerController(self.cmbField)
    ftype = self.store.getDefaultFeatureType()
    self.pickerField.setFeatureType(ftype)
    #noneElement=ListElement("",None)
    #self.cmbField.getModel().addElement(noneElement)
    
    if defaultField!=None:
      self.pickerField.set(defaultField)
    else:
      self.pickerField.set(None)

    # Add history and bookmarks
    self.bookmarks = ToolsLocator.getBookmarksAndHistoryManager().getBookmarksGroup("fieldCalculatorTool")
    self.history = ToolsLocator.getBookmarksAndHistoryManager().getHistoryGroup("fieldCalculatorTool")

    self.bookmarksController = ToolsSwingLocator.getToolsSwingManager().createBookmarksController(self.bookmarks, self.btnBookmarks)
    self.historyController = ToolsSwingLocator.getToolsSwingManager().createHistoryController(self.history, self.btnHistory)

    #self.historyController.setFilter(None)

    self.historyController.addActionListener(BookmarksAndHistoryListener(self))
    self.bookmarksController.addActionListener(BookmarksAndHistoryListener(self))

    # Init defaults
    self.cmbField_change()
    self.cmbTypeFilter_change()


    self.pnl1.setLayout(BorderLayout())
    self.pnl1.add(self.expBuilder.asJComponent())
    self.pnl1.updateUI()
    
  def cmbField_change(self,*args):
    try:
      if self.pickerField.get().isComputed():
        self.cmbTypeFilter.setSelectedIndex(2)
        self.cmbTypeFilter.setEnabled(False)
      else:
        self.cmbTypeFilter.setEnabled(True)
      self.updateEnableApplyButton()
    except:
      pass

  def cmbTypeFilter_change(self,*args):
    try:
      if self.expFilter ==None: return
      if self.cmbTypeFilter.getSelectedItem().getFilterType()==1:
        self.expFilter.setEnabled(True)
      else:
        self.expFilter.setEnabled(False)
    except:
      pass
      
  def getFilterType(self,*args):
   return self.cmbTypeFilter.getSelectedItem().getFilterType()

  def getFieldName(self, *args):
    return self.pickerField.getName()
  def getFieldDescriptor(self, *args):
    return self.pickerField.get()
  def getExpBuilder(self, *args):
    return self.expBuilder
  def getExpFilter(self, *args):
    return self.expFilter
  def btnClose_click(self,*args):
    self.hide()

  def fetch(self): #Save fieldCalculatorToolParameters 
    if self.expBuilder.getExpression() != None:
      fctParameters = FieldCalculatorToolParameters()
      fctParameters.setName(self.pickerField.getName())
      fctParameters.setExp(self.expBuilder.getExpression().getPhrase())
      fctParameters.setComboFilterResults(self.cmbTypeFilter.getSelectedIndex())
      if self.expFilter.get() != None:
        fctParameters.setFilterResults(self.expFilter.get().getPhrase())
      else:
        fctParameters.setFilterResults(None)
      return fctParameters
    else:
      return None

  def clear(self): #Clear all fieldCalculatorTool elements.
    self.pickerField.set(None)
    self.expBuilder.getConfig().removeAllElements()
    self.cmbTypeFilter.setSelectedIndex(2)
    self.expFilter.getConfig().removeAllElements()

  def put(self, fctParameters): #Put fieldCalculatorToolParameter on his elements
    expressionEvaluatorManager = ExpressionEvaluatorLocator.getExpressionEvaluatorManager()
    self.pickerField.set(fctParameters.getName())
    self.updateEnableApplyButton()
    #construir expresion a partir de String fctParameters.getExp()
    newExpression = expressionEvaluatorManager.createExpression()
    newExpression.setPhrase(fctParameters.getExp())
    self.expBuilder.setExpression(newExpression)
    self.cmbTypeFilter.setSelectedIndex(fctParameters.getComboFilterResults())
    newExpFilter = expressionEvaluatorManager.createExpression()
    newExpFilter.setPhrase(fctParameters.getFilterResults())
    self.expFilter.set(newExpFilter)
    self.expFilterStore = DALSwingLocator.getSwingManager().createFeatureStoreElement(self.store)
    self.expFilter.getConfig().addElement(self.expFilterStore)

  def setDialog(self,dialog):
    self.dialog = dialog

  def updateEnableApplyButton(self):
    if self.dialog == None:
      return
    if self.pickerField.get()==None:
      self.dialog.setButtonEnabled(WindowManager_v2.BUTTON_APPLY, False);
    else:
      self.dialog.setButtonEnabled(WindowManager_v2.BUTTON_APPLY, True);


def main(*args):
  store = gvsig.currentLayer().getFeatureStore()
  l = FieldCalculatorTool(store)
  l.showTool("Testing")
  pass