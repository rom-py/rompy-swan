"""SWAN output component."""

from typing import Literal, Optional, Union

from pydantic import Field, field_validator, model_validator

from rompy.logging import get_logger
from rompy_swan.components.base import BaseComponent
from rompy_swan.subcomponents.base import IJ, XY

logger = get_logger(__name__)

SPECIAL_NAMES = ["BOTTGRID", "COMPGRID", "BOUNDARY", "BOUND_"]


class TEST(BaseComponent):
    """Write intermediate results.

    .. code-block:: text

        TEST [itest] [itrace] POINTS XY|IJ (PAR 'fname') (S1D 'fname') (S2D 'fname')

    Note
    ----
    The 6 source terms written due to the presence of the keyword S1D or S2D are: wind
    input, whitecapping, bottom friction, breaking, 3- and 4- wave interactions.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.output import TEST
        test = TEST(
            itest=10,
            points=dict(model_type="ij", i=[0, 0], j=[10, 20]),
            fname_par="integral_parameters.test",
            fname_s1d="1d_variance_density.test",
            fname_s2d="2d_variance_density.test",
        )
        print(test.render())
        import numpy as np
        test = TEST(
            points=dict(
                model_type="xy",
                x=np.linspace(172.5, 174.0, 25),
                y=25*[-38],
            ),
            fname_s2d="2d_variance_density.test",
        )
        print(test.render())

    TODO: Support `k` in POINTS IJ.

    """

    model_type: Literal["test", "TEST"] = Field(
        default="test", description="Model type discriminator"
    )
    itest: Optional[int] = Field(
        default=None,
        description=(
            "The level of test output, for values under 100 the amount is usually "
            "reasonable, for values above 200 it can be very large. Values of up to "
            "50 can be interpreted by the user (SWAN default: 1)"
        ),
    )
    itrace: Optional[int] = Field(
        default=None,
        description=(
            "SWAN writes a message (name of subroutine) to the PRINT file at the "
            "first `itrace` entries of each subroutine (SWAN default: 0)"
        ),
    )
    points: Union[XY, IJ] = Field(
        description="Points where detailed print output is produced (max of 50 points)",
        discriminator="model_type",
    )
    fname_par: Optional[str] = Field(
        default=None,
        description="Name of the file where the integral parameters are written to",
    )
    fname_par: Optional[str] = Field(
        default=None,
        description="Name of the file where the integral parameters are written to",
    )
    fname_s1d: Optional[str] = Field(
        default=None,
        description=(
            "Name of the file where the 1D variance density and 6 source terms are "
            "written to"
        ),
    )
    fname_s2d: Optional[str] = Field(
        default=None,
        description=(
            "Name of the file where the 2D variance density and 6 source terms are "
            "written to"
        ),
    )

    @field_validator("points")
    @classmethod
    def validate_points(cls, points: Union[XY, IJ]) -> Union[XY, IJ]:
        if points.size > 50:
            raise ValueError(f"Maximum of 50 points allowed in TEST, got {points.size}")
        return points

    @model_validator(mode="after")
    def at_least_one(self) -> "TEST":
        """Warns if no test file is being specified."""
        if all(v is None for v in [self.fname_par, self.fname_s1d, self.fname_s2d]):
            logger.warning(
                "TEST command prescribed with no output files, please ensure at least "
                "one of ()`fname_par`, `fname_s1d` or `fname_s2d`) is specified"
            )
        return self

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "TEST"
        if self.itest is not None:
            repr += f" itest={self.itest}"
        if self.itrace is not None:
            repr += f" itrace={self.itrace}"
        repr += f" POINTS {self.points.model_type.upper()}{self.points.render()}"
        if self.fname_par is not None:
            repr += f"PAR fname='{self.fname_par}' "
        if self.fname_s1d is not None:
            repr += f"S1D fname='{self.fname_s1d}' "
        if self.fname_s2d is not None:
            repr += f"S2D fname='{self.fname_s2d}' "
        return repr.rstrip()
