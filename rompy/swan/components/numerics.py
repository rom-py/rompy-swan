"""Model physics components."""
import logging
from typing import Any, Literal, Optional, Union, Annotated
from pydantic import field_validator, model_validator, Field, FieldValidationInfo

from rompy.swan.components.base import BaseComponent
from rompy.swan.types import IDLA, PhysicsOff
from rompy.swan.subcomponents.physics import (
    JANSSEN,
    KOMEN,
    WESTHUYSEN,
    ST6,
    ST6C1,
    ST6C2,
    ST6C3,
    ST6C4,
    ST6C5,
    ELDEBERKY,
    DEWIT,
    TRANSM,
    TRANS1D,
    TRANS2D,
    GODA,
    DANGREMOND,
    REFL,
    RSPEC,
    RDIFF,
    FREEBOARD,
    LINE,
)


logger = logging.getLogger(__name__)



class BSBT(BaseComponent):
    """BSBT first order propagation scheme."""

    model_type: Literal["bsbt", "BSBT"] = Field(
        default="bsbt", description="Model type discriminator"
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        return "BSBT"


class GSE(BaseComponent):
    """Third order propagation scheme with conteraction to the garden-sprinkler effect.

    Garden-sprinkler effect is to be counteracted in the S&L propagation scheme
    (default for nonstationary regular grid computations) or in the propagation
    scheme for unstructured grids by adding a diffusion term to the basic equation.
    This may affect the numerical stability of SWAN.

    Examples
    --------

    .. ipython:: python
        :okwarning:
        :okexcept:

        @suppress
        from rompy.swan.components.numerics import GSE

        scheme = GSE(waveage=1, units="day")
        print(scheme.render())

    """

    model_type: Literal["gse", "GSE"] = Field(
        default="gse", description="Model type discriminator"
    )
    waveage: Optional[float] = Field(
        default=None,
        description=(
            "The time interval used to determine the diffusion which counteracts the "
            "so-called garden-sprinkler effect. The default value of `waveage` is "
            "zero, i.e. no added diffusion. The value of `waveage` should correspond "
            "to the travel time of the waves over the computational region.",
        ),
    )
    units: Literal["sec", "min", "hr", "day"] = Field(
        default="hr", description="Units for waveage",
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "GSE"
        if self.waveage is not None:
            repr += f" {self.waveage} {self.units.upper()}"
        return repr


PROP_TYPE = Annotated[
    Union[BSBT, GSE],
    Field(description="Propagation scheme", discriminator="model_type"),
]

class PROP(BaseComponent):
    """Propagation scheme.

    .. code-block:: text

        PROP BSTB|GSE

    Notes
    -----
    * The scheme defaults to `S&L` and `SORDUP` for nonstationary and stationary
      simulations if not specified.
    * All schemes (BSBT, SORDUP and S&L) can be used in combination with curvilinear
      grids. With the higher order schemes (S&L and SORDUP) it is important to use a
      gradually varying grid otherwise there may be a severe loss of accuracy. If sharp
      transitions in the grid cannot be avoided it is safer to use the BSBT scheme.
    * In the computation with unstructured meshes, a lowest order upwind scheme will be
      employed. This scheme is very robust but rather diffusive. This may only be
      significant for the case when swell waves propagate over relative large distances
      (in the order of thousands of kilometers) within the model domain. However and
      most fortunately, in such a case this will alleviate the garden-sprinkler effect.
    * Alleviating the garden-sprinkler effect by adding some diffusion makes the SWAN
      computation conditionally stable. You can either use (i) a smaller time step,
      (ii) a lower value of `waveage`, (iii) better resolution in the directional
      space, or (iv) worse resolution in the geographic space, in order of preference,
      to make the model stable when necessary.

    Examples
    --------

    .. ipython:: python
        :okwarning:
        :okexcept:

        @suppress
        from rompy.swan.components.numerics import PROP

        prop = PROP()
        print(prop.render())
        prop = PROP(scheme=dict(model_type="bsbt"))
        print(prop.render())
        prop = PROP(scheme=dict(model_type="gse", waveage=5, units="hr"))
        print(prop.render())

    """
    model_type: Literal["prop", "PROP"] = Field(
        default="prop", description="Model type discriminator"
    )
    scheme: Optional[PROP_TYPE] = Field(
        default=None,
        description=(
            "Propagation scheme, by default S&L for nonstationary and SORDUP for "
            "stationary computation."
        ),
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "PROP"
        if self.scheme is not None:
            repr += f" {self.scheme.render()}"
        return repr
