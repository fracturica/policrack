

from abaqusGui import *
from abaqusConstants import ALL
import os
import createCrackDb
import time

import info


class CrackDb_plugin(AFXForm):
    """
    """
    (ID_CRACK_TYPE,
     ID_CRACK_A,
     ID_CRACK_B,

     ID_APPLY_LOADS,

     ID_ANALYSIS_TYPE,
     ID_MESH_DIMENSIONS,
     ID_MESH_SEEDS,

     ID_XFEM_TYPE,
     ID_XFEM_MP_MESH_PARTITIONS,
     ID_XFEM_MP_MESH_SEEDS,

     ID_GENERATE_MDB_NAME,

     ID_LAST) = range(AFXForm.ID_LAST, AFXForm.ID_LAST + 12)

    def __init__(self, owner):
        """
        """
        AFXForm.__init__(self, owner)
        self.previousDialog = None
        self.params = {"maxCrackRatio": 100}

        self.cmd = AFXGuiCommand(
            mode=self,
            method="createCommands",
            objectName="executeCreateCrackDbCommands",
            registerQuery=False)

        self.createKeywords()

        FXMAPFUNC(self, SEL_COMMAND, self.ID_CRACK_TYPE, self.onCrackTypeSelect)
        FXMAPFUNC(self, SEL_COMMAND, self.ID_CRACK_A, self.onCrackASelect)
        FXMAPFUNC(self, SEL_COMMAND, self.ID_CRACK_B, self.onCrackBSelect)

        FXMAPFUNC(self, SEL_COMMAND, self.ID_APPLY_LOADS, self.onApplyLoads)

        FXMAPFUNC(self, SEL_COMMAND, self.ID_ANALYSIS_TYPE, self.onAnalysisType)
        FXMAPFUNC(self, SEL_COMMAND, self.ID_MESH_DIMENSIONS, self.onMeshDimensions)
        FXMAPFUNC(self, SEL_COMMAND, self.ID_MESH_SEEDS, self.onMeshSeeds)

        FXMAPFUNC(self, SEL_COMMAND, self.ID_XFEM_TYPE, self.onXfemType)
        FXMAPFUNC(self, SEL_COMMAND, self.ID_XFEM_MP_MESH_PARTITIONS, self.onXfemMPmeshPartitions)
        FXMAPFUNC(self, SEL_COMMAND, self.ID_XFEM_MP_MESH_SEEDS, self.onXfemMPmeshSeeds)

        FXMAPFUNC(self, SEL_COMMAND, self.ID_GENERATE_MDB_NAME, self.onGenerateMdbName)

    def onGenerateMdbName(self, sender, sel, ptr, a):
        """
        """
        sec = time.time()
        sec = str(round(sec, 2))
        rawName = sec.split(".")
        name = rawName[0] + "dot" + rawName[1]
        self.kw["mdbName"].setValue(name)

    def onXfemMPmeshPartitions(self, sender, sel, ptr, a):
        """
        """
        self.dialog2.createXfemMPmeshPartitions()

    def onXfemMPmeshSeeds(self, sender, sel, ptr, a):
        """
        """
        self.dialog2.createXfemMPmeshSeeds()

    def onXfemType(self, sender, sel, ptr, a):
        """
        """
        index = self.dialog2.xfemTabBook.getCurrent()
        tabs = {
            "0": "simple",
            "1": "crackPartition",
            "2": "multiplePartitions"}
        self.kw["xfemType"].setValue(tabs[str(index)])

    def onMeshSeeds(self, sender, sel, ptr, a):
        """
        """
        self.dialog2.createFEMmeshSeeds()

    def onMeshDimensions(self, sender, sel, ptr, a):
        """
        """
        self.dialog2.createFEMmeshPartition()

    def onAnalysisType(self, sender, sel, ptr, a):
        """
        """
        index = self.dialog2.tabBook.getCurrent()
        tabs = {
            "0": "FEM",
            "1": "XFEM"}
        self.kw["analysisType"].setValue(tabs[str(index)])

    def onApplyLoads(self, sender, sel, ptr, a):
        """
        """
        print "onApplyLoads"
        print "init value", self.kw["applyLoads"].getValue()
        if self.kw["applyLoads"].getValue() is True:
            self.kw["applyLoads"].setValue(False)
        else:
            self.kw["applyLoads"].setValue(True)
        print "current value", self.kw["applyLoads"].getValue()

        crack = self.kw["crackType"].getValue()
        if self.kw["applyLoads"].getValue() is True:
            self.dialog2.magnitude.enable()
            if crack == "embedded":
                self.dialog2.gamma.enable()
                self.dialog2.omega.enable()
            elif crack == "surface":
                self.dialog2.gamma.enable()
                self.dialog2.omega.disable()
            elif crack == "edge":
                self.dialog2.omega.disable()
                self.dialog2.gamma.disable()
        elif self.kw["applyLoads"].getValue() is False:
            self.dialog2.magnitude.disable()
            self.dialog2.omega.disable()
            self.dialog2.gamma.disable()

    def onCrackTypeSelect(self, sender, sel, ptr, a):
        """
        """
        index = self.dialog2.crackType.getCurrentItem()
        crack = self.dialog2.crackType.getItemText(index)
        self.kw["crackType"].setValue(crack)
        icons = {
            "embedded": self.dialog2.embeddedCI,
            "surface": self.dialog2.surfaceCI,
            "edge": self.dialog2.edgeCI}
        self.dialog2.crackParTable.setItemIcon(
                row=0,
                column=0,
                icon=icons[crack])
        if self.kw["applyLoads"].getValue() is True:
            self.dialog2.gamma.enable()
            self.dialog2.omega.enable()
            if crack == "surface":
                self.kw["omega"].setValue(0)
                self.dialog2.omega.disable()
            elif crack == "edge":
                self.kw["omega"].setValue(0)
                self.dialog2.omega.disable()
                self.kw["gamma"].setValue(0)
                self.dialog2.gamma.disable()

    def onCrackASelect(self, sender, sel, ptr, a):
        """
        """
        self.kw["a"].setValue(self.dialog2.crackA.getValue())
        self.onCrackABchange()

    def onCrackBSelect(self, sender, sel, ptr, a):
        """
        """
        self.kw["b"].setValue(self.dialog2.crackB.getValue())
        self.onCrackABchange()

    def onCrackABchange(self):
        """
        """
        a = self.dialog2.crackA.getValue()
        b = self.dialog2.crackB.getValue()
        self.dialog2.crackInfo.setText("{0}".format(round(a/b, 2)))

    def createKeywords(self):
        """
        """
        self.kw = {}
        self.kw["a"] = AFXFloatKeyword(
            command=self.cmd,
            name="a",
            isRequired=True,
            defaultValue=10.0,
            precision=6)
        self.kw["b"] = AFXFloatKeyword(
            command=self.cmd,
            name="b",
            isRequired=True,
            defaultValue=10.0,
            precision=6)
        self.kw["crackType"] = AFXStringKeyword(
            command=self.cmd,
            name="crackType",
            isRequired=True,
            defaultValue="embedded")

        self.kw["containerH"] = AFXFloatKeyword(
            command=self.cmd,
            name="containerH",
            isRequired=True,
            defaultValue=50,
            precision=6)
        self.kw["containerD"] = AFXFloatKeyword(
            command=self.cmd,
            name="containerD",
            isRequired=True,
            defaultValue=50,
            precision=6)

        self.kw["materialName"] = AFXStringKeyword(
            command=self.cmd,
            name="materialName",
            isRequired=True,
            defaultValue="steel")
        self.kw["eModulus"] = AFXFloatKeyword(
            command=self.cmd,
            name="eModulus",
            isRequired=True,
            defaultValue=200000,
            precision=6)
        self.kw["vRatio"] = AFXFloatKeyword(
            command=self.cmd,
            name="vRatio",
            isRequired=True,
            defaultValue=0.3,
            precision=6)

        self.kw["applyLoads"] = AFXBoolKeyword(
            command=self.cmd,
            name="applyLoads",
            isRequired=True,
            defaultValue=True)
        self.kw["sigma"] = AFXFloatKeyword(
            command=self.cmd,
            name="sigma",
            isRequired=True,
            defaultValue=100,
            precision=6)
        self.kw["gamma"] = AFXFloatKeyword(
            command=self.cmd,
            name="gamma",
            isRequired=True,
            defaultValue=0,
            precision=6)
        self.kw["omega"] = AFXFloatKeyword(
            command=self.cmd,
            name="omega",
            isRequired=True,
            defaultValue=0,
            precision=6)

        self.kw["analysisType"] = AFXStringKeyword(
            command=self.cmd,
            name="analysisType",
            isRequired=True,
            defaultValue="FEM")
        self.kw["xfemType"] = AFXStringKeyword(
            command=self.cmd,
            name="xfemType",
            isRequired=True,
            defaultValue="simple")
        self.kw["femElements"] = AFXStringKeyword(
            command=self.cmd,
            name="femElements",
            isRequired=True,
            defaultValue="LinearRI - C3D8R")

        self.kw["crackTipScale"] = AFXFloatKeyword(
            command=self.cmd,
            name="crackTipScale",
            isRequired=True,
            defaultValue=1.0,
            precision=6)
        self.kw["crackZoneScale"] = AFXFloatKeyword(
            command=self.cmd,
            name="crackZoneScale",
            isRequired=True,
            defaultValue=1.0,
            precision=6)
        self.kw["arcSeeds"] = AFXFloatKeyword(
            command=self.cmd,
            name="arcSeeds",
            isRequired=True,
            defaultValue=5)
        self.kw["crackZoneSeeds"] = AFXFloatKeyword(
            command=self.cmd,
            name="crackZoneSeeds",
            isRequired=True,
            defaultValue=5)
        self.kw["containerRefinementSeeds"] = AFXFloatKeyword(
            command=self.cmd,
            name="containerRefinementSeeds",
            isRequired=True,
            defaultValue=5)
        self.kw["crackZoneRefinementSeeds"] = AFXFloatKeyword(
            command=self.cmd,
            name="crackZoneRefinementSeeds",
            isRequired=True,
            defaultValue=3)
        self.kw["meshTransform"] = AFXStringKeyword(
            command=self.cmd,
            name="meshTransform",
            isRequired=True,
            defaultValue="elliptic")

        self.kw["singularityRadius"] = AFXFloatKeyword(
            command=self.cmd,
            name="singularityRadius",
            isRequired=True,
            defaultValue=0)

        self.kw["xfemSimpleElements"] = AFXStringKeyword(
            command=self.cmd,
            name="xfemSimpleElements",
            isRequired=True,
            defaultValue="LinearTet - C3D4")
        self.kw["simpleContainerSeeds"] = AFXFloatKeyword(
            command=self.cmd,
            name="simpleContainerSeeds",
            isRequired=True,
            defaultValue=15)

        self.kw["xfemCPElements"] = AFXStringKeyword(
            command=self.cmd,
            name="xfemCPElements",
            isRequired=True,
            defaultValue="LinearTet - C3D4")
        self.kw["CPcrackSeeds"] = AFXFloatKeyword(
            command=self.cmd,
            name="CPcrackSeeds",
            isRequired=True,
            defaultValue=1)
        self.kw["CPcontainerSeeds"] = AFXFloatKeyword(
            command=self.cmd,
            name="CPcontainerSeeds",
            isRequired=True,
            defaultValue=10)

        self.kw["xfemMPElements"] = AFXStringKeyword(
            command=self.cmd,
            name="xfemMPElements",
            isRequired=True,
            defaultValue="LinearHexRI - C3D8R")
        self.kw["xfemMPoffset"] = AFXFloatKeyword(
            command=self.cmd,
            name="xfemMPoffset",
            isRequired=True,
            defaultValue=5,
            precision=6)
        self.kw["xfemMPheight"] = AFXFloatKeyword(
            command=self.cmd,
            name="xfemMPheight",
            isRequired=True,
            defaultValue=5,
            precision=6)
        self.kw["xfemMPcontainerSeeds"] = AFXFloatKeyword(
            command=self.cmd,
            name="xfemMPcontainerSeeds",
            isRequired=True,
            defaultValue=5)
        self.kw["xfemMPsmallContainerSeeds"] = AFXFloatKeyword(
            command=self.cmd,
            name="xfemMPsmallContainerSeeds",
            isRequired=True,
            defaultValue=8)

        self.kw["mdbName"] = AFXStringKeyword(
            command=self.cmd,
            name="mdbName",
            isRequired=True,
            defaultValue="")

        self.kw["iconDir"] = AFXStringKeyword(
            command=self.cmd,
            name="iconDir",
            isRequired=False,
            defaultValue=thisDir + "\\icons\\")

    def getFirstDialog(self):
        """
        """
        self.cmd.setKeywordValuesToDefaults()
        self.dialog1 = createCrackDb.WarningOnNewMdb(self)
        return self.dialog1

    def getNextDialog(self, previousDialog):
        """
        """
        self.previousDialog = previousDialog
        self.dialog2 = createCrackDb.DefineCrackParameters(self)
        return self.dialog2

    def doCustomChecks(self):
        """
        """
        analysisType = self.kw["analysisType"].getValue()
        xfemType = self.kw["xfemType"].getValue()
        mainWindow = getAFXApp().getAFXMainWindow()

        a = self.kw["a"].getValue()
        b = self.kw["b"].getValue()
        d = self.kw["containerD"].getValue()
        h = self.kw["containerH"].getValue()
        majorAxis = max(a, b)
        minorAxis = min(a, b)
        czs = self.kw["crackZoneScale"].getValue() * minorAxis
        offset = self.kw["xfemMPoffset"].getValue()
        mpHeight = self.kw["xfemMPheight"].getValue()

        if self.previousDialog == self.dialog1:
            if majorAxis >= d:
                showAFXErrorDialog(
                    mainWindow,
                    'The crack does not fit in the container.\nIncrease the container diameter.')
                return False

            if analysisType == "FEM":
                if majorAxis + czs >= d:
                    showAFXErrorDialog(
                        mainWindow,
                        'The crack and the crack zone do not fit in the container.\nEither increase the container diameter or reduce the crack zone scale factor.')
                    return False

                elif czs >= h:
                    showAFXErrorDialog(
                        mainWindow,
                        "Crack zone side does not fit in the container.\nEither increase the container height ot reduce the crack zone side.")
                    return False

                elif analysisType == "XFEM":
                    if xfemType == "multiplePartitions":
                        if mpHeight >= h:
                            showAFXErrorDialog(
                                mainWindow,
                                "Height of the partition must be less than the height of the container.\nEither reduce the height of the partition or increase the height of the container.")
                            return False

                        elif majorAxis + offset >= d:
                            showAFXErrorDialog(
                                mainWindow,
                                "The partition for the crack does not fit in the container.\nEither reduce the offset or increase the diameter of the container.")
                            return False
            return True
        return True


thisPath = os.path.abspath(__file__)
thisDir = os.path.dirname(thisPath)

toolset = getAFXApp().getAFXMainWindow().getPluginToolset()
toolset.registerGuiMenuButton(
    buttonText=info.submenu + 'Create Crack Model...',
    object=CrackDb_plugin(toolset),
    kernelInitString='import executeCreateCrackDbCommands',
    messageId=AFXMode.ID_ACTIVATE,
    icon=None,
    applicableModules=ALL,
    version=info.version,
    author=info.authors,
    description=info.description['preprocessor'],
    helpUrl=info.helpUrl)
