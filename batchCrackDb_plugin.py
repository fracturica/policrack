

from abaqusGui import *
from abaqusConstants import ALL
import osutils
import os
import batchCrackDb
import sharedFunctions

import info


class BatchCrackDb_plugin(AFXForm):
    """
    """
    (ID_LOAD_BUTTON,
     ID_LAST) = range(AFXForm.ID_LAST, AFXForm.ID_LAST+2)

    def __init__(self, owner):
        """
        """
        AFXForm.__init__(self, owner)
        self.previousDialog = None
        self.cmd = AFXGuiCommand(
                mode=self,
                method="batchCreateCrackDb",
                objectName="executeBatchCommands",
                registerQuery=False)
        self.createKeywords()
        FXMAPFUNC(self, SEL_COMMAND, self.ID_LOAD_BUTTON, self.onLoadButton)

    def onLoadButton(self, sender, sel, ptr, a):
        """
        """
        self.dialog1.createLoadDialog()

    def createKeywords(self):
        """
        """
        self.kw = {}
        self.kw["batchConf"] = AFXStringKeyword(
            self.cmd, "batchConf", True, "")
        self.kw["crackReadOnly"] = AFXBoolKeyword(
            self.cmd, "crackReadOnly", True, False)

    def getFirstDialog(self):
        """
        """
        self.cmd.setKeywordValuesToDefaults()
        self.dialog1 = batchCrackDb.SelectCrackParametersFile(self)
        return self.dialog1

    def getNextDialog(self, previousDialog):
        """
        """
        print "getNextDialog"
        self.previousDialog = previousDialog
        self.dialog2 = batchCrackDb.ParameterReviewDialog(self)
        return self.dialog2

    def doCustomChecks(self):
        """
        """
        fileName = self.kw["batchConf"].getValue()
        mainWindow = getAFXApp().getAFXMainWindow()
        if self.previousDialog is None:
            try:
                sharedFunctions.parseInput(fileName)
            except:
                showAFXErrorDialog(
                    mainWindow,
                    "Parsing of the file failed.\n\
                    Check the file and try again!")
                return False
        return True


thisModulePath = os.path.abspath(__file__)
pluginDir = os.path.dirname(thisModulePath)


toolset = getAFXApp().getAFXMainWindow().getPluginToolset()
toolset.registerGuiMenuButton(
    buttonText=info.submenu + 'Create a Batch...',
    object=BatchCrackDb_plugin(toolset),
    messageId=AFXMode.ID_ACTIVATE,
    icon=None,
    kernelInitString='import executeBatchCommands',
    applicableModules=ALL,
    version=info.version,
    author=info.authors,
    description=info.description['batch'],
    helpUrl=info.helpUrl)
