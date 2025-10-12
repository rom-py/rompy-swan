"""SWAN biphase parameterization models for TRIAD components.

This module contains all models used for biphase parameterization in triad interactions:
- ELDEBERKY: Biphase parameterization of Eldeberky (1999)
- DEWIT: Biphase parameterization of De Wit (2022)

These are private implementation details used as field types in TRIAD components.
"""

from typing import Literal, Optional

from pydantic import Field

from rompy_swan.subcomponents.base import BaseSubComponent


class ELDEBERKY(BaseSubComponent):
    """Biphase of Eldeberky (1999).

    .. code-block:: text

        BIPHASE ELDEBERKY [urcrit]

    Biphase parameterisation as a funtion of the Ursell number of Eldeberky (1999).

    References
    ----------
    Eldeberky, Y., Polnikov, V. and Battjes, J.A., 1996. A statistical approach for
    modeling triad interactions in dispersive waves. In Coastal Engineering 1996
    (pp. 1088-1101).

    Eldeberky, Y. and Madsen, P.A., 1999. Deterministic and stochastic evolution
    equations for fully dispersive and weakly nonlinear waves. Coastal Engineering,
    38(1), pp.1-24.

    Doering, J.C. and Bowen, A.J., 1995. Parametrization of orbital velocity
    asymmetries of shoaling and breaking waves using bispectral analysis. Coastal
    engineering, 26(1-2), pp.15-33.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics._biphase import ELDEBERKY
        biphase = ELDEBERKY()
        print(biphase.render())
        biphase = ELDEBERKY(urcrit=0.63)
        print(biphase.render())

    """

    model_type: Literal["eldeberky"] = Field(
        default="eldeberky", description="Model type discriminator"
    )
    urcrit: Optional[float] = Field(
        default=None,
        description=(
            "The critical Ursell number appearing in the parametrization. Note: the "
            "value of `urcrit` is setted by Eldeberky (1996) at 0.2 based on a "
            "laboratory experiment, whereas Doering and Bowen (1995) employed the "
            "value of 0.63 based on the field experiment data (SWAN default: 0.63)"
        ),
    )

    def cmd(self) -> str:
        repr = "BIPHASE ELDEBERKY"
        if self.urcrit is not None:
            repr += f" urcrit={self.urcrit}"
        return repr


class DEWIT(BaseSubComponent):
    """Biphase of De Wit (2022).

    .. code-block:: text

        BIPHASE DEWIT [lpar]

    Biphase parameterization based on bed slope and peak period of De Wit (2022).

    References
    ----------
    De Wit, F.P., 2022. Wave shape prediction in complex coastal systems (Doctoral
    dissertation, PhD. thesis. Delft University of Technology. https://repository.
    tudelft. nl/islandora/object/uuid% 3A0fb850a4-4294-4181-9d74-857de21265c2).

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics._biphase import DEWIT
        biphase = DEWIT()
        print(biphase.render())
        biphase = DEWIT(lpar=0.0)
        print(biphase.render())

    """

    model_type: Literal["dewit"] = Field(
        default="dewit", description="Model type discriminator"
    )
    lpar: Optional[float] = Field(
        default=None,
        description=(
            "Scales spatial averaging of the De Wit's biphase in terms of a multiple "
            "of peak wave length of the incident wave field. Note: `lpar` = 0` means "
            "no averaging (SWAN default: 0)"
        ),
    )

    def cmd(self) -> str:
        repr = "BIPHASE DEWIT"
        if self.lpar is not None:
            repr += f" lpar={self.lpar}"
        return repr
