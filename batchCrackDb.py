

from abaqusConstants import INTEGER, FLOAT
from abaqusGui import *
import sharedFunctions


class SelectCrackParametersFile(AFXDataDialog):
    """
    """
    def __init__(self, form):
        """
        """
        self.form = form
        AFXDataDialog.__init__(
            self,
            form,
            "Select Batch Config File",
            self.CANCEL | self.CONTINUE,
            DIALOG_ACTIONS_RIGHT | DIALOG_ACTIONS_SEPARATOR)

        self.createWidgets()

    def createWidgets(self):
        """
        """
        vFrame = FXVerticalFrame(
            p=self,
            opts=LAYOUT_FILL_X | LAYOUT_FILL_Y,
            pl=0,
            pr=0,
            pb=0)
        loadGB = FXGroupBox(
            p=vFrame,
            text="Specify batch config file",
            opts=FRAME_GROOVE | LAYOUT_FILL_X)

        self.loadTextField = AFXTextField(
            p=loadGB,
            ncols=50,
            labelText="File name: ",
            tgt=self.form.kw["batchConf"],
            sel=0,
            opts=AFXTEXTFIELD_STRING | LAYOUT_FILL_X)
        self.loadTextField.setEditable(False)

        FXButton(
            p=loadGB,
            text="Browse",
            tgt=self.form,
            sel=self.form.ID_LOAD_BUTTON,
            opts=BUTTON_NORMAL | LAYOUT_RIGHT)

    def createLoadDialog(self):
        """
        """
        self.selectFileDialog = AFXFileSelectorDialog(
            self,
            "Select batch configuration file",
            self.form.kw["batchConf"],
            self.form.kw["crackReadOnly"],
            AFXSELECTFILE_EXISTING,
            "Batch config (*.txt)\nAll Files (*.*)")
        self.selectFileDialog.create()
        self.selectFileDialog.showModal()
        return 1


