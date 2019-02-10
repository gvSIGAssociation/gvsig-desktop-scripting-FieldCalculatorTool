# encoding: utf-8

import gvsig
from gvsig.libs.formpanel import FormPanel
from org.gvsig.expressionevaluator.swing import ExpressionEvaluatorSwingLocator
from java.awt import BorderLayout
from org.gvsig.fmap.dal.swing import DALSwingLocator
from org.gvsig.fmap.dal.swing import DataSwingManager
from org.gvsig.fmap.dal import DataManager

class FieldCalculatorTool(FormPanel):
  def __init__(self, store):
    FormPanel.__init__(self,gvsig.getResource(__file__,"fieldCalculatorTool.xml"))
    self.store = store
                
    # Expression
    self.expBuilder = ExpressionEvaluatorSwingLocator.getManager().createJExpressionBuilder()
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
    self.pickerField.set(ftype.get(0))
    
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
  l.showTool("Centrar Coordenadas")
  pass