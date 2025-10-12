"""SWAN reflection models for OBSTACLE components.

This module contains all models used for wave reflection from obstacles:
- REFL: Constant reflection coefficient
- RSPEC: Specular reflection
- RDIFF: Diffuse reflection
- FREEBOARD: Freeboard dependent transmission and reflection
- LINE: Line of points to define obstacle location

These are private implementation details used as field types in OBSTACLE components.
"""

from typing import Literal, Optional

from pydantic import Field, model_validator

from rompy_swan.subcomponents.base import BaseSubComponent


class REFL(BaseSubComponent):
    """Obstacle reflections.

    .. code-block:: text

        REFL [reflc]

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics._reflection import REFL
        refl = REFL()
        print(refl.render())
        refl = REFL(reflc=0.5)
        print(refl.render())

    """

    model_type: Literal["refl", "REFL"] = Field(
        default="refl", description="Model type discriminator"
    )
    reflc: Optional[float] = Field(
        default=None,
        description=(
            "Constant reflection coefficient (ratio of reflected over incoming "
            "significant wave height) (SWAN default: 1.0)"
        ),
    )

    def cmd(self) -> str:
        """Command file string for this subcomponent."""
        repr = "REFL"
        if self.reflc is not None:
            repr += f" reflc={self.reflc}"
        return repr


class RSPEC(BaseSubComponent):
    """Specular reflection.

    .. code-block:: text

        RSPEC

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics._reflection import RSPEC
        refl = RSPEC()
        print(refl.render())

    """

    model_type: Literal["rspec", "RSPEC"] = Field(
        default="rspec", description="Model type discriminator"
    )

    def cmd(self) -> str:
        """Command file string for this subcomponent."""
        return "RSPEC"


class RDIFF(BaseSubComponent):
    """Diffuse reflection.

    .. code-block:: text

        RDIFF [pown]

    Specular reflection where incident waves are scattered over reflected direction.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics._reflection import RDIFF
        refl = RDIFF()
        print(refl.render())
        refl = RDIFF(pown=1.0)
        print(refl.render())

    """

    model_type: Literal["rdiff", "RDIFF"] = Field(
        default="rdiff", description="Model type discriminator"
    )
    pown: Optional[float] = Field(
        default=None,
        description=(
            "Each incoming direction θ is scattered over reflected direction θ_refl "
            "according to cos^pown(θ-θ_refl). The parameter `pown` indicates the width"
            "of the redistribution function (SWAN default: 1.0)"
        ),
    )

    def cmd(self) -> str:
        """Command file string for this subcomponent."""
        repr = "RDIFF"
        if self.pown is not None:
            repr += f" pown={self.pown}"
        return repr


class FREEBOARD(BaseSubComponent):
    """Freeboard dependent transmission and reflection.

    .. code-block:: text

        FREEBOARD [hgt] [gammat] [gammar] [QUAY]

    With this option the user indicates that the fixed transmission `trcoef` and
    reflection `reflc` coefficients are freeboard dependent. The freeboard dependency
    has no effect on the transmission coefficient as computed using the DAM option.

    Notes
    -----
    See the Scientific/Technical documentation for background information on the
    `gammat` and `gammar` shape parameters.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics._reflection import FREEBOARD
        freeboard = FREEBOARD(hgt=2.0)
        print(freeboard.render())
        freeboard = FREEBOARD(hgt=2.0, gammat=1.0, gammar=1.0, quay=True)
        print(freeboard.render())

    """

    model_type: Literal["freeboard", "FREEBOARD"] = Field(
        default="freeboard", description="Model type discriminator"
    )
    hgt: float = Field(
        description=(
            "The elevation of the top of the obstacle or height of the quay above the "
            "reference level (same reference level as for the bottom). Use a negative "
            "value if the top is below that reference level. In case `hgt` is also "
            "specified in the DAM option, both values of `hgt` should be equal for "
            "consistency"
        ),
    )
    gammat: Optional[float] = Field(
        default=None,
        description=(
            "Shape parameter of relative freeboard dependency of transmission "
            "coefficient. This parameter should be higher than zero (SWAN default 1.0)"
        ),
        gt=0.0,
    )
    gammar: Optional[float] = Field(
        default=None,
        description=(
            "Shape parameter of relative freeboard dependency of reflection "
            "coefficient. This parameter should be higher than zero (SWAN default 1.0)"
        ),
        gt=0.0,
    )
    quay: bool = Field(
        default=False,
        description=(
            "With this option the user indicates that the freeboard dependency of the "
            "transmission and reflection coefficients also depends on the relative "
            "position of an obstacle-linked grid point with respect to the position "
            "of the obstacle line representing the edge of a quay. In case the active "
            "grid point is on the deeper side of the obstacle, then the correction "
            "factors are applied using the parameters `hgt`, `gammat` and `gammar`."
            "In case the active grid point is on the shallower side of the obstacle, "
            "the reflection coefficient is set to 0 and the transmission coefficient "
            "to 1."
        ),
    )

    def cmd(self) -> str:
        """Command file string for this subcomponent."""
        repr = "FREEBOARD"
        if self.hgt is not None:
            repr += f" hgt={self.hgt}"
        if self.gammat is not None:
            repr += f" gammat={self.gammat}"
        if self.gammar is not None:
            repr += f" gammar={self.gammar}"
        if self.quay:
            repr += " QUAY"
        return repr


class LINE(BaseSubComponent):
    """Line of points to define obstacle location.

    .. code-block:: text

        LINE < [xp] [yp] >

    With this option the user indicates that the fixed transmission `trcoef` and
    reflection `reflc` coefficients are freeboard dependent. The freeboard dependency
    has no effect on the transmission coefficient as computed using the DAM option.

    Notes
    -----
    Points coordinates should be provided in m If Cartesian coordinates are used or in
    degrees if spherical coordinates are used (see command `COORD`). At least two
    corner points must be provided.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics._reflection import LINE
        line = LINE(xp=[174.1, 174.2, 174.3], yp=[-39.1, -39.1, -39.1])
        print(line.render())

    """

    model_type: Literal["line", "LINE"] = Field(
        default="line", description="Model type discriminator"
    )
    xp: list[float] = Field(
        description="The x-coordinates of the points defining the line", min_length=2
    )
    yp: list[float] = Field(
        description="The y-coordinates of the points defining the line", min_length=2
    )

    @model_validator(mode="after")
    def check_length(self) -> "LINE":
        """Check that the length of xp and yp are the same."""
        if len(self.xp) != len(self.yp):
            raise ValueError("xp and yp must be the same length")
        return self

    def cmd(self) -> str:
        """Command file string for this subcomponent."""
        repr = "LINE"
        for xp, yp in zip(self.xp, self.yp):
            repr += f" {xp} {yp}"
        return repr
