"""Boundary for SWAN."""
from typing import Literal, Optional, Any
from pathlib import Path
from typing_extensions import Literal
from pydantic import root_validator, confloat, constr

from rompy.swan.components.base import BaseComponent
from rompy.swan.subcomponents.shape import SHAPESPEC
from rompy.swan.subcomponents.boundary import (
    SIDE,
    SEGMENTXY,
    SEGMENTIJ,
    CONSTANTPAR,
    VARIABLEPAR,
    CONSTANTFILE,
    VARIABLEFILE,
)


HERE = Path(__file__).parent


class BOUNDSPEC(BaseComponent):
    """SWAN BOUNDSPEC boundary component.

    `BOUNDSPEC SIDE|SEGMENT ... CONSTANT|VARIABLE PAR|FILE ...`

    This command BOUNDSPEC defines parametric spectra at the boundary. It consists of
    two parts, the first part defines the boundary side or segment where the spectra
    will be given, the second part defines the spectral parameters of these spectra.
    Note that in fact only the incoming wave components of these spectra are used by
    SWAN. The fact that complete spectra are calculated at the model boundaries from
    the spectral parameters should not be misinterpreted. Only the incoming components
    are effective in the computation.

    Parameters
    ----------
    model_type: Literal["boundspec"]
        Model type discriminator.
    shapespec: Optional[SHAPESPEC]
        Spectral shape specification.
    location: SIDE | SEGMENTXY | SEGMENTIJ
        Location to apply th boundary.
    data: CONSTANTPAR | CONSTANTFILE | VARIABLEPAR | VARIABLEFILE
        Spectral data.

    TODO: Add support for unstructured grid (k).

    """

    model_type: Literal["boundspec"] = "boundspec"
    shapespec: SHAPESPEC = SHAPESPEC()
    location: SIDE | SEGMENTXY | SEGMENTIJ
    data: CONSTANTPAR | CONSTANTFILE | VARIABLEPAR | VARIABLEFILE

    def __repr__(self):
        repr = f"{self.shapespec.render()}\n"
        repr += f"BOUNDSPEC {self.location.render()}{self.data.render()}"
        return repr


class BOUNDNEST1(BaseComponent):
    """Boundary spectra from a coarser SWAN nest at all sides of computational domain.

    `BOUNDNEST1 NEST 'fname CLOSED|OPEN`

    Parameters
    ----------
    model_type: Literal["boundnest1"]
        Model type discriminator.
    fname: str
        Name of the file containing the boundary conditions for the present run,
        created by the previous SWAN coarse grid run. This file is structured
        according to the rules given in Appendix D for 2D spectra.
    rectangle: Literal["closed", "open"]
        Defines if the boundary is defined over a closed (default) or an open
        rectangle. Boundary generated from the NESTOUT command is aways closed.

    With this optional command a nested SWAN run can be carried out with the boundary
    conditions obtained from a coarse grid SWAN run (generated in that previous SWAN
    run with command NESTOUT). The spectral frequencies and directions of the coarse
    grid run do not have to coincide with the frequencies and directions used in the
    nested SWAN run; SWAN will interpolate to these frequencies and directions in the
    nested run (see Section 2.6.3). To generate the nest boundary in the coarse grid
    run, use command NGRID. For the nested run, use the command CGRID with identical
    geographical information except the number of meshes (which will be much higher for
    the nested run). This BOUNDNEST1 command is not available for 1D computations; in
    such cases the commands SPECOUT and BOUNDSPEC can be used for the same purpose. A
    nested SWAN run must use the same coordinate system as the coarse grid SWAN run.
    For a curvilinear grid, it is advised to use the commands POINTS or CURVE and
    SPECOUT instead of NGRID and NESTOUT.

    """

    model_type: Literal["boundnest1"] = "boundnest1"
    fname: constr(min_length=1, max_length=98)
    rectangle: Literal["closed", "open"] = "closed"

    def __repr__(self):
        return f"BOUNDNEST1 NEST fname='{self.fname}' {self.rectangle.upper()}"
