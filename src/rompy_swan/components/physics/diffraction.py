"""SWAN wave diffraction component.

This module contains the DIFFRACTION component for wave diffraction in SWAN.
"""

from typing import Literal, Optional

from pydantic import Field

from rompy_swan.components.base import BaseComponent


class DIFFRACTION(BaseComponent):
    """Wave diffraction.

    .. code-block:: text

        DIFFRACTION [idiffr] [smpar] [smnum] [cgmod]

    If this optional command is given, the diffraction is included in the wave
    computation. But the diffraction approximation in SWAN does not properly handle
    diffraction in harbours or in front of reflecting obstacles (see
    Scientific/Technical documentation). Behind breakwaters with a down-wave beach, the
    SWAN results seem reasonable. The spatial resolution near (the tip of) the
    diffraction obstacle should be 1/5 to 1/10 of the dominant wave length.

    Notes
    -----
    Without extra measures, the diffraction computations with SWAN often converge
    poorly or not at all. Two measures can be taken:

    1. (RECOMMENDED) The user can request under-relaxation. See command `NUMERIC`
    parameter `alpha` and Scientific/Technical documentation (Eq. (3.31)). Very limited
    experience suggests `alpha = 0.01`.

    2. Alternatively, the user can request smoothing of the wave field for the
    computation of the diffraction parameter (the wave field remains intact for all
    other computations and output). This is done with a repeated convolution filtering.

    Examples
    --------

    .. ipython:: python

        from rompy_swan.components.physics import DIFFRACTION
        diffraction = DIFFRACTION()
        print(diffraction.render())
        diffraction = DIFFRACTION(idiffr=True, smpar=0.0, smnum=1.0)
        print(diffraction.render())

    """

    model_type: Literal["diffraction", "DIFFRACTION"] = Field(
        default="diffraction", description="Model type discriminator"
    )
    idiffr: Optional[bool] = Field(
        default=None,
        description=(
            "Indicates the use of diffraction. If `idiffr=0` then no diffraction is "
            "taken into account (SWAN default: 1)"
        ),
    )
    smpar: Optional[float] = Field(
        default=None,
        description=(
            "Smoothing parameter for the calculation of ∇ · √Etot. During every "
            "smoothing step all grid points exchange `smpar` times the energy with "
            "their neighbours. Note that `smpar` is parameter a in the above text "
            "(SWAN default: 0.0)"
        ),
    )
    smnum: Optional[int] = Field(
        default=None,
        description="Number of smoothing steps relative to `smpar` (SWAN default: 0)",
    )
    cgmod: Optional[float] = Field(
        default=None,
        description=(
            "Adaption of propagation velocities in geographic space due to "
            "diffraction. If `cgmod=0` then no adaption (SWAN default: 1.0)"
        ),
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "DIFFRACTION"
        if self.idiffr is not None:
            repr += f" idiffr={int(self.idiffr)}"
        if self.smpar is not None:
            repr += f" smpar={self.smpar}"
        if self.smnum is not None:
            repr += f" smnum={self.smnum}"
        if self.cgmod is not None:
            repr += f" cgmod={self.cgmod}"
        return repr
