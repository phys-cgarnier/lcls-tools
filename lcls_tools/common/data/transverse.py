import numpy as np
from typing import Any 
from pydantic import BaseModel, ConfigDict
from pytao import Tao


class BeamCalculations(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    parameters: str
    tao: Tao = Tao()
    element: Any

    def twiss(tao, element, which="design"):
        """Gets twiss for element, which can be model, design or base"""
        result = tao.ele_twiss(element, which=which)
        return [result[p] for p in ["beta_a", "alpha_a", "beta_b", "alpha_b"]]

    def bmag(self):
        pass

    def bmag_func(self, tao, element, reference_element):
        twiss = self.twiss(tao, element)
        twiss_reference = self.twiss(tao, reference_element)
        return self.bmag(twiss, twiss_reference)

    def beam_size(self, tao, element, emittance, reference_element):
        twiss = self.get_twiss(tao, element)
        beta_a, alpha_a, beta_b, alpha_b = twiss
        # Beam size is sqrt(beta * epsilon), where epsilon is emittance
        beam_size_a = np.sqrt(beta_a * emittance)
        beam_size_b = np.sqrt(beta_b * emittance)
        return beam_size_a, beam_size_b


    # normalized emmittance property

    @property
    def normalized_emittance(self):
        ne = 0
        return ne