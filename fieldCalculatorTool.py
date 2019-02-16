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

class FieldCalculatorTool(FormPanel):
  def __init__(self, store, taskStatus=None, defaultField=None):
    
    FormPanel.__init__(self,gvsig.getResource(__file__,"fieldCalculatorTool.xml"))
    self.store = store
    self.taskStatus = taskStatus
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
    #self.lblFilter.setText()
    #self.lblSelection.setText()

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
      self.expBuilder.setPreviewSymbolTable(featureSymbolTable.createParent())
      
    #self.expBuilder.addSymbolTable(DataManager.FEATURE_SYMBOL_TABLE)
    swingManager = ExpressionEvaluatorSwingLocator.getManager()
    element = swingManager.createElement(
                DataSwingManager.FEATURE_STORE_EXPRESSION_ELEMENT,
                self.expBuilder,
                self.store)
    self.expBuilder.addElement(element)
    
    self.pnl1.setLayout(BorderLayout())
    self.pnl1.add(self.expBuilder.asJComponent())
    self.pnl1.updateUI()

    # Task status
    if self.fcTaskStatus!=None:
      self.pnlTaskStatus.setLayout(BorderLayout())
      self.pnlTaskStatus.add(self.fcTaskStatus.asJComponent())
      self.pnlTaskStatus.updateUI()
    
    # Filter picker
    self.expFilter = ExpressionEvaluatorSwingLocator.getManager().createExpressionPickerController(self.txtExp, self.btnExp)
        
    swingManager = ExpressionEvaluatorSwingLocator.getManager()
    element = swingManager.createElement(
                DataSwingManager.FEATURE_STORE_EXPRESSION_ELEMENT,
                self.expFilter,
                self.store)
    
    self.expFilter.addElement(element)
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
    self.pickerField = DALSwingLocator.getSwingManager().createAttributeDescriptorPickerController(self.cmbField)
    ftype = self.store.getDefaultFeatureType()
    self.pickerField.setFeatureType(ftype)
    if defaultField!=None:
      self.pickerField.set(defaultField)
    else:
      self.pickerField.set(ftype.get(0))

    # Init defaults
    self.cmbField_change()
    self.cmbTypeFilter_change()
    
  def cmbField_change(self,*args):
    try:
      if self.pickerField.get().isComputed():
        self.cmbTypeFilter.setSelectedIndex(2)
        self.cmbTypeFilter.setEnabled(False)
      else:
        self.cmbTypeFilter.setEnabled(True)
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

def main(*args):
  store = gvsig.currentLayer().getFeatureStore()
  l = FieldCalculatorTool(store)
  l.showTool("Testing")
  pass