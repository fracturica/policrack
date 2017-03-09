

import sys
import math

from abaqus import *
from abaqusConstants import *

import part
import material
import section
import assembly
import step
import interaction
import sketch
import regionToolset, displayGroupMdbToolset as dgm, mesh, load, job
import inpReader
import meshEdit

import xfemBaseCrack


class XFEMtetCrackMdb(xfemBaseCrack.BaseXFEMcrackMdb):
    """
    """
    def createAllParts(self):
        """
        """
        self.createSolidParts()
        self.createCrackPart()
        crackType = self.inputData.getCrackType()
        if crackType != "embedded":
            self.createCrackPartitionPart()

    def createInstancesForPartitioning(self):
        """
        """
        crackType = self.inputData.getCrackType()
        if crackType != "embedded":
            partitionPartName = self.inputData.getCrackPartitionData()["name"]
            self.createInstance(partitionPartName)

            (crackContainerPartName,) = self.inputData.getSolidPartsParameters().keys()
            self.createInstance(crackContainerPartName)
        else:
            self.createInstancesFromAllParts()
