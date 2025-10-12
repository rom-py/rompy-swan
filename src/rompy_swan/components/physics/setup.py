"""SWAN wave setup component.

This module contains the SETUP component for wave-induced setup in SWAN.
"""

from typing import Literal, Optional

from pydantic import Field

from rompy_swan.components.base import BaseComponent


class SETUP(BaseComponent):
    """Wave setup.

    .. code-block:: text

        SETUP [supcor]

    If this command is given, the wave-induced set-up is computed and accounted for in
    the wave computations (during the computation it is added to the depth that is
    obtained from the `READ BOTTOM` and `READ WLEVEL` commands). This approximation in
    SWAN can only be applied to open coast (unlimited supply of water from outside the
    domain, e.g. nearshore coasts) in contrast to closed basin, e.g. lakes and
    estuaries, where this option should not be used. Note that set-up is not computed
    correctly with spherical coordinates.

    Notes
    -----

    * The SETUP command cannot be used in case of unstructured grids.
    * Set-up is not supported in case of parallel runs using either MPI or OpenMP.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics import SETUP
        setup = SETUP()
        print(setup.render())
        setup = SETUP(supcor=0.5)
        print(setup.render())

    """

    model_type: Literal["setup", "SETUP"] = Field(
        default="setup", description="Model type discriminator"
    )
    supcor: Optional[float] = Field(
        default=None,
        description=(
            "By default the wave-induced set-up is computed with a constant added "
            "such that the set-up is zero in the deepest point in the computational "
            "grid. The user can modify this constant by the value of `supcor`. The "
            "user can thus impose a set-up in any one point (and only one) in the "
            "computational grid by first running SWAN, then reading the set-up in "
            "that point and adding or subtracting the required value of `supcor` "
            "(in m; positive if the set-up has to rise) (SWAN default: 0.0)"
        ),
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "SETUP"
        if self.supcor is not None:
            repr += f" supcor={self.supcor}"
        return repr
