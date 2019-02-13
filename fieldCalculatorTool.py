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
  def __init__(self, store, fcTaskStatus=None, defaultField=None):
    FormPanel.__init__(self,gvsig.getResource(__file__,"fieldCalculatorTool.xml"))
    self.store = store
    # Update
    i18nManager = ToolsLocator.getI18nManager()
    self.lblField.setText(i18nManager.getTranslation("_update_field"))
    self.lblFilter.setText(i18nManager.getTranslation("_filter_to_apply"))
    self.lblSelection.setText(i18nManager.getTranslation("_use_selection"))

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
      
    self.expBuilder.addSymbolTable(DataManager.FEATURE_SYMBOL_TABLE)
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
    if fcTaskStatus!=None:
      self.pnlTaskStatus.setLayout(BorderLayout())
      self.pnlTaskStatus.add(fcTaskStatus.asJComponent())
      self.pnlTaskStatus.updateUI()
    
    # Filter picker
    self.expFilter = ExpressionEvaluatorSwingLocator.getManager().createExpressionPickerController(self.txtExp, self.btnExp)
        
    swingManager = ExpressionEvaluatorSwingLocator.getManager()
    element = swingManager.createElement(
                DataSwingManager.FEATURE_STORE_EXPRESSION_ELEMENT,
                self.expFilter,
                self.store)
    
    self.expFilter.addElement(element)
    
    # Combo picker
    self.pickerField = DALSwingLocator.getSwingManager().createAttributeDescriptorPickerController(self.cmbField)
    ftype = self.store.getDefaultFeatureType()
    self.pickerField.setFeatureType(ftype)
    if defaultField!=None:
      self.pickerField.set(defaultField)
    else:
      self.pickerField.set(ftype.get(0))
    
    # Radiobutton
    #print "size:", store.getSelection().getSize()
    #if store.getSelection().getSize()==0:
    #  self.rdbSelection.setEnabled(False)
    
    self.rdbFilter.setSelected(True)
    self.lblSelection.setEnabled(False)
    self.rdbFilter.addChangeListener(PickerRadioChangeListener(self.lblFilter, self.expFilter))
    self.rdbSelection.addChangeListener(SelectionRadioChangeListener(self.lblSelection))

    bgroup = ButtonGroup()
    #self.rdbFilter.setEnabled(True)
    
    bgroup.add(self.rdbSelection)
    bgroup.add(self.rdbFilter)
  def getUseSelection(self,*args):
    return self.rdbSelection.isSelected()
  def getFieldName(self, *args):
    return self.pickerField.getName()
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