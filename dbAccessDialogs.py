

from abaqusConstants import *
from abaqusGui import *
from kernelAccess import *
import os
import shelve
import sharedFunctions


class SelectDb(AFXDataDialog):
    """
    """
    def __init__(self, form):
        """
        """
        self.form = form
        AFXDataDialog.__init__(
            self,
            form,
            "Select Database",
            self.CANCEL | self.CONTINUE,
            DIALOG_ACTIONS_SEPARATOR | DIALOG_ACTIONS_RIGHT | DECOR_RESIZE)
        self.createWidgets()

    def createWidgets(self):
        """
        """
        hFrame = FXHorizontalFrame(
            p=self,
            opts=LAYOUT_FILL_X | LAYOUT_FILL_Y,
            pl=0, pr=0, pt=0, pb=0)
        self.createDbListWidgets(hFrame)

        vFrame = FXVerticalFrame(
            p=hFrame,
            opts=LAYOUT_FILL_X | LAYOUT_FILL_Y,
            pl=0, pr=0, pt=0, pb=0)

        self.createDbInfoWidgets(vFrame)
        self.createDbDescriptionWidgets(vFrame)
        self.createScannerWidget(vFrame)

    def createDbInfoWidgets(self, frame):
        """
        """
        gBox = FXGroupBox(
            p=frame,
            text="Database info",
            opts=LAYOUT_FILL_X | FRAME_GROOVE)
        vAlign = AFXVerticalAligner(p=gBox)
        self.crackType = AFXTextField(
            p=vAlign,
            ncols=25,
            labelText="crack type: ",
            tgt=None,
            sel=0,
            opts=AFXTEXTFIELD_STRING)
        self.crackType.setEditable(False)
        self.loads = AFXTextField(
            p=vAlign,
            ncols=25,
            labelText="loads: ",
            tgt=None,
            sel=0,
            opts=AFXTEXTFIELD_STRING)
        self.loads.setEditable(False)

    def createDbDescriptionWidgets(self, frame):
        """
        """
        gBox = FXGroupBox(
            p=frame,
            text="Database description",
            opts=LAYOUT_FILL_X | LAYOUT_FILL_Y | FRAME_GROOVE)
        self.description = FXText(
            p=gBox,
            tgt=None,
            sel=0,
            opts=TEXT_READONLY | TEXT_WORDWRAP | LAYOUT_FILL_X | LAYOUT_FILL_Y)

    def createDbListWidgets(self, frame):
        """
        """
        gBox = FXGroupBox(
            p=frame,
            text="Databases",
            opts=FRAME_GROOVE | LAYOUT_FILL_Y)
        self.dbList = AFXList(
            p=gBox,
            nvis=25,
            tgt=self.form,
            sel=self.form.ID_DBLIST_SELECT,
            opts=AFXLIST_NO_AUTOCOMMIT | LIST_SINGLESELECT | HSCROLLING_OFF)
        dbs = sharedFunctions.getListOfDbs()
        for db in sorted(dbs):
            self.dbList.appendItem(db)

    def createScannerWidget(self, frame):
        """
        """
        gBox = FXGroupBox(
            p=frame,
            text="Selected database entries",
            opts=FRAME_GROOVE | LAYOUT_FILL_X)
        self.scanner = AFXProgressBar(
            gBox, None, 0,
            LAYOUT_FILL_X | LAYOUT_FIX_HEIGHT |
            AFXPROGRESSBAR_ITERATOR,
            0, 0, 200, 25, 5, 5, 10, 10)
        self.scanner.setTotal(0)

    def updateProgress(self):
        """
        """
        entryNumber = self.form.counter.getValue()
        self.scanner.setProgress(entryNumber)

    def updateWidgets(self):
        """
        """
        dbPath = sharedFunctions.getDbPath(self.form.kw["dbName"].getValue())
        db = shelve.open(dbPath, 'r')
        metadata = db["metadata"]
        numEntries = len(db.keys()) - 1
        db.close()
        self.description.setText(metadata["description"])
        self.crackType.setText(metadata["crackType"])
        self.loads.setText(metadata["loads"])
        self.scanner.setTotal(numEntries)


