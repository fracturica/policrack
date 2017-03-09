

import math
import miscFunctions
import baseAE


class EmbeddedCrackAnalyticalSolutions(baseAE.BaseAnalyticalExpressions):
    """
    """
    def initializeParameters(self):
        """
        """
        tensileStress = self.data["input"]["sigma"]
        a = float(max(self.data["input"]["a"], self.data["input"]["b"]))/2.0
        b = float(min(self.data["input"]["a"], self.data["input"]["b"]))/2.0
        v = self.data["input"]["v"]
        gamma = math.radians(float(self.data["input"]["gamma"]))
        omega = math.radians(float(self.data["input"]["omega"]))
        k = math.sqrt(1.0 - (b/a)**2)

        self.data["sigma"] = tensileStress * math.cos(gamma)**2
        self.data["tao"] = tensileStress * math.sin(gamma)*math.cos(gamma)

        self.data["E(k)"] = miscFunctions.compEllipIntE(k)
        self.data["K(k)"] = miscFunctions.compEllipIntK(k)
        self.data["R"] = miscFunctions.Rfun({"a": a, "b": b, "k": k, "v": v})
        self.data["Q"] = miscFunctions.Qfun({"a": a, "b": b, "k": k, "v": v})

        self.data["a"] = a
        self.data["b"] = b
        self.data["gamma"] = gamma
        self.data["omega"] = omega
        self.data["k"] = k
        self.data["v"] = v

    def k1(self, beta):
        """
        """
        beta = math.radians(float(beta))
        sigma = self.data["sigma"]
        a = self.data["a"]
        b = self.data["b"]
        k = self.data["k"]
        Ek = self.data["E(k)"]

        term1 = sigma * math.sqrt(math.pi*b/a) / Ek
        term2 = (((a**4)*(math.sin(beta))**2 + (b**4)*(math.cos(beta))**2) /
                 ((a**2)*(math.sin(beta))**2 + (b**2)*(math.cos(beta))**2))**0.25
        k1 = term1*term2
        return k1

    def k2(self, beta):
        """
        """
        beta = math.radians(float(beta))
        gamma = self.data["gamma"]
        omega = self.data["omega"]
        tao = self.data["tao"]
        v = self.data["v"]
        a = self.data["a"]
        b = self.data["b"]
        k = self.data["k"]
        R = self.data["R"]
        Q = self.data["Q"]

        term1 = -tao * math.sqrt(math.pi*b/a)
        term2a = (b**2) * R * math.cos(beta) * math.cos(omega)
        term2b = (a**2) * Q * math.sin(beta) * math.sin(omega)
        term3a = ((a**2) * math.sin(beta)**2 + (b**2) * math.cos(beta)**2)**0.25
        term3b = ((a**4) * math.sin(beta)**2 + (b**4) * math.cos(beta)**2)**0.25

        k2 = term1 * (term2a + term2b) / (term3a * term3b)
        return k2

    def k3(self, beta):
        """
        """
        beta = math.radians(float(beta))
        gamma = self.data["gamma"]
        omega = self.data["omega"]
        sigma = self.data["sigma"]
        tao = self.data["tao"]
        v = self.data["v"]
        a = self.data["a"]
        b = self.data["b"]
        k = self.data["k"]
        Ek = self.data["E(k)"]
        R = self.data["R"]
        Q = self.data["Q"]

        term1 = tao * (1-v) * math.sqrt(math.pi*b/a)
        term2a = (a**2) * R * math.sin(beta) * math.cos(omega)
        term2b = (b**2) * Q * math.cos(beta) * math.sin(omega)
        term3a = ((a**2) * math.sin(beta)**2 + (b**2) * math.cos(beta)**2)**0.25
        term3b = ((a**4) * math.sin(beta)**2 + (b**4) * math.cos(beta)**2)**0.25

        k3 = term1 * (term2a - term2b) / (term3a * term3b)
        return k3

    def j(self, beta):
        """
        """
        pass
