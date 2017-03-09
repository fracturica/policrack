

from abaqusConstants import INTEGER, FLOAT
from abaqusGui import *


class DefineCrackParameters(AFXDataDialog):
    """
    """
    def __init__(self, form):
        """
        """
        self.form = form
        AFXDataDialog.__init__(
            self,
            form,
            "Create Crack Model",
            self.CANCEL | self.OK,
            DIALOG_ACTIONS_RIGHT | DIALOG_ACTIONS_SEPARATOR)

        self.createButton = self.getActionButton(self.ID_CLICKED_OK)
        self.createButton.setText("Create")

        self.createWidgets()
        self.form.onGenerateMdbName(None, None, None, None)

    def createWidgets(self):
        """
        """
        hFrame = FXHorizontalFrame(
            p=self,
            opts=LAYOUT_FILL_X | LAYOUT_FILL_Y,
            pl=0, pr=0, pt=0, pb=0)
        vFrameLeft = FXVerticalFrame(
            p=hFrame,
            opts=LAYOUT_FILL_X | LAYOUT_FILL_Y,
            pl=0, pr=0, pt=0, pb=0)
        miniHFrame = FXHorizontalFrame(
            p=vFrameLeft,
            opts=LAYOUT_FILL_X,
            pl=0, pr=0, pt=0, pb=0)
        self.createMdbNameWidgets(miniHFrame)

        paramGB = FXGroupBox(
            p=vFrameLeft,
            text="Geometric parameters",
            opts=FRAME_GROOVE)

        miniHFrame = FXHorizontalFrame(p=paramGB)
        self.createCrackParamsWidgets(miniHFrame)
        self.createContainerParamsWidgets(miniHFrame)

        miniHFrame = FXHorizontalFrame(p=vFrameLeft)
        self.createMaterialWidgets(miniHFrame)
        self.createLoadWidgets(miniHFrame)

        vFrameRight = FXVerticalFrame(p=hFrame, opts=LAYOUT_FILL_Y)
        self.createTabWidgets(vFrameRight)

    def createMdbNameWidgets(self, frame):
        """
        """
        gBox = FXGroupBox(
            p=frame,
            text="Model database",
            opts=FRAME_GROOVE | LAYOUT_FILL_X)
        hFrame = FXHorizontalFrame(
            p=gBox,
            opts=LAYOUT_FILL_X)
        self.mdbName = AFXTextField(
            p=hFrame,
            ncols=20,
            labelText="name: ",
            tgt=self.form.kw["mdbName"],
            sel=0)
        FXButton(
            p=hFrame,
            text="Generate name",
            tgt=self.form,
            sel=self.form.ID_GENERATE_MDB_NAME,
            opts=BUTTON_NORMAL | LAYOUT_RIGHT)

    def createCrackParamsWidgets(self, frame):
        """
        """
        gBox = FXGroupBox(p=frame, text="Crack", opts=FRAME_GROOVE)
        vFrame = FXVerticalFrame(p=gBox)
        vAlign = AFXVerticalAligner(p=vFrame)

        self.crackType = AFXComboBox(
            p=vAlign,
            ncols=8,
            nvis=3,
            text="type: ",
            tgt=self.form,
            sel=self.form.ID_CRACK_TYPE)
        self.crackType.appendItem("embedded")
        self.crackType.appendItem("surface")
        self.crackType.appendItem("edge")

        self.crackA = AFXFloatSpinner(
            p=vAlign,
            ncols=10,
            labelText="a",
            tgt=self.form,
            sel=self.form.ID_CRACK_A)
        self.crackA.setRange(1, 100)
        self.crackA.setValue(10)

        self.crackB = AFXFloatSpinner(
            p=vAlign,
            ncols=10,
            labelText="b",
            tgt=self.form,
            sel=self.form.ID_CRACK_B)
        self.crackB.setRange(1, 100)
        self.crackB.setValue(10)

        self.crackInfo = AFXTextField(
            p=vAlign,
            ncols=10,
            labelText="a/b",
            tgt=None,
            sel=0,
            opts=AFXTEXTFIELD_FLOAT | AFXTEXTFIELD_READONLY)
        self.crackInfo.setPrecision(2)
        self.crackInfo.setText("1.0")

        self.crackParTable = AFXTable(
            p=vFrame,
            numVisRows=1,
            numVisColumns=1,
            numRows=1,
            numColumns=1,
            tgt=None,
            sel=0,
            w=121, h=61)
        self.crackParTable.setRowHeight(0, 69)
        self.crackParTable.setColumnWidth(0, 142)
        self.embeddedCI = afxCreatePNGIcon(
            self.form.kw["iconDir"].getValue() + "embedded.png")
        self.surfaceCI = afxCreatePNGIcon(
            self.form.kw["iconDir"].getValue() + "surface.png")
        self.edgeCI = afxCreatePNGIcon(
            self.form.kw["iconDir"].getValue() + "edge.png")
        self.crackParTable.setItemIcon(row=0, column=0, icon=self.embeddedCI)

    def createContainerParamsWidgets(self, frame):
        """
        """
        gBox = FXGroupBox(
            p=frame,
            text="Container",
            opts=FRAME_GROOVE | LAYOUT_FILL_Y)
        vFrame = FXVerticalFrame(p=gBox)
        vAlign = AFXVerticalAligner(p=vFrame)

        self.containerH = AFXFloatSpinner(
            p=vAlign,
            ncols=10,
            labelText="h",
            tgt=self.form.kw["containerH"],
            sel=0)
        self.containerH.setRange(1, 10000)

        self.containerD = AFXFloatSpinner(
            p=vAlign,
            ncols=10,
            labelText='d',
            tgt=self.form.kw["containerD"],
            sel=0)
        self.containerD.setRange(1, 10000)

        table = AFXTable(
            p=vFrame,
            numVisRows=1,
            numVisColumns=1,
            numRows=1,
            numColumns=1,
            tgt=None,
            sel=0,
            w=125, h=111)
        containerCI = afxCreatePNGIcon(
            self.form.kw["iconDir"].getValue() + "container.png")
        table.setItemIcon(row=0, column=0, icon=containerCI)
        table.setColumnWidth(0, 139)
        table.setRowHeight(0, 134)
        table.recalc()

    def createMaterialWidgets(self, frame):
        """
        """
        gBox = FXGroupBox(
            p=frame,
            text="Material",
            opts=FRAME_GROOVE | LAYOUT_FILL_Y)
        vAlign = AFXVerticalAligner(p=gBox)

        materialName = AFXTextField(
            p=vAlign,
            ncols=12,
            labelText="name",
            tgt=self.form.kw["materialName"],
            sel=0,
            opts=LAYOUT_SIDE_BOTTOM)

        eModulus = AFXFloatSpinner(
            p=vAlign,
            ncols=10,
            labelText="E",
            tgt=self.form.kw["eModulus"],
            sel=0,
            opts=LAYOUT_SIDE_BOTTOM)
        eModulus.setRange(0, 1000000000000000)

        vRatio = AFXFloatSpinner(
            p=vAlign,
            ncols=10,
            labelText="v",
            tgt=self.form.kw["vRatio"],
            sel=0,
            opts=LAYOUT_SIDE_BOTTOM)
        vRatio.setRange(0, 0.5)
        vRatio.setIncrement(0.01)

    def createLoadWidgets(self, frame):
        """
        """
        gBox = FXGroupBox(p=frame, text="Load", opts=FRAME_GROOVE)
        vFrame = FXVerticalFrame(p=gBox)

        applyLoads = FXCheckButton(
            p=vFrame,
            text="Apply Loads",
            tgt=self.form,
            sel=self.form.ID_APPLY_LOADS)

        vAlign = AFXVerticalAligner(p=vFrame)

        self.magnitude = AFXFloatSpinner(
            p=vAlign,
            ncols=10,
            labelText="magnitude",
            tgt=self.form.kw["sigma"],
            sel=0)
        self.magnitude.setRange(-1000000000000, 100000000000000)

        self.gamma = AFXFloatSpinner(
            p=vAlign,
            ncols=10,
            labelText="gamma",
            tgt=self.form.kw["gamma"],
            sel=0)
        self.gamma.setRange(-90, 90)

        self.omega = AFXFloatSpinner(
            p=vAlign,
            ncols=10,
            labelText="omega",
            tgt=self.form.kw["omega"],
            sel=0)
        self.omega.setRange(-90, 90)

        if self.form.kw["applyLoads"].getValue() is False:
            self.magnitude.disable()
            self.gamma.disable()
            self.omega.disable()
        elif self.form.kw["applyLoads"].getValue() is True:
            applyLoads.setCheck(True)

    def createTabWidgets(self, frame):
        """
        """
        self.tabBook = FXTabBook(
            p=frame,
            tgt=self.form,
            sel=self.form.ID_ANALYSIS_TYPE,
            opts=LAYOUT_FILL_Y | TABBOOK_TOPTABS)

        FXTabItem(
            p=self.tabBook,
            text="FEM",
            ic=None,
            opts=TAB_TOP)
        femFrame = FXVerticalFrame(
            p=self.tabBook,
            opts=FRAME_RAISED | FRAME_SUNKEN)
        self.createFemWidgets(femFrame)

        FXTabItem(
            p=self.tabBook,
            text="XFEM",
            ic=None,
            opts=TAB_TOP)
        xfemFrame = FXVerticalFrame(
            p=self.tabBook,
            opts=FRAME_RAISED | FRAME_SUNKEN)
        self.createXfemWidgets(xfemFrame)

    def createFemWidgets(self, frame):
        """
        """
        vFrame = FXVerticalFrame(
            p=frame,
            opts=LAYOUT_FILL_X | LAYOUT_FILL_Y)

        elements = AFXComboBox(
            p=vFrame,
            ncols=0,
            nvis=4,
            text="Elements",
            tgt=self.form.kw["femElements"],
            sel=0)
        elements.appendItem("LinearRI - C3D8R")
        elements.appendItem("LinearFI - C3D8")
        elements.appendItem("QuadraticRI - C3D20R")
        elements.appendItem("QuadraticFI - C3D20")

        FXHorizontalSeparator(
            p=vFrame,
            opts=SEPARATOR_GROOVE | LAYOUT_FILL_X)

        meshTransform = AFXComboBox(
            p=vFrame,
            ncols=0,
            nvis=2,
            text="Mesh transformation: ",
            tgt=self.form.kw["meshTransform"],
            sel=0)
        meshTransform.appendItem("elliptic")
        meshTransform.appendItem("simpleScale")
        FXHorizontalSeparator(
            p=vFrame,
            opts=SEPARATOR_GROOVE | LAYOUT_FILL_X)

        gBox = FXGroupBox(
            p=vFrame,
            text="Mesh partition dimensions",
            opts=FRAME_GROOVE | LAYOUT_FILL_X)

        vAlign = AFXVerticalAligner(p=gBox, opts=LAYOUT_FILL_X)

        self.crackZoneScale = AFXFloatSpinner(
            p=vAlign,
            ncols=10,
            labelText="crack zone scale",
            tgt=self.form.kw["crackZoneScale"],
            sel=0)
        self.crackZoneScale.setRange(0.1, 1.99)
        self.crackZoneScale.setIncrement(0.1)
        self.form.kw["crackZoneScale"].setValue(1.0)

        self.crackTipScale = AFXFloatSpinner(
            p=vAlign,
            ncols=10,
            labelText="crack tip scale",
            tgt=self.form.kw["crackTipScale"],
            sel=0)
        self.crackTipScale.setRange(0.1, 0.99)
        self.crackTipScale.setIncrement(0.1)
        self.form.kw["crackTipScale"].setValue(0.3)

        FXButton(
            p=gBox,
            ic=None,
            text="Show mesh partitions",
            tgt=self.form,
            sel=self.form.ID_MESH_DIMENSIONS,
            opts=BUTTON_NORMAL | LAYOUT_SIDE_RIGHT)

        gBox = FXGroupBox(
            p=vFrame,
            text="Mesh seeds",
            opts=FRAME_GROOVE | FRAME_SUNKEN | LAYOUT_FILL_X)

        vAlign = AFXVerticalAligner(p=gBox, opts=LAYOUT_FILL_X)
        self.arcSeeds = AFXFloatSpinner(
            p=vAlign,
            ncols=10,
            labelText="arcSeeds",
            tgt=self.form.kw["arcSeeds"],
            sel=0,
            opts=LAYOUT_SIDE_RIGHT)
        self.arcSeeds.setRange(3, 200)
        self.crackZoneSeeds = AFXFloatSpinner(
            p=vAlign,
            ncols=10,
            labelText="crackZoneSeeds",
            tgt=self.form.kw["crackZoneSeeds"],
            sel=0,
            opts=LAYOUT_SIDE_RIGHT)
        self.crackZoneSeeds.setRange(3, 200)
        self.containerRefinement = AFXFloatSpinner(
            p=vAlign,
            ncols=10,
            labelText="containerRefinementSeeds",
            tgt=self.form.kw["containerRefinementSeeds"],
            sel=0)
        self.containerRefinement.setRange(1, 100)
        self.crackZoneRefinement = AFXFloatSpinner(
            p=vAlign,
            ncols=10,
            labelText="crackZoneRefinementSeeds",
            sel=0)
        self.crackZoneRefinement.setRange(1, 100)

        FXButton(
            p=gBox,
            ic=None,
            text="Show mesh seeds",
            tgt=self.form,
            sel=self.form.ID_MESH_SEEDS,
            opts=BUTTON_NORMAL | LAYOUT_SIDE_RIGHT)

    def createXfemWidgets(self, frame):
        """
        """
        self.xfemTabBook = FXTabBook(
            p=frame,
            tgt=self.form,
            sel=self.form.ID_XFEM_TYPE,
            opts=LAYOUT_FILL_Y | TABBOOK_TOPTABS)

        FXTabItem(
            p=self.xfemTabBook,
            text="simple",
            ic=None,
            opts=TAB_TOP)
        vFrame = FXVerticalFrame(
            p=self.xfemTabBook,
            opts=FRAME_RAISED | FRAME_SUNKEN)
        self.createSimpleXfemWidgets(vFrame)

        FXTabItem(
            p=self.xfemTabBook,
            text="crackPartition",
            ic=None,
            opts=TAB_TOP)
        vFrame = FXVerticalFrame(
            p=self.xfemTabBook,
            opts=FRAME_RAISED | FRAME_SUNKEN)
        self.createCrackPartitionWidgets(vFrame)

        FXTabItem(
            p=self.xfemTabBook,
            text="multiplePartitions",
            ic=None,
            opts=TAB_TOP)
        vFrame = FXVerticalFrame(
            p=self.xfemTabBook,
            opts=FRAME_RAISED | FRAME_SUNKEN)
        self.createXfemCrackMPWidgets(vFrame)

    def createSimpleXfemWidgets(self, frame):
        """
        """
        vFrame = FXVerticalFrame(p=frame, opts=LAYOUT_FILL_X)

        elements = AFXComboBox(
            p=vFrame,
            ncols=0,
            nvis=2,
            text="Elements",
            tgt=self.form.kw["xfemSimpleElements"],
            sel=0)
        elements.appendItem("LinearTet - C3D4")
        elements.appendItem("LinearHexRI - C3D8R")

        FXHorizontalSeparator(p=vFrame, opts=SEPARATOR_GROOVE | LAYOUT_FILL_X)

        gBox = FXGroupBox(
            p=vFrame,
            text="Mesh seeds",
            opts=FRAME_SUNKEN | FRAME_RAISED | LAYOUT_FILL_X)

        self.simpleContainerSeeds = AFXFloatSpinner(
            p=gBox,
            ncols=10,
            labelText="container seeds",
            tgt=self.form.kw["simpleContainerSeeds"],
            sel=0)

        FXHorizontalSeparator(p=vFrame, opts=SEPARATOR_GROOVE | LAYOUT_FILL_X)
        self.calcRadius = AFXFloatSpinner(
            p=vFrame,
            ncols=10,
            labelText="Singularity radius: ",
            tgt=self.form.kw["singularityRadius"],
            sel=0)
        self.calcRadius.setRange(0, 100)
        self.calcRadius.setIncrement(0.01)
        self.form.kw["singularityRadius"].setValue(0)

    def createCrackPartitionWidgets(self, frame):
        """
        """
        vFrame = FXVerticalFrame(p=frame, opts=LAYOUT_FILL_X)
        elements = AFXComboBox(
            p=vFrame,
            ncols=0,
            nvis=2,
            text="Elements",
            tgt=self.form.kw["xfemCPElements"],
            sel=0)
        elements.appendItem("LinearTet - C3D4")
        elements.disable()

        FXHorizontalSeparator(p=vFrame, opts=SEPARATOR_GROOVE | LAYOUT_FILL_X)

        gBox = FXGroupBox(
            p=vFrame,
            text="Mesh seeds",
            opts=FRAME_SUNKEN | FRAME_RAISED | LAYOUT_FILL_X)

        vAlign = AFXVerticalAligner(
            p=gBox, opts=LAYOUT_FILL_X)
        self.CPcrackSeeds = AFXFloatSpinner(
            p=vAlign,
            ncols=10,
            labelText="crackSeeds",
            tgt=self.form.kw["CPcrackSeeds"],
            sel=0)
        self.CPcontainerSeeds = AFXFloatSpinner(
            p=vAlign,
            ncols=10,
            labelText="containerSeeds",
            tgt=self.form.kw["CPcontainerSeeds"],
            sel=0)
        self.CPcontainerSeeds.setRange(1, 100)

        FXHorizontalSeparator(p=vFrame, opts=SEPARATOR_GROOVE | LAYOUT_FILL_X)
        self.calcRadius = AFXFloatSpinner(
            p=vFrame,
            ncols=10,
            labelText="Singularity radius: ",
            tgt=self.form.kw["singularityRadius"],
            sel=0)
        self.calcRadius.setRange(0, 100)
        self.calcRadius.setIncrement(0.01)
        self.form.kw["singularityRadius"].setValue(0)

    def createXfemCrackMPWidgets(self, frame):
        """
        """
        vFrame = FXVerticalFrame(p=frame, opts=LAYOUT_FILL_X)
        elements = AFXComboBox(
            p=vFrame,
            ncols=0,
            nvis=2,
            text="Elements",
            tgt=self.form.kw["xfemMPElements"],
            sel=0)
        elements.appendItem("LinearHexRI - C3D8R")
        elements.appendItem("LinearHexFI - C3D8")
        FXHorizontalSeparator(p=vFrame, opts=SEPARATOR_GROOVE | LAYOUT_FILL_X)

        gBox = FXGroupBox(
            p=vFrame,
            text="Mesh partition dimensions",
            opts=FRAME_SUNKEN | FRAME_RAISED | LAYOUT_FILL_X)
        vAlign = AFXVerticalAligner(p=gBox)

        self.xfemMPoffset = AFXFloatSpinner(
            p=vAlign,
            ncols=10,
            labelText="offset",
            tgt=self.form.kw["xfemMPoffset"],
            sel=0)
        self.xfemMPoffset.setRange(1, 100)

        self.xfemMPheight = AFXFloatSpinner(
            p=vAlign,
            ncols=10,
            labelText="height",
            tgt=self.form.kw["xfemMPheight"],
            sel=0)
        self.xfemMPheight.setRange(1, 100)

        FXButton(
            p=gBox,
            ic=None,
            text="Show mesh partitions",
            tgt=self.form,
            sel=self.form.ID_XFEM_MP_MESH_PARTITIONS,
            opts=BUTTON_NORMAL | LAYOUT_SIDE_RIGHT)

        gBox = FXGroupBox(
            p=vFrame,
            text="Mesh seeds",
            opts=FRAME_SUNKEN | FRAME_RAISED | LAYOUT_FILL_X)
        vAlign = AFXVerticalAligner(p=gBox)

        self.xfemMPContainer = AFXFloatSpinner(
            p=vAlign,
            ncols=10,
            labelText="container",
            tgt=self.form.kw["xfemMPcontainerSeeds"],
            sel=0)
        self.xfemMPContainer.setRange(1, 100)

        self.xfemMPsmallContainer = AFXFloatSpinner(
            p=vAlign,
            ncols=10,
            labelText="small container",
            tgt=self.form.kw["xfemMPsmallContainerSeeds"],
            sel=0)
        self.xfemMPsmallContainer.setRange(1, 100)

        FXButton(
            p=gBox,
            ic=None,
            text="Show mesh seeds",
            tgt=self.form,
            sel=self.form.ID_XFEM_MP_MESH_SEEDS,
            opts=BUTTON_NORMAL | LAYOUT_SIDE_RIGHT)

        FXHorizontalSeparator(
            p=vFrame,
            opts=SEPARATOR_GROOVE | LAYOUT_FILL_X)
        self.calcRadius = AFXFloatSpinner(
            p=vFrame,
            ncols=10,
            labelText="Singularity radius: ",
            tgt=self.form.kw["singularityRadius"],
            sel=0)
        self.calcRadius.setRange(0, 100)
        self.calcRadius.setIncrement(0.01)
        self.form.kw["singularityRadius"].setValue(0)

    def createFEMmeshPartition(self):
        """
        """
        iconPath = self.form.kw["iconDir"].getValue() + "fem_dimensions.png"
        dialog = DescriptiveImageDialog(
            title="Crack container partitions",
            legend="Mesh partitions",
            iconPath=iconPath,
            w=581,
            h=567
        )

    def createFEMmeshSeeds(self):
        """
        """
        iconPath = self.form.kw["iconDir"].getValue() + "fem_seeds.png"
        dialog = DescriptiveImageDialog(
            title="Crack container seeds",
            legend="Mesh seeds",
            iconPath=iconPath,
            w=581,
            h=567
        )

    def createXfemMPmeshSeeds(self):
        """
        """
        iconPath = self.form.kw["iconDir"].getValue() + "xfem_mp_seeds.png"
        dialog = DescriptiveImageDialog(
            title="Crack container seeds",
            legend="xfem MP mesh seeedss",
            iconPath=iconPath,
            w=581,
            h=567
        )

    def createXfemMPmeshPartitions(self):
        """
        """
        iconPath = self.form.kw["iconDir"].getValue() + "xfem_mp_dimensions.png"
        dialog = DescriptiveImageDialog(
            title="Crack container partitions",
            legend="xfem MP mesh partitions",
            iconPath=iconPath,
            w=288,
            h=567
        )


class DescriptiveImageDialog(AFXDialog):
    """
    """
    def __init__(self, title, legend, iconPath, w, h):
        """
        """
        AFXDialog.__init__(
            self,
            title,
            self.DISMISS,
            DIALOG_ACTIONS_SEPARATOR)
        self.createImage(legend, iconPath, w, h)
        self.create()
        self.show()

    def createImage(self, legend, iconPath, w, h):
        frame = FXHorizontalFrame(
            p=self,
            opts=LAYOUT_FILL_X | LAYOUT_FILL_Y,
            pl=0, pr=0, pt=0, pb=0)
        gBox = FXGroupBox(
            p=frame,
            text=legend,
            opts=FRAME_GROOVE | LAYOUT_FILL_Y)
        table = AFXTable(
            p=gBox,
            numVisRows=1,
            numVisColumns=1,
            numRows=1,
            numColumns=1,
            tgt=None,
            sel=0)
        icon = afxCreatePNGIcon(iconPath)
        table.setItemIcon(row=0, column=0, icon=icon)
        table.setColumnWidth(0, w)
        table.setRowHeight(0, h)
        table.recalc()


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
            text="Current model database will be closed without being saved!")