class AccessDb(AFXDataDialog):
    """
    """
    def __init__(self, form):
        """
        """
        self.form = form
        self.db = sharedFunctions.getDbPath(
            self.form.kw["dbName"].getValue())
        title = "Database Browser: {0}".format(
            self.form.kw["dbName"].getValue())

        AFXDataDialog.__init__(
            self, form, title,
            self.APPLY | self.DISMISS,
            DIALOG_ACTIONS_SEPARATOR | DIALOG_ACTIONS_RIGHT | DECOR_RESIZE)

        applyButton = self.getActionButton(self.ID_CLICKED_APPLY)
        applyButton.setText("Create")
        self.getDbMetadata()
        self.createWidgets()

    def getDbMetadata(self):
        """
        """
        db = shelve.open(self.db, 'r')
        self.metadata = db["metadata"]
        db.close()

    def createWidgets(self):
        """
        """
        mainHorizontalFrame = FXHorizontalFrame(
            p=self,
            opts=LAYOUT_FILL_X | LAYOUT_FILL_Y,
            pl=0, pr=0, pt=0, pb=0)
        self.createTreeWidget(mainHorizontalFrame)
        self.createDataOptionsWidgets(mainHorizontalFrame)
        self.createContoursOptionsWidgets(mainHorizontalFrame)
        self.createOutputOptionsWidgets(mainHorizontalFrame)

    def createOutputOptionsWidgets(self, mainHorizontalFrame):
        """
        """
        outputVerticalFrame = FXVerticalFrame(
            p=mainHorizontalFrame,
            opts=0,
            pl=0, pr=0, pt=0, pb=0)
        outputGroupBox = FXGroupBox(
            p=outputVerticalFrame,
            text="Items to create",
            opts=FRAME_GROOVE)
        FXCheckButton(
            p=outputGroupBox,
            text="XYPlotData",
            tgt=self.form.kw["XYPlotData"],
            sel=0)
        FXCheckButton(
            p=outputGroupBox,
            text="Print data structure",
            tgt=self.form.kw["printData"],
            sel=0)
        FXHorizontalSeparator(p=outputGroupBox)
        FXCheckButton(
            p=outputGroupBox,
            text="Visualization Odb",
            tgt=self.form.kw["VisualizationOdb"],
            sel=0)

    def createContoursOptionsWidgets(self, mainHorizontalFrame):
        """
        """
        contourVerticalFrame = FXVerticalFrame(
            p=mainHorizontalFrame,
            opts=0,
            pl=0, pr=0, pt=0, pb=0)
        contourGroupBox = FXGroupBox(
            p=contourVerticalFrame,
            text="Contours",
            opts=FRAME_GROOVE)
        contourListGroupBox = FXGroupBox(
            p=contourGroupBox,
            text="Contours to average",
            opts=FRAME_GROOVE | LAYOUT_FILL_X)
        contourList = AFXList(
            p=contourListGroupBox,
            nvis=7,
            tgt=self.form.kw["contoursToAverage"],
            opts=FRAME_GROOVE |
            AFXLIST_NO_AUTOCOMMIT |
            LIST_EXTENDEDSELECT |
            LAYOUT_FILL_X)

        for contour in range(1, 6, 1):
            contourName = "Contour " + str(contour)
            contourList.appendItem(text=contourName)

        contourGroupBox = FXGroupBox(
            p=contourGroupBox,
            text="Separate contours",
            opts=FRAME_GROOVE)
        FXCheckButton(
            p=contourGroupBox,
            text="Include contour data",
            tgt=self.form.kw["includeContours"],
            sel=0)

    def createDataOptionsWidgets(self, mainHorizontalFrame):
        """
        """
        dataVerticalFrame = FXVerticalFrame(
            p=mainHorizontalFrame,
            opts=0,
            pl=0, pr=0, pt=0, pb=0)
        gBox = FXGroupBox(
            p=dataVerticalFrame,
            text="Results selection",
            opts=FRAME_GROOVE)
        self.createAnalyticalDataWidgets(gBox)
        self.createAnalysisDataWidgets(gBox)

    def createAnalyticalDataWidgets(self, frame):
        """
        """
        loads = self.metadata["loads"]
        crack = self.metadata["crackType"]
        analyticalSolutions = {
            "infiniteBody": {
                "embedded": ("K1", "K2", "K3"),
                "surface": (),
                "edge": ()},
            "custom": {
                "embedded": (),
                "surface": (),
                "edge": ()}}
        analyticalKeys = analyticalSolutions[loads][crack]
        if analyticalKeys:
            gBox = FXGroupBox(
                p=frame,
                text="Analytical solutions",
                opts=FRAME_GROOVE | LAYOUT_FILL_X)
            for key in sorted(analyticalKeys):
                FXCheckButton(
                    p=gBox,
                    text=key,
                    tgt=self.form.kw["analytical"][key],
                    sel=0)
                self.form.kw["analytical"][key].setValue(True)

    def createAnalysisDataWidgets(self, frame):
        """
        """
        gBox = FXGroupBox(
            p=frame,
            text="Analysis results",
            opts=FRAME_GROOVE | LAYOUT_FILL_X)
        dataKeys = []
        histOuts = self.metadata["historyOutputs"]
        for key in histOuts:
            for dataKey in sorted(self.form.outputDataKeys[key]):
                dataKeys += dataKey,

        for key in dataKeys:
            FXCheckButton(
                p=gBox,
                text=key,
                tgt=self.form.kw["analysis"][key],
                sel=0)
            self.form.kw["analysis"][key].setValue(True)

    def createTreeWidget(self, mainHorizontalFrame):
        """
        """
        self.selectableTreeItemIDs = ()
        treeGroupBox = FXGroupBox(
                p=mainHorizontalFrame,
                text="Database records",
                opts=FRAME_GROOVE | LAYOUT_FILL_X | LAYOUT_FILL_Y)
        self.tree = FXTreeList(
                p=treeGroupBox,
                nvis=0,
                tgt=self.form,
                sel=self.form.ID_TREE,
                opts=LAYOUT_FILL_X | LAYOUT_FILL_Y |
                TREELIST_BROWSESELECT | TREELIST_MULTIPLESELECT |
                TREELIST_SHOWS_LINES | TREELIST_SHOWS_BOXES |
                TREELIST_ROOT_BOXES)

        self.treeEntries = {}
        self.treeEntries["FEM"] = self.tree.addItemLast(None, "FEM")
        self.tree.disableItem(self.treeEntries["FEM"])
        self.treeEntries["XFEM"] = self.tree.addItemLast(None, "XFEM")
        self.tree.disableItem(self.treeEntries["XFEM"])

        db = shelve.open(self.db)
        counter = 0
        dbKeys = db.keys()
        dbKeys.remove("metadata")

        for key in dbKeys:
            self.form.counter.setValue(counter)
            self.form.updateProgress()
            counter += 1
            dataID = sharedFunctions.createID(db[key]["input"], key)
            analysisType = db[key]["input"]["analysisType"]
            self.createTreeItems(
                dbEntryID=dataID,
                dbKey=key,
                analysisType=analysisType,
                dbEntry=db[key])
        db.close()

    def createTreeItems(self, dbEntryID, dbKey, analysisType, dbEntry):
        """
        """
        treeItemID = analysisType
        parent = analysisType
        for key in sorted(dbEntryID.keys()):
            idFromKey = "_" + key.split("_")[1]
            treeItemID += idFromKey
            self.createTreeEntry(parent, treeItemID, dbEntry)
            parent = treeItemID
            treeItemID += "_" + dbEntryID[key]
            self.createTreeEntry(parent, treeItemID, dbEntry)
            parent = treeItemID

    def createTreeEntry(self, parent, treeItemID, dbEntry):
        """
        """
        if treeItemID not in self.treeEntries.keys():
            parent = self.treeEntries[parent]
            treeItemName = treeItemID.split("_")[-1]
            if (('dot' not in treeItemName) and
                    ((len(treeItemName) < 25) or ('.' in treeItemName))):
                self.treeEntries[treeItemID] = self.tree.addItemLast(
                    parent, treeItemName)
                self.tree.disableItem(self.treeEntries[treeItemID])
            else:
                self.treeEntries[treeItemID] = self.tree.addItemLast(
                    p=parent,
                    text=treeItemName,
                    ptr=treeItemName,
                    notify=True)
                if dbEntry["reports"]["successfulAnalysis"]:
                    self.selectableTreeItemIDs += treeItemID,
                else:
                    self.tree.disableItem(self.treeEntries[treeItemID])
