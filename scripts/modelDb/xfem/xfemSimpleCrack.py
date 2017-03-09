

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


class SimpleXFEMcrackMdb(xfemBaseCrack.BaseXFEMcrackMdb):
    """
    """
    def createAllParts(self):
        """
        """
        self.createSolidParts()
        self.createCrackPart()

    def assignSectionToCrackDomain(self):
        """
        """
        sectionName = self.inputData.getSectionName()
        solidParts = self.inputData.getSolidPartsParameters()
        (name,) = solidParts.keys()
        crackDomainName = name

        part = self.mdb["parts"][crackDomainName]
        region = regionToolset.Region(cells=part.cells)
        part.SectionAssignment(
            region=region,
            sectionName=sectionName)
