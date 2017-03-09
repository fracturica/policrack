

from abaqusConstants import ALL
from abaqusGui import *
import pickle
import shelve
import os
import sharedFunctions
import info

thisPath = os.path.abspath(__file__)
thisDir = os.path.dirname(thisPath)


class WarningOnNewMdb(AFXDataDialog):
    """
    """
    def __init__(self, form):
        """
        """
        AFXDataDialog.__init__(
            self,
            form,
            "Save current model",
            self.CONTINUE | self.CANCEL,
            DIALOG_ACTIONS_SEPARATOR)
        FXLabel(
            p=self,
            text="Current model will be closed without being saved!")


class ExtractResults(AFXDataDialog):
    """
    """
    def __init__(self, form):
        """
        """
        self.form = form
        AFXDataDialog.__init__(
            self,
            form,
            "Select Output Database and Config File",
            self.CANCEL | self.CONTINUE,
            DIALOG_ACTIONS_RIGHT | DIALOG_ACTIONS_SEPARATOR | DECOR_RESIZE)
        self.checkOdbs()
        self.createWidgets()

    def checkOdbs(self):
        """
        """
        self.odbPaths = session.odbs.keys()
        self.odbNames = []
        for path in self.odbPaths:
            odbName = path.split("/")[-1]
            self.odbNames += odbName,

    def createWidgets(self):
        """
        """
        hFrame = FXHorizontalFrame(
            p=self,
            opts=LAYOUT_FILL_X | LAYOUT_FILL_Y,
            pl=0, pr=0, pt=0, pb=0)
        listBox = FXGroupBox(
            p=hFrame,
            text="Open Odbs",
            opts=LAYOUT_FILL_Y | FRAME_GROOVE)

        self.odbList = AFXList(
            p=listBox,
            nvis=10,
            tgt=self.form,
            sel=self.form.ID_ODB_LIST,
            opts=FRAME_GROOVE | AFXLIST_NO_AUTOCOMMIT |
            LIST_SINGLESELECT | HSCROLLING_OFF)
        for odbName in self.odbNames:
            self.odbList.appendItem(odbName)

        vFrame = FXVerticalFrame(
            p=hFrame,
            opts=LAYOUT_FILL_X | LAYOUT_FILL_Y,
            pl=0, pr=0, pt=0, pb=0)
        mdbGB = FXGroupBox(
            p=vFrame,
            text="Crack configuration",
            opts=LAYOUT_FILL_X | FRAME_GROOVE)

        self.mdbTextField = AFXTextField(
            p=mdbGB,
            ncols=30,
            labelText="Config file: ",
            tgt=self.form.kw["confFile"],
            sel=0,
            opts=AFXTEXTFIELD_STRING | LAYOUT_FILL_X)
        self.mdbTextField.setEditable(False)

        FXButton(
            p=mdbGB,
            text="Browse",
            tgt=self.form,
            sel=self.form.ID_MDB_FILE,
            opts=BUTTON_NORMAL | LAYOUT_RIGHT)

    def fileSelectDialog(self):
        """
        """
        odbName = self.form.kw["odbName"].getValue()[:-4]
        self.selectFileDialog = AFXFileSelectorDialog(
            self,
            "Select a model database",
            self.form.kw["confFile"],
            None,
            AFXSELECTFILE_EXISTING,
            "Crack config ({0}.pickle)\nCrack config (*.pickle)".format(
                odbName),
            None)
        self.selectFileDialog.create()
        self.selectFileDialog.showModal()
        return 1


