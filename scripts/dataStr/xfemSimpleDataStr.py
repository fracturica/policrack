

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

import xfemBaseDataStr


class XFEMsimpleDataStr(xfemBaseDataStr.XFEMbaseDataStr):
    """
    """
    def __init__(self):
        """
        """
        xfemBaseDataStr.XFEMbaseDataStr.__init__(self)
        self.dataStr["input"]["modelType"] = "simple"
