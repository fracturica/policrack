

from abaqusGui import *
from abaqusConstants import ALL
import os
import extractResults
import time

import info


class ExtractResults_plugin(AFXForm):
    """
    """
    (ID_ODB_LIST,
     ID_MDB_FILE,
     ID_MDB_METADATA,
     ID_ODB_DESCRIPTION,
     ID_CREATE_DB,
     ID_LAST) = range(AFXForm.ID_LAST, AFXForm.ID_LAST+6)

    def __init__(self, owner):
        """
        """
        AFXForm.__init__(self, owner)
        self.previousDialog = None

        self.cmd = AFXGuiCommand(
            mode=self,
            method="extractData",
            objectName="executeExtractResults",
            registerQuery=False)
        self.createKeywords()

        FXMAPFUNC(
            self, SEL_COMMAND, self.ID_ODB_LIST, self.onOdbList)
        FXMAPFUNC(
            self, SEL_COMMAND, self.ID_ODB_DESCRIPTION, self.onOdbDescription)
        FXMAPFUNC(
            self, SEL_COMMAND, self.ID_MDB_FILE, self.onMdbFile)
        FXMAPFUNC(
            self, SEL_COMMAND, self.ID_MDB_METADATA, self.onMdbMetadata)
        FXMAPFUNC(
            self, SEL_COMMAND, self.ID_CREATE_DB, self.onCreateDb)

    def onCreateDb(self, sender, sel, ptr, a):
        """
        """
        newDbName = self.dialog2.getNewShelveName()
        if newDbName == "" or newDbName in self.dialog2.getListOfDbs():
            mainWindow = getAFXApp().getAFXMainWindow()
            showAFXErrorDialog(
                mainWindow,
                "Select a different name for the new database.")
        else:
            self.dialog2.createNewDb(newDbName)
            self.dialog2.newDbName.setText("")
            self.kw["outputDb"].setValue(newDbName)

    def onMdbMetadata(self, sender, sel, ptr, a):
        """
        """
        self.dialog1.setCompatibilityText()

    def onMdbFile(self, sender, sel, ptr, a):
        """
        """
        self.dialog1.fileSelectDialog()

    def onOdbDescription(self, sender, sel, ptr, a):
        """
        """
        text = self.dialog1.odbDescription.getText()
        self.kw["description"].setValue(text)

    def onOdbList(self, sender, sel, ptr, a):
        """
        """
        print "odb list select"
        selectedOdb = self.dialog1.odbList.getSingleSelection()
        odbName = self.dialog1.odbNames[selectedOdb]
        odbPath = self.dialog1.odbPaths[selectedOdb]
        self.kw["odbName"].setValue(odbName)
        self.kw["odbPath"].setValue(odbPath)

    def createKeywords(self):
        """
        """
        self.kw = {}
        self.kw["odbName"] = AFXStringKeyword(
            self.cmd, "odbName", True, "")
        self.kw["odbPath"] = AFXStringKeyword(
            self.cmd, "odbPath", True, "")
        self.kw["confFile"] = AFXStringKeyword(
            self.cmd, "confFile", True, "")
        self.kw["description"] = AFXStringKeyword(
            self.cmd, "description", True, "")
        self.kw["outputDb"] = AFXStringKeyword(
            self.cmd, "outputDb", True, "")

    def getFirstDialog(self):
        """
        """
        self.cmd.setKeywordValuesToDefaults()
        self.previousDialog = None
        self.dialog1 = extractResults.ExtractResults(self)
        return self.dialog1

    def getNextDialog(self, previousDialog):
        """
        """
        self.previousDialog = self.dialog1
        self.dialog2 = extractResults.PreviewAndSave(self)
        return self.dialog2

    def doCustomChecks(self):
        """
        """
        return True


thisPath = os.path.abspath(__file__)
thisDir = os.path.dirname(thisPath)

toolset = getAFXApp().getAFXMainWindow().getPluginToolset()
toolset.registerGuiMenuButton(
    buttonText=info.submenu + "Postprocess...",
    object=ExtractResults_plugin(toolset),
    kernelInitString="import executeExtractResults",
    messageId=AFXMode.ID_ACTIVATE,
    icon=None,
    applicableModules=ALL,
    version=info.version,
    author=info.authors,
    description=info.description['postprocessor'],
    helpUrl=info.helpUrl)
