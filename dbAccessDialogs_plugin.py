

from abaqusGui import *
from abaqusConstants import ALL
import osutils
import os
import dbAccessDialogs
from kernelAccess import *

import info


class dbAccessDialogs_plugin(AFXForm):
    """
    """
    (ID_DBLIST_SELECT,
     ID_TREE,
     ID_LAST) = range(AFXForm.ID_LAST, AFXForm.ID_LAST+3)

    def __init__(self, owner):
        """
        """
        AFXForm.__init__(self, owner)
        self.previousDialog = None
        self.outputDataKeys = {
            "SIFs": ("K1", "K2", "K3", "Cpd", "JKs"),
            "T-Stress": ("T",),
            "J-Int": ("J",),
            "C-Int": ("C",)}
        self.cmd = AFXGuiCommand(
            mode=self,
            method='readFromDb',
            objectName='executeDbAccessCommands',
            registerQuery=False)
        self.createKeywords()
        FXMAPFUNC(
            self, SEL_COMMAND, self.ID_TREE, self.onTreeSelect)
        FXMAPFUNC(
            self, SEL_COMMAND, self.ID_DBLIST_SELECT, self.onDbListSelect)

    def onDbListSelect(self, sender, sel, ptr, a):
        """
        """
        index = self.dialog1.dbList.getSingleSelection()
        dbName = self.dialog1.dbList.getItemText(index)
        self.kw["dbName"].setValue(dbName)
        self.dialog1.updateWidgets()

    def onTreeSelect(self, sender, sel, ptr, a):
        """
        """
        selectedDbEntries = ()
        dbEntriesQueue = ""
        treeItemIDs = self.dialog2.selectableTreeItemIDs
        tree = self.dialog2.tree
        for itemID in treeItemIDs:
            item = self.dialog2.treeEntries[itemID]
            if tree.isItemSelected(item):
                modelName = self.getModelName(itemID)
                selectedDbEntries += modelName,

        for key in selectedDbEntries:
            dbEntriesQueue += key + "_"
        dbEntriesQueue = dbEntriesQueue[:-1]

        self.kw["dbKeys"].setValue(dbEntriesQueue)
        entries = self.kw["dbKeys"].getValue()

    def getModelName(self, itemID):
        """
        """
        modelName = itemID.split("_")[-1]
        return modelName

    def createKeywords(self):
        """
        """
        self.counter = AFXIntKeyword(self.cmd, "counter", True, 0, True)
        self.kw = {
            "analytical": {},
            "analysis": {},
            "contoursAverage": None}
        self.kw["dbName"] = AFXStringKeyword(
            self.cmd, "dbName", True, "")
        self.kw["dbKeys"] = AFXStringKeyword(
            self.cmd, 'dbKeys', True, "")

        self.kw["contoursToAverage"] = AFXStringKeyword(
            self.cmd, 'contoursToAverage', True, '')
        self.kw["includeContours"] = AFXBoolKeyword(
            self.cmd, "includeContours",
            AFXBoolKeyword.TRUE_FALSE, True, False)
        self.kw["XYPlotData"] = AFXBoolKeyword(
            self.cmd, "XYPlotData",
            AFXBoolKeyword.TRUE_FALSE, True,  False)
        self.kw["VisualizationOdb"] = AFXBoolKeyword(
            self.cmd, "VisualizationOdb",
            AFXBoolKeyword.TRUE_FALSE, True, True)
        self.kw["printData"] = AFXBoolKeyword(
            self.cmd, "printData",
            AFXBoolKeyword.TRUE_FALSE, True, False)
        self.createOutputDataKeywords()

    def createOutputDataKeywords(self):
        """
        """
        aKeys = []
        for key in self.outputDataKeys.keys():
            for aKey in self.outputDataKeys[key]:
                aKeys += aKey,
        for key in aKeys:
            keywordName = key + "analysis"
            self.kw["analysis"][key] = AFXBoolKeyword(
                self.cmd, keywordName,
                AFXBoolKeyword.TRUE_FALSE, True,  False)
        for key in aKeys:
            keywordName = key + "analytical"
            self.kw["analytical"][key] = AFXBoolKeyword(
                self.cmd, keywordName,
                AFXBoolKeyword.TRUE_FALSE, True,  False)

    def updateProgress(self):
        """
        """
        self.dialog1.updateProgress()

    def getFirstDialog(self):
        """
        """
        self.cmd.setKeywordValuesToDefaults()
        self.dialog1 = dbAccessDialogs.SelectDb(self)
        return self.dialog1

    def getNextDialog(self, previousDialog):
        """
        """
        self.previousDialog = previousDialog
        self.dialog2 = dbAccessDialogs.AccessDb(self)
        return self.dialog2

    def doCustomChecks(self):
        """
        """
        if self.previousDialog == self.dialog1:
            dbKeys = self.kw["dbKeys"].getValue()
            contours = self.kw["contoursToAverage"].getValue()
            mainWindow = getAFXApp().getAFXMainWindow()
            if dbKeys == "" and contours != "":
                showAFXErrorDialog(
                    mainWindow,
                    "Select at least one db entry!")
                return False
            elif dbKeys != "" and contours == "":
                showAFXErrorDialog(
                    mainWindow,
                    "Select at least one contour entry!")
                return False
            elif dbKeys == "" and contours == "":
                showAFXErrorDialog(
                    mainWindow,
                    "Select at least one db entry and contour!")
                return False
            else:
                return True
        else:
            return True

    def okToCancel(self):
        return False


thisPath = os.path.abspath(__file__)
thisDir = os.path.dirname(thisPath)

toolset = getAFXApp().getAFXMainWindow().getPluginToolset()
toolset.registerGuiMenuButton(
    buttonText=info.submenu + 'Browse Database...',
    object=dbAccessDialogs_plugin(toolset),
    messageId=AFXMode.ID_ACTIVATE,
    icon=None,
    kernelInitString='import executeDbAccessCommands',
    applicableModules=ALL,
    version=info.version,
    author=info.authors,
    description=info.description['browser'],
    helpUrl=info.helpUrl)
