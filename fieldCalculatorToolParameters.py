# encoding: utf-8

import gvsig
import sys
from org.gvsig.tools.persistence import Persistent
from org.gvsig.tools import ToolsLocator
from java.lang import String
from org.gvsig.fmap.dal.feature import FeatureQuery

from gvsig import logger
from gvsig import LOGGER_WARN,LOGGER_INFO,LOGGER_ERROR
from org.gvsig.app import ApplicationLocator

from java.lang import StringBuilder

import java.lang.Exception
import java.lang.Throwable

from java.lang import Throwable

class FieldCalculatorToolParameters(Persistent):
  def __init__(self, name=None, exp=None, comboFilterResults=None, filterResults=None):
    self.name = name
    self.exp=exp
    self.comboFilterResults=comboFilterResults
    self.filterResults=filterResults
    
  def getName(self):
    return self.name

  def setName(self, newName):
    self.name=newName

  def getExp(self):
    return self.exp

  def setExp(self, newExp):
    self.exp = newExp

  def getFilterResults(self):
    return self.filterResults

  def setFilterResults(self, newFilterResults):
    self.filterResults=newFilterResults

  def getComboFilterResults(self):
    return self.comboFilterResults

  def setComboFilterResults(self, newComboFilterResults):
    self.comboFilterResults=newComboFilterResults

  def registerPersistence(self):
    persitenceManager = ToolsLocator.getPersistenceManager()
    if persitenceManager.getDefinition("fieldCalculatorTool") == None: 
        definition = persitenceManager.addDefinition(FieldCalculatorToolParameters,
                "FieldCalculatorToolParameters",
                "FieldCalculatorToolParameters persistence definition",
                None,
                None);
        definition.addDynFieldString("name").setMandatory(False)
        definition.addDynFieldString("exp").setMandatory(False)
        definition.addDynFieldInt("comboFilterResults").setMandatory(False)
        definition.addDynFieldString("filterResults").setMandatory(False)
#              definition.addDynFieldMap("values").setClassOfItems(String.class);
#              definition.addDynFieldObject("query").setClassOfValue(FeatureQuery.class).setMandatory(false);
#              definition.addDynFieldString("name").setClassOfValue(String.class);
#              definition.addDynFieldInt("searchMode").setClassOfValue(Integer.class);

  def saveToState(self, state):
    logger("saveToState", LOGGER_INFO)
    state.setValue("name", self.name)
    state.setValue("exp", self.exp)
    state.setValue("comboFilterResults", self.comboFilterResults)
    state.setValue("filterResults", self.filterResults)

#          HashMap<String, String> valuesMap = new HashMap<>();
#          for (String key : this.values.keySet()) {
#              JsonObject value = this.values.get(key);
#              valuesMap.put(key, value.toString());
#          }
#          state.set("values", valuesMap);
#          state.set("query", this.query);
#          state.set("name", this.name);
#          state.set("searchMode", this.searchMode);

  def loadFromState(self, state):
    logger("loadFromState", LOGGER_INFO)
    self.name = state.getString("name")
    self.exp = state.getString("exp")
    self.comboFilterResults = state.getInt("comboFilterResults")
    self.filterResults = state.getString("filterResults")
#          this.resultColumnNames = new ArrayList<>(state.getList("resultColumnNames"));
#          Map<String, String> valuesState = state.getMap("values");
#          HashMap<String, JsonObject> valuesMap = new HashMap<>();
#  
#          for (String key : valuesState.keySet()) {
#              String value = valuesState.get(key);
#              InputStream targetStream = new ByteArrayInputStream(value.getBytes());
#              JsonReader reader = Json.createReader(targetStream);
#              JsonObject jsonObject = reader.readObject();
#              valuesMap.put(key, jsonObject);
#          }
#  
#          this.values = valuesMap;
#          this.query = (FeatureQuery) state.get("query");
#          self.name = state.getString("name");
#          try {
#              this.searchMode = state.getInt("searchMode");
#          } catch(Exception ex) {
#              this.searchMode = DefaultSearchPanel.PANEL_SIMPLIFIED;
#          }

  def getCopy(self):
    try:
      return self.clone()
    except:
      return None

  def toString(self):
    i18nManager = ToolsLocator.getI18nManager()
    if self.exp != None:
      try:
        builder = StringBuilder()
        
        if self.exp != None:
          builder.append(self.exp)
          builder.append(", ")
          
        if self.name != None:
          builder.append("Field: ")
          builder.append(self.name)
          builder.append(", ")
          
        if self.comboFilterResults != None:
          builder.append("Filter: ")
          if self.comboFilterResults == 0:
            builder.append(i18nManager.getTranslation("_use_selection"))
          if self.comboFilterResults == 1:
            builder.append(i18nManager.getTranslation("_use_filter"))
          else:
            builder.append(i18nManager.getTranslation("_use_all"))
          builder.append(", ")

        if self.filterResults != None:
          builder.append(self.filterResults)
        if self.filterResults == None: 
          builder.append("None")

        return builder.toString()
      except java.lang.Throwable, ex:
        logger("Error creando bookmarks1.", LOGGER_WARN, ex)
        raise ex
      except:
        ex = sys.exc_info()[1]
        logger("Error creando bookmarks2." + str(ex), gvsig.LOGGER_WARN, ex)
      finally:
        pass

    else:
      logger("Error creando bookmarks3.", LOGGER_WARN)
      return None

