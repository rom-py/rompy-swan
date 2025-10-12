"""SWAN vegetation component.

This module contains the VEGETATION component for configuring wave damping due to
vegetation in SWAN.
"""

from typing import Any, Literal, Union

from pydantic import Field, ValidationInfo, field_validator, model_validator

from rompy_swan.components.base import BaseComponent


class VEGETATION(BaseComponent):
    """Vegetation dumping.

    .. code-block:: text

        VEGETATION [iveg] < [height] [diamtr] [nstems] [drag] >

    With this command the user can activate wave damping due to vegetation based on the
    Dalrymple's formula (1984) as implemented by Suzuki et al. (2011). This damping is
    uniform over the wave frequencies. An alternative is the frequency-dependent
    (canopy) dissipation model of Jacobsen et al. (2019). If this command is not used,
    SWAN will not account for vegetation effects.

    The vegetation (rigid plants) can be divided over a number of vertical segments and
    so, the possibility to vary the vegetation vertically is included. Each vertical
    layer represents some characteristics of the plants. These variables as indicated
    below can be repeated as many vertical layers to be chosen.

    References
    ----------
    Dalrymple, R.A., Kirby, J.T. and Hwang, P.A., 1984. Wave diffraction due to areas
    of energy dissipation. Journal of waterway, port, coastal, and ocean engineering,
    110(1), pp.67-79.

    Jacobsen, N.G., Bakker, W., Uijttewaal, W.S. and Uittenbogaard, R., 2019.
    Experimental investigation of the wave-induced motion of and force distribution
    along a flexible stem. Journal of Fluid Mechanics, 880, pp.1036-1069.

    Suzuki, T., Zijlema, M., Burger, B., Meijer, M.C. and Narayan, S., 2012. Wave
    dissipation by vegetation with layer schematization in SWAN. Coastal Engineering,
    59(1), pp.64-71.

    Notes
    -----
    Vertical layering of the vegetation is not yet implemented for the
    Jacobsen et al. (2019) method.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics import VEGETATION
        # Single layer
        vegetation = VEGETATION(
            height=1.2,
            diamtr=0.1,
            drag=0.5,
            nstems=10,
        )
        print(vegetation.render())
        # 2 vertical layers
        vegetation = VEGETATION(
            iveg=1,
            height=[1.2, 0.8],
            diamtr=[0.1, 0.1],
            drag=[0.5, 0.5],
            nstems=[10, 5],
        )
        print(vegetation.render())

    """

    model_type: Literal["vegetation", "VEGETATION"] = Field(
        default="vegetation", description="Model type discriminator"
    )
    iveg: Literal[1, 2] = Field(
        default=1,
        description=(
            "Indicates the method for the vegetation computation (SWAN default: 1):\n"
            "\n* 1: Suzuki et al. (2011)\n* 2: Jacobsen et al. (2019)\n"
        ),
    )
    height: Union[float, list[float]] = Field(
        description="The plant height per layer (in m)"
    )
    diamtr: Union[float, list[float]] = Field(
        description="The diameter of each plant stand per layer (in m)"
    )
    drag: Union[float, list[float]] = Field(
        description="The drag coefficient per layer"
    )
    nstems: Union[int, list[int]] = Field(
        default=1,
        description=(
            "The number of plant stands per square meter for each layer. Note that "
            "`nstems` is allowed to vary over the computational region to account for "
            "the zonation of vegetation. In that case use the commands "
            "`IMPGRID NPLANTS` and `READINP NPLANTS` to define and read the "
            "vegetation density. The (vertically varying) value of `nstems` in this "
            "command will be multiplied by this horizontally varying plant density "
            "(SWAN default: 1)"
        ),
        validate_default=True,
    )

    @field_validator("height", "diamtr", "drag", "nstems")
    @classmethod
    def number_of_layers(cls, v: Any, info: ValidationInfo) -> Any:
        if v is None:
            return v
        elif not isinstance(v, list):
            v = [v]
        sizes = {k: len(v) for k, v in info.data.items() if isinstance(v, list)}
        if len(set(sizes.values())) > 1:
            raise ValueError(
                "The number of layers must be the same for all variables. "
                f"Got these number of layers: {sizes}"
            )
        return v

    @model_validator(mode="after")
    def jacomsen_layering_not_implemented(self) -> "VEGETATION":
        if self.iveg == 2 and len(self.nstems) > 1:
            raise NotImplementedError(
                "Vertical layering of the vegetation is not yet implemented for the "
                "Jacobsen et al. (2019) method, please define single layer"
            )
        return self

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = f"VEGETATION iveg={self.iveg}"
        for h, d, dr, n in zip(self.height, self.diamtr, self.drag, self.nstems):
            repr += f" height={h} diamtr={d} nstems={n} drag={dr}"
        return repr