class PreviewAndSave(AFXDataDialog):
    """
    """
    def __init__(self, form):
        """
        """
        self.form = form
        self.dbDir = os.path.join(thisDir, 'db')

        AFXDataDialog.__init__(
            self,
            form,
            "Preview and Save Results to Database",
            self.CANCEL | self.OK,
            DIALOG_ACTIONS_RIGHT | DIALOG_ACTIONS_SEPARATOR | DECOR_RESIZE)
        self.readConfigFile()
        self.createWidgets()

    def readConfigFile(self):
        """
        """
        confFilePath = self.form.kw["confFile"].getValue()
        confFile = open(confFilePath, 'rb')
        self.metadata = pickle.load(confFile)
        confFile.close()
        print self.metadata

    def createWidgets(self):
        """
        """
        hFrame = FXHorizontalFrame(
            p=self,
            opts=LAYOUT_FILL_X | LAYOUT_FILL_Y,
            pl=0, pr=0, pt=0, pb=0)
        self.createOdbWidgets(hFrame)
        FXVerticalSeparator(
            p=hFrame,
            opts=SEPARATOR_GROOVE | LAYOUT_FILL_Y)
        self.createShelvesWidgets(hFrame)

    def createOdbWidgets(self, frame):
        """
        """
        vFrame = FXVerticalFrame(
            p=frame,
            opts=LAYOUT_FILL_X | LAYOUT_FILL_Y,
            pl=0, pr=0, pt=0, pb=0)
        gBox = FXGroupBox(
            p=vFrame,
            text="Model database parameters",
            opts=LAYOUT_FILL_X | LAYOUT_FILL_Y | FRAME_GROOVE)
        self.createOdbTree(gBox)

    def createOdbTree(self, frame):
        """
        """
        self.tree = FXTreeList(
            p=frame,
            nvis=0,
            tgt=None,
            sel=0,
            opts=TREELIST_NORMAL |
            LAYOUT_FILL_X | LAYOUT_FILL_Y |
            TREELIST_SHOWS_BOXES | TREELIST_ROOT_BOXES |
            TREELIST_SHOWS_LINES)
        treeTypes = {
            "FEM": self.createFEMtree,
            "XFEM_simple": self.createXFEM_simpleTree,
            "XFEM_cp": self.createXFEM_cpTree,
            "XFEM_mp": self.createXFEM_mpTree}
        treeRootText = {
            "FEM": "FEM analysis",
            "XFEM_simple": "XFEM simple analysis",
            "XFEM_cp": "XFEM crack partition analysis",
            "XFEM_mp": "XFEM multiple partitions analysis"}

        analysisType = self.metadata["input"]["analysisType"]
        if analysisType == "XFEM":
            modelType = self.metadata["input"]["modelType"]
            print modelType
            rootText = "{0} {1} analysis".format(analysisType, modelType)
            if modelType == "simple":
                key = "XFEM_simple"
            elif modelType == "multiplePartitions":
                key = "XFEM_mp"
            elif modelType == "crackPartition":
                key = "XFEM_cp"
        elif analysisType == "FEM":
            key = "FEM"

        rootText = treeRootText[key]
        self.treeRoot = self.tree.addItemFirst(p=None, text=rootText)
        self.tree.expandTree(self.treeRoot)

        crackType = self.metadata["input"]["crackParameters"]["crackType"]
        crackBranch = self.tree.addItemLast(
            p=self.treeRoot, text="Crack: " + crackType)
        a = self.metadata["input"]["crackParameters"]["a"]
        self.tree.addItemLast(
            p=crackBranch, text="a = " + str(a))
        b = self.metadata["input"]["crackParameters"]["b"]
        self.tree.addItemLast(
            p=crackBranch, text="b = " + str(b))

        containerBranch = self.tree.addItemLast(
            p=self.treeRoot, text="Container")
        h = self.metadata["input"]["geometricParameters"]["containerHeight"]
        self.tree.addItemLast(
            p=containerBranch, text="h = " + str(h))
        d = 2 * self.metadata["input"][
            "geometricParameters"]["containerRadius"]
        self.tree.addItemLast(
            p=containerBranch, text="d = " + str(d))

        material = self.metadata["input"]["material"]
        materialBranch = self.tree.addItemLast(
            p=self.treeRoot, text="Material: " + material["name"])
        e = str(material["E"])
        self.tree.addItemLast(p=materialBranch, text="E = " + e)
        v = str(material["v"])
        self.tree.addItemLast(p=materialBranch, text="v = " + v)

        self.createLoadsBranch()
        treeTypes[key]()

    def createLoadsBranch(self):
        """
        """
        predefinedLoads = self.metadata["input"]["createPredefinedLoads"]
        if predefinedLoads:
            loadsText = "Loads: infinite body"
            loadsBranch = self.tree.addItemLast(
                p=self.treeRoot, text=loadsText)
            sigma = self.metadata["input"]["analysisParameters"]["sigma"]
            self.tree.addItemLast(
                p=loadsBranch, text="sigma = " + str(sigma))
            crackType = self.metadata["input"]["crackParameters"]["crackType"]
            if crackType == "embedded":
                gamma = self.metadata["input"]["analysisParameters"]["gamma"]
                self.tree.addItemLast(
                    p=loadsBranch, text="gamma = " + str(gamma))
                omega = self.metadata["input"]["analysisParameters"]["omega"]
                self.tree.addItemLast(
                    p=loadsBranch, text="omega = " + str(omega))
            elif crackType == "surface":
                gamma = self.metadata["input"]["analysisParameters"]["gamma"]
                self.tree.addItemLast(
                    p=loadsBranch, text="gamma = " + str(gamma))
        else:
            loadsText = "Loads: custom"
            loadsBranch = self.tree.addItemLast(
                p=self.treeRoot, text=loadsText)

    def createXFEM_simpleTree(self):
        """
        """
        mesh = self.tree.addItemLast(
            p=self.treeRoot, text="Mesh")
        elements = self.metadata["input"]["meshParameters"]["elements"]
        self.tree.addItemLast(
            p=mesh, text="elements: " + elements)
        singularityRadius = self.metadata["input"][
                "interactionProperties"]["crack"]["singularityCalcRadius"]
        self.tree.addItemLast(
            p=mesh, text="singularity radius = " + str(singularityRadius))

        seed = self.tree.addItemLast(
            p=self.treeRoot, text="Seed")
        seeds = self.metadata["input"]["seedParameters"]["allEdges"]
        self.tree.addItemLast(
            p=seed, text="container seeds = " + str(seeds))

    def createFEMtree(self):
        """
        """
        mesh = self.tree.addItemLast(p=self.treeRoot, text="Mesh")
        elements = self.metadata[
            "input"]["meshParameters"]["elements"]
        self.tree.addItemLast(p=mesh, text="elements: " + elements)

        transform = self.metadata["input"][
            "meshParameters"]["transformationType"]
        self.tree.addItemLast(p=mesh, text="transformation: " + transform)

        crackTipSide = self.metadata["input"][
            "geometricParameters"]["crackTipSide"]
        self.tree.addItemLast(
            p=mesh, text="crack tip side = " + str(crackTipSide))

        crackZoneSide = self.metadata["input"][
            "geometricParameters"]["crackZoneSide"]
        self.tree.addItemLast(
            p=mesh, text="crack zone side = " + str(crackZoneSide))

        seed = self.tree.addItemLast(p=self.treeRoot, text="Seeds")
        arcSeeds = self.metadata["input"]["seedParameters"]["arcSeeds"]
        self.tree.addItemLast(p=seed, text="arcs = " + str(arcSeeds))

        crackZoneMainSeeds = self.metadata["input"][
            "seedParameters"]["crackZoneMainSeeds"]
        self.tree.addItemLast(
            p=seed, text="crack zone main = " + str(crackZoneMainSeeds))

        crackZoneRefinement = self.metadata["input"][
            "seedParameters"]["crackZoneRefinementSeeds"]
        self.tree.addItemLast(
            p=seed, text="crack zone refinement = " + str(crackZoneRefinement))

        containerRefinement = self.metadata["input"][
            "seedParameters"]["containerRefinementSeeds"]
        self.tree.addItemLast(
            p=seed, text="container refinement = " + str(containerRefinement))

    def createXFEM_cpTree(self):
        """
        """
        mesh = self.tree.addItemLast(p=self.treeRoot, text="Mesh")
        elements = self.metadata["input"]["meshParameters"]["elements"]
        self.tree.addItemLast(p=mesh, text="elements: " + elements)

        singularityRadius = self.metadata["input"][
            "interactionProperties"]["crack"]["singularityCalcRadius"]
        self.tree.addItemLast(
            p=mesh, text="singularity radius = " + str(singularityRadius))

        seed = self.tree.addItemLast(p=self.treeRoot, text="Seed")
        containerSeeds = self.metadata["input"]["seedParameters"]["allEdges"]
        self.tree.addItemLast(
            p=seed, text="container seeds = " + str(containerSeeds))

        crackSeeds = self.metadata["input"]["seedParameters"]["crackEdges"]
        self.tree.addItemLast(p=seed, text="crack seeds = " + str(crackSeeds))

    def createXFEM_mpTree(self):
        """
        """
        mesh = self.tree.addItemLast(p=self.treeRoot, text="Mesh")
        elements = self.metadata["input"]["meshParameters"]["elements"]
        self.tree.addItemLast(p=mesh, text="elements: " + elements)

        partitionH = self.metadata["input"][
            "geometricParameters"]["smallContainerHeight"]
        self.tree.addItemLast(
            p=mesh, text="partition height = " + str(partitionH))

        partitionOffset = self.metadata["input"][
            "geometricParameters"]["crackFrontOffset"]
        self.tree.addItemLast(
            p=mesh, text="partition offset = " + str(partitionOffset))

        singularityRadius = self.metadata["input"][
            "interactionProperties"]["crack"]["singularityCalcRadius"]
        self.tree.addItemLast(
            p=mesh, text="singularity radius = " + str(singularityRadius))

        seed = self.tree.addItemLast(p=self.treeRoot, text="Seed")
        containerSeeds = self.metadata["input"]["seedParameters"]["allEdges"]
        self.tree.addItemLast(
            p=seed, text="container = " + str(containerSeeds))

        crackSeeds = self.metadata["input"]["seedParameters"]["crackContEdges"]
        self.tree.addItemLast(
            p=seed, text="partition = " + str(crackSeeds))

    def createShelvesWidgets(self, frame):
        """
        """
        vFrame = FXVerticalFrame(
            p=frame,
            opts=LAYOUT_FILL_Y,
            pl=0, pr=0, pt=0, pb=0)
        gBox = FXGroupBox(
            p=vFrame,
            text="Output database",
            opts=FRAME_GROOVE | LAYOUT_FILL_X)
        self.createNewNameWidgets(gBox)

        gBox = FXGroupBox(
            p=vFrame,
            text="Compatible databases",
            opts=FRAME_GROOVE | LAYOUT_FILL_X)
        self.createDbList(gBox)

    def createNewNameWidgets(self, frame):
        """
        """
        gBox = FXGroupBox(
            p=frame,
            text="New database",
            opts=FRAME_GROOVE | LAYOUT_FILL_X)
        self.newDbName = AFXTextField(
            p=gBox,
            ncols=30,
            labelText="Name: ",
            tgt=None,
            sel=0,
            opts=AFXTEXTFIELD_STRING)
        FXButton(
            p=gBox,
            text="Create database",
            tgt=self.form,
            sel=self.form.ID_CREATE_DB,
            opts=BUTTON_NORMAL | LAYOUT_SIDE_RIGHT)

    def getNewShelveName(self):
        """
        """
        name = self.newDbName.getText().strip().rstrip()
        return name

    def createNewDb(self, newDbName):
        """
        """
        sharedFunctions.createResultsDirStr(newDbName)
        dbPath = sharedFunctions.getDbPath(newDbName)
        odbMetadata = self.createOdbMetadata()
        db = shelve.open(dbPath)
        db["metadata"] = odbMetadata
        db.close()
        self.dbList.appendItem(text=newDbName)

    def createOdbMetadata(self):
        """
        """
        histOutputs = self.metadata["input"][
            "interactionProperties"]["crack"]["historyOutputs"].keys()
        histOutputs.sort()
        crackType = self.metadata["input"]["crackParameters"]["crackType"]
        loadType = self.metadata["input"]["createPredefinedLoads"]

        odbMetadata = {
            "crackType": crackType,
            "dbVersion": info.dbVersion,
            "historyOutputs": histOutputs,
            "description": ""}
        if loadType:
            odbMetadata["loads"] = "infiniteBody"
        else:
            odbMetadata["loads"] = "custom"
        return odbMetadata

    def createDbList(self, frame):
        """
        """
        self.dbList = AFXList(
            p=frame,
            nvis=15,
            tgt=self.form.kw["outputDb"],
            sel=0,
            opts=AFXLIST_NO_AUTOCOMMIT | LIST_SINGLESELECT | LAYOUT_FILL_X)
        self.populateDbList()

    def populateDbList(self):
        """
        """
        dbNames = sharedFunctions.getListOfDbs()
        for db in dbNames:
            if self.checkCompatibility(db):
                self.dbList.appendItem(text=db)

    def checkCompatibility(self, db):
        """
        """
        dbPath = sharedFunctions.getDbPath(db)
        db = shelve.open(dbPath, 'r')
        dbMeta = db["metadata"]
        db.close()
        odbMeta = self.createOdbMetadata()
        print "odbMetadata", odbMeta
        print "dbMetadata", dbMeta
        equal = True
        if str(odbMeta["dbVersion"]) != str(dbMeta["dbVersion"]):
            return False
        else:
            if odbMeta["crackType"] != dbMeta["crackType"]:
                return False
            if odbMeta["loads"] != dbMeta["loads"]:
                return False
            odbMeta["historyOutputs"].sort()
            dbMeta["historyOutputs"].sort()
            if odbMeta["historyOutputs"] != dbMeta["historyOutputs"]:
                return False
            return True

    def getListOfDbs(self):
        """
        """
        return sharedFunctions.getListOfDbs()