class ParameterReviewDialog(AFXDataDialog):
    """
    """
    def __init__(self, form):
        """
        """
        self.form = form
        AFXDataDialog.__init__(
            self,
            form,
            "Preview and Create",
            self.CANCEL | self.OK,
            DIALOG_ACTIONS_RIGHT | DIALOG_ACTIONS_SEPARATOR | DECOR_RESIZE)
        self.createButton = self.getActionButton(self.ID_CLICKED_OK)
        self.createButton.setText("Create")
        self.extractParameters()
        self.createWidgets()

    def extractParameters(self):
        """
        """
        fileName = self.form.kw["batchConf"].getValue()
        self.parameters = sharedFunctions.parseInput(fileName)

    def createWidgets(self):
        """
        """
        vFrame = FXVerticalFrame(
            p=self,
            opts=LAYOUT_FILL_X | LAYOUT_FILL_Y,
            pl=0,
            pr=0,
            pb=0)
        crackType = self.parameters["analysisType"][0]
        widgetTypes = {
            "FEM": self.createFEMwidgets,
            "XFEM_mp": self.createXFEM_mpWidgets,
            "XFEM_cp": self.createXFEM_cpWidgets,
            "XFEM_simple": self.createXFEM_simpleWidgets}
        treeRootText = {
            "FEM": "FEM analysis",
            "XFEM_mp": "XFEM multiple partitions analysis",
            "XFEM_cp": "XFEM crack partition analysis",
            "XFEM_simple": "XFEM simple analysis"}
        gBox = FXGroupBox(
            p=vFrame,
            text="Crack parameters",
            opts=FRAME_GROOVE | LAYOUT_FILL_X | LAYOUT_FILL_Y)
        self.tree = FXTreeList(
            p=gBox,
            nvis=0,
            tgt=None,
            sel=0,
            opts=LAYOUT_FILL_X | LAYOUT_FILL_Y | TREELIST_SHOWS_BOXES |
            TREELIST_ROOT_BOXES | TREELIST_SHOWS_LINES)
        self.treeRoot = self.tree.addItemLast(None, treeRootText[crackType])
        self.tree.expandTree(self.treeRoot)

        self.createCrackParametersTreeEntries()
        self.createContainerParametersTreeEntries()
        self.createMaterialTreeEntries()
        self.createLoadParametersTreeEntries()

        widgetTypes[crackType]()
        self.createSavingOptionsOptions(vFrame)

    def createXFEM_mpWidgets(self):
        """
        """
        mesh = self.tree.addItemLast(self.treeRoot, "Mesh")
        self.tree.addItemLast(
            mesh, "elements: " + str(self.parameters["elementType"]))
        self.tree.addItemLast(
            mesh,
            "partition height: " + str(self.parameters["meshPartitionHeight"]))
        self.tree.addItemLast(
            mesh,
            "partition offset: " + str(self.parameters["meshPartitionOffset"]))
        self.tree.addItemLast(
            mesh,
            "singularity radius: " + str(self.parameters["singularityRadius"]))

        seeds = self.tree.addItemLast(self.treeRoot, "Seeds")
        self.tree.addItemLast(
            seeds,
            "container: " + str(self.parameters["containerSeeds"]))
        self.tree.addItemLast(
            seeds,
            "partition container: " + str(
                self.parameters["partitionContainerSeeds"]))

    def createXFEM_cpWidgets(self):
        """
        """
        mesh = self.tree.addItemLast(self.treeRoot, "Mesh")
        self.tree.addItemLast(
            mesh,
            "elements: " + str(self.parameters["elementType"]))
        self.tree.addItemLast(
            mesh,
            "singularity radius: " + str(self.parameters["singularityRadius"]))

        seeds = self.tree.addItemLast(self.treeRoot, "Seeds")
        self.tree.addItemLast(
            seeds,
            "container seeds: " + str(self.parameters["containerSeeds"]))
        self.tree.addItemLast(
            seeds,
            "crack seeds: " + str(self.parameters["crackSeeds"]))

    def createXFEM_simpleWidgets(self):
        """
        """
        mesh = self.tree.addItemLast(self.treeRoot, "Mesh")
        self.tree.addItemLast(
            mesh,
            "elements: " + str(self.parameters["elementType"]))
        self.tree.addItemLast(
            mesh,
            "singularity radius: " + str(self.parameters["singularityRadius"]))

        seeds = self.tree.addItemLast(self.treeRoot, "Seeds")
        self.tree.addItemLast(
            seeds,
            "container seeds: " + str(self.parameters["containerSeeds"]))

    def createFEMwidgets(self):
        """
        """
        mesh = self.tree.addItemLast(self.treeRoot, "Mesh")
        self.tree.addItemLast(
            mesh,
            "transform: " + str(self.parameters["transformation"]))
        self.tree.addItemLast(
            mesh,
            "elements: " + str(self.parameters["elementType"]))
        self.tree.addItemLast(
            mesh,
            "crack zone scale = " + str(
                self.parameters["crackZoneSideScaleFactor"]))
        self.tree.addItemLast(
            mesh,
            "crack tip scale = " + str(
                self.parameters["crackTipSideScaleFactor"]))

        seeds = self.tree.addItemLast(self.treeRoot, "Seeds")
        czms = self.tree.addItemLast(
            seeds,
            "crack zone main = " + str(self.parameters["czms"]))
        czrs = self.tree.addItemLast(
            seeds,
            "crack zone refinement = " + str(self.parameters["czrs"]))
        arcs = self.tree.addItemLast(
            seeds,
            "arcs = " + str(self.parameters["arcs"]))
        crs = self.tree.addItemLast(
            seeds,
            "container refinement = " + str(self.parameters["crs"]))

    def createCrackParametersTreeEntries(self):
        """
        """
        crackParams = self.tree.addItemLast(
            self.treeRoot,
            "Crack: " + self.parameters["crackType"][0])
        a = self.tree.addItemLast(
            crackParams,
            "a = " + str(self.parameters["a"]))
        b = self.tree.addItemLast(
            crackParams,
            "b = " + str(self.parameters["b"]))

    def createMaterialTreeEntries(self):
        """
        """
        material = self.tree.addItemLast(
            self.treeRoot,
            "Material: " + self.parameters["materialName"][0])
        self.tree.addItemLast(
            material,
            "E = " + str(self.parameters["E"][0]))
        self.tree.addItemLast(
            material,
            "v = " + str(self.parameters["v"][0]))

    def createContainerParametersTreeEntries(self):
        """
        """
        container = self.tree.addItemLast(self.treeRoot, "Container")
        h = self.tree.addItemLast(
            container,
            "h = " + str(self.parameters["containerH"]))
        d = self.tree.addItemLast(
            container,
            "d = " + str(self.parameters["containerD"]))

    def createLoadParametersTreeEntries(self):
        """
        """
        loads = self.parameters["loads"][0]
        crackType = self.parameters["crackType"][0]
        loadsBranch = self.tree.addItemLast(self.treeRoot, "Loads")
        if loads != "infiniteBody":
            loadsBranch.setText("Loads: custom")
        else:
            loadsBranch.setText("Loads: infinite body")
            self.tree.addItemLast(
                loadsBranch,
                "sigma = " + str(self.parameters["sigma"]))
            if crackType == "embedded":
                self.tree.addItemLast(
                    loadsBranch,
                    "gamma = " + str(self.parameters["gamma"]))
                self.tree.addItemLast(
                    loadsBranch,
                    "omega = " + str(self.parameters["omega"]))
            elif crackType == "surface":
                self.tree.addItemLast(
                    loadsBranch,
                    "gamma = " + str(self.parameters["gamma"]))

    def createSavingOptionsOptions(self, frame):
        """
        """
        gBox = FXGroupBox(
            p=frame,
            text="Saving options",
            opts=FRAME_GROOVE | LAYOUT_FILL_X)
        combinations = self.calcNumberOfCombinations()
        vAlign = AFXVerticalAligner(p=gBox)
        combField = AFXTextField(
            p=vAlign,
            ncols=20,
            labelText="Number of Combinations: ")
        combField.setText(str(combinations))
        combField.setEditable(False)

        if (self.parameters["saveResults"][0] == "yes" and
                self.parameters["loads"][0] == "infiniteBody"):
            db = self.parameters["outputDatabase"][0]
            dbField = AFXTextField(
                p=vAlign,
                ncols=20,
                labelText="Results database: ")
            dbField.setText(db)
            dbField.setEditable(False)

            duplicatesField = AFXTextField(
                p=vAlign,
                ncols=20,
                labelText="Recalculate duplicates: ")
            duplicatesField.setText("no")
            duplicatesField.setEditable(False)

    def calcNumberOfCombinations(self):
        """
        """
        numAs = len(self.parameters["a"])
        numBs = len(self.parameters["b"])
        numHs = len(self.parameters["containerH"])
        numDs = len(self.parameters["containerD"])

        geomConfigs = numAs * numBs * numHs * numDs

        if self.parameters["loads"][0] == "infiniteBody":
            numSigmas = len(self.parameters["sigma"])
            crackType = self.parameters["crackType"][0]
            if crackType == "embedded":
                numGammas = len(self.parameters["gamma"])
                numOmegas = len(self.parameters["omega"])
            elif crackType == "surface":
                numGammas = len(self.parameters["gamma"])
                numOmegas = 1
            elif crackType == "edge":
                numGammas = 1
                numOmegas = 1
            loadConfigs = numSigmas * numGammas * numOmegas
        else:
            loadConfigs = 1

        numElemTypes = len(self.parameters["elementType"])
        analysis = self.parameters["analysisType"][0]
        if analysis == "FEM":
            numCzms = len(self.parameters["czms"])
            numCzrs = len(self.parameters["czrs"])
            numArcs = len(self.parameters["arcs"])
            numCrs = len(self.parameters["crs"])
            seedConfigs = numCzms * numCzrs * numArcs * numCrs

            numTransform = len(self.parameters["transformation"])
            numCtssf = len(self.parameters["crackTipSideScaleFactor"])
            numMnp = len(self.parameters["midNodePosition"])
            meshConfigs = numTransform * numCtssf * numMnp * numElemTypes

        elif analysis == "XFEM_simple":
            seedConfigs = len(self.parameters["containerSeeds"])

            numSingRadii = len(self.parameters["singularityRadius"])
            meshConfigs = numElemTypes * numSingRadii

        elif analysis == "XFEM_mp":
            numContSeeds = len(self.parameters["containerSeeds"])
            numPartContSeeds = len(self.parameters["partitionContainerSeeds"])
            seedConfigs = numContSeeds * numPartContSeeds

            numPartH = len(self.parameters["meshPartitionHeight"])
            numPartO = len(self.parameters["meshPartitionOffset"])
            numSingRadii = len(self.parameters["singularityRadius"])
            meshConfigs = numPartH * numPartO * numSingRadii * numElemTypes

        elif analysis == "XFEM_cp":
            numContSeeds = len(self.parameters["containerSeeds"])
            numCrackSeeds = len(self.parameters["crackSeeds"])
            seedConfigs = numContSeeds * numCrackSeeds

            numSingRadii = len(self.parameters["singularityRadius"])
            meshConfigs = numSingRadii

        totalConfigs = geomConfigs * loadConfigs * seedConfigs * meshConfigs
        return totalConfigs
