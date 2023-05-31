"""Subcomponents to be rendered inside of components."""
from typing import Optional, Literal
from pydantic import root_validator, confloat

from rompy.swan.components.base import BaseComponent
from rompy.swan.types import SideOptions


class SIDE(BaseComponent):
    """SWAN SIDE BOUNDSPEC subcomponent.

    The boundary is one full side of the computational grid (in 1D cases either of the
    two ends of the 1D-grid). SHOULD NOT BE USED IN CASE OF CURVILINEAR GRIDS!

    Parameters
    ----------
    model_type: Literal["side"]
        Model type discriminator.
    side: Literal["north", "nw", "west", "sw", "south", "se", "east", "ne"]
        The side of the grid to apply the boundary to.

    """
    model_type: Literal["side"] = "side"
    side: Literal["north", "nw", "west", "sw", "south", "se", "east", "ne"]
    direction: Literal["ccw", "clockwise"] = "ccw"

    def __repr__(self):
        repr = f"BOUNDSPEC SIDE {self.side.upper()}"
        repr += f" {self.direction.upper()}"
        return repr


class SEGMENTXY(BaseComponent):
    """SWAN SEGMENT XY BOUNDSPEC subcomponent.

    The segment is defined by means of a series of points in terms of problem
    coordinates; these points do not have to coincide with grid points. The (straight)
    line connecting two points must be close to grid lines of the computational grid
    (the maximum distance is one hundredth of the length of the straight line).

    Parameters
    ----------
    model_type: Literal["segmentxy"]
        Model type discriminator.
    points: list[tuple[float, float]]
        Pairs of (x, y) values to define the segment.
    float_format: str
        The format to use for the floats in the points.

    """
    model_type: Literal["segmentxy"] = "segmentxy"
    points: list[tuple[float, float]]
    float_format: str = "0.8f"

    def render(self):
        repr = f"SEGMENT XY &"
        for point in self.points:
            repr += f"\n\t{point[0]:{self.float_format}} {point[1]:{self.float_format}} &"
        return repr


class SEGMENTIJ(BaseComponent):
    """SWAN SEGMENT IJ BOUNDSPEC subcomponent.

    The segment is defined by means of a series of computational grid points given in
    terms of grid indices (origin at 0,0); not all grid points on the segment have to
    be mentioned. If two points are on the same grid line, intermediate points are
    assumed to be on the segment as well.

    Parameters
    ----------
    model_type: Literal["segmentij"]
        Model type discriminator.
    points: list[tuple[int, int]]
        Pairs of (i, j) values to define the segment.

    """
    model_type: Literal["segmentxy"] = "segmentxy"
    points: list[tuple[int, int]]

    def __repr__(self):
        repr = f"SEGMENT XY &"
        for point in self.points:
            repr += f"\n\t{point[0]} {point[1]} &"
        return repr


class PAR(BaseComponent):
    """SWAN wave parameter definition.

    Parameters
    ----------
    model_type: Literal["par"]
        Model type discriminator.
    hs: float
        The significant wave height (m).
    per: float
        The characteristic period (s) of the energy spectrum (relative frequency; which
        is equal to absolute frequency in the absence of currents); `per` is the value
        of the peak period if option PEAK is chosen in command BOUND SHAPE or `per` is
        the value of the mean period, if option MEAN was chosen in command BOUND SHAPE.
    dir: float
        The peak wave direction θpeak (degrees), constant over frequencies.
    dd: float
        Coefficient of directional spreading; a $cos^m(θ)$ distribution is assumed.
        `dd` is interpreted as the directional standard deviation in degrees, if the
        option DEGREES is chosen in the command BOUND SHAPE. Default: `dd=30`.
        `dd` is interpreted as the power `m`, if the option POWER is chosen in the
        command BOUND SHAPE. Default: `dd=2`.
    len: Optional[int]
        Is the distance from the first point of the side or segment to the point along
        the side or segment for which the incident wave spectrum is prescribed.
        Note: these points do no have to coincide with grid points of the computational
        grid. `len` is the distance in m or degrees in the case of spherical
        coordinates, not in grid steps. The values of `len` should be given
        in ascending order. The length along a SIDE is measured in clockwise or
        counterclockwise direction, depending on the options CCW or CLOCKWISE (see
        above). The option CCW is default. In case of a SEGMENT the length is
        measured from the indicated begin point of the segment.

    """
    model_type: Literal["par"] = "par"
    hs: float
    per: float
    dir: float
    dd: float
    len: Optional[confloat(ge=0)]

    def __repr__(self):
        """Render subcomponent cmd."""
        repr = "PAR"
        if self.len is not None:
            repr += f" len={self.len}"
        repr += f" hs={self.hs} per={self.per} dir={self.dir} dd={self.dd}"
        return repr
