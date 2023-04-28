"""Computational grid for SWAN."""
from pydantic import validator, root_validator, conint

from rompy.core import RompyBaseModel
from rompy.swan.components.base import BaseComponent


class CGrid(BaseComponent):
    """SWAN computational grid.

    Parameters
    ----------
    mdc: int
        Number of meshes in θ-space. In the case of CIRCLE, this is the number of
        subdivisions of the 360 degrees of a circle so ∆θ = [360]/[mdc] is the spectral
        directional resolution. In the case of SECTOR, ∆θ = ([dir2] - [dir1])/[mdc].
        The minimum number of directional bins is 3 per directional quadrant.
    flow: float
        Lowest discrete frequency that is used in the calculation (in Hz).
    fhigh: float
        Highest discrete frequency that is used in the calculation (in Hz).
    msc: int
        One less than the number of frequencies. This defines the grid resolution in
        frequency-space between the lowest discrete frequency `flow` and the highest
        discrete frequency `fhigh`. This resolution is not constant, since the
        frequencies are distributed logarithmical: fi+1 = yfi with y is a constant.
        The minimum number of frequencies is 4.
    dir1: float
        The direction of the right-hand boundary of the sector when looking outward
        from the sector (required for option SECTOR) in degrees.
    dir2: float
        The direction of the left-hand boundary of the sector when looking outward
        from the sector (required for option SECTOR) in degrees.

    Notes
    -----
    Directions in the spectra are defined either as a CIRCLE or as a SECTOR. In the
    case of a SECTOR, both `dir1` and `dir2` must be specified. In the case of a
    CIRCLE, neither `dir1` nor `dir2` should be specified.

    """

    mdc: int
    flow: float | None = None
    fhigh: float | None = None
    msc: conint(gt=2) | None = None
    dir1: float | None = None
    dir2: float | None = None

    @root_validator
    def check_direction_definition(cls, values: dict) -> dict:
        """Check that dir1 and dir2 are specified together."""
        dir1 = values.get("dir1")
        dir2 = values.get("dir2")
        if None in [dir1, dir2] and dir1 != dir2:
            raise ValueError("dir1 and dir2 must be specified together")
        return values

    @root_validator
    def check_frequency_definition(cls, values: dict) -> dict:
        """Check spectral frequencies are prescribed correctly."""
        flow = values.get("flow")
        fhigh = values.get("fhigh")
        msc = values.get("msc")
        args = [flow, fhigh, msc]
        if None in args:
            args = [arg for arg in args if arg is not None]
            if len(args) != 2:
                raise ValueError("You must specify at least 2 of [flow, fhigh, msc]")
        if flow is not None and fhigh is not None and flow >= fhigh:
            raise ValueError("flow must be less than fhigh")
        return values

    @property
    def dir_sector(self):
        if self.dir1 is None and self.dir2 is None:
            return "CIRCLE"
        else:
            return f"SECTOR {self.dir1} {self.dir2}"

    def __repr__(self):
        str = f"{self.dir_sector} mdc={self.mdc}"
        if self.flow is not None:
            str += f" flow={self.flow}"
        if self.fhigh is not None:
            str += f" fhigh={self.fhigh}"
        if self.msc is not None:
            str += f" msc={self.msc}"
        return str


class CGridRegular(CGrid):
    """SWAN regular computational grid.

    Parameters
    ----------
    xpc: float
        Geographic location of the origin of the computational grid in the problem
        coordinate system (x-coordinate, in m).
    ypc: float
        Geographic location of the origin of the computational grid in the problem
        coordinate system (y-coordinate, in m).
    alpc: float
        direction of the positive x-axis of the computational grid (in degrees,
        Cartesian convention). In 1D-mode, `alpc` should be equal to the direction
        `alpinp`.
    xlenc: float
        Length of the computational grid in x-direction (in m). In case of spherical
        coordinates `xlenc` is in degrees.
    ylenc: float
        Length of the computational grid in y-direction (in m). In 1D-mode, `ylenc`
        should be 0. In case of spherical coordinates `ylenc` is in degrees.
    mxc: int
        Number of meshes in computational grid in x-direction (this number is one less
        than the number of grid points in this domain).
    myc: int
        Number of meshes in computational grid in y-direction (this number is one less
        than the number of grid points in this domain).  In 1D-mode, `myc` should be 0.

    """

    xpc: float = 0.0
    ypc: float = 0.0
    alpc: float = 0.0
    xlenc: float
    ylenc: float
    mxc: int
    myc: int

    def __repr__(self):
        str = (
            f"CGRID REGULAR xpc={self.xpc} ypc={self.ypc} alpc={self.alpc} "
            f"xlenc={self.xlenc} ylenc={self.ylenc} mxc={self.mxc} myc={self.myc} "
            f"{super().__repr__()}"
        )
        return str


class CGridCurvilinear(CGrid):
    """SWAN curvilinear computational grid.

    Parameters
    ----------
    mxc: int
        Number of meshes in computational grid in ξ-direction (this number
        is one less than the number of grid points in this domain).
    myc: int
        Number of meshes in computational grid in η-direction (this number
        is one less than the number of grid points in this domain).
    xexc: float
        the value which the user uses to indicate that a grid point is to be ignored
        in the computations (this value is provided by the user at the location of the
        x-coordinate considered in the file of the x-coordinates, see command
        READGRID COOR).
    yexc: float
        the value which the user uses to indicate that a grid point is to be ignored
        in the computations (this value is provided by the user at the location of the
        y-coordinate considered in the file of the y-coordinates, see command
        READGRID COOR).

    """

    mxc: int
    myc: int
    xexc: float | None = None
    yexc: float | None = None

    @root_validator
    def check_exception_definition(cls, values: dict) -> dict:
        """Check exception values are prescribed correctly."""
        xexc = values.get("xexc")
        yexc = values.get("yexc")
        if (xexc is None and yexc is not None) or (yexc is None and xexc is not None):
            raise ValueError("xexc and yexc must be specified together")
        return values

    @property
    def exception(self):
        if self.xexc is not None:
            return f"EXCEPTION xexc={self.xexc} xexc={self.yexc}"
        else:
            return ""

    def __repr__(self):
        str = f"CGRID CURVILINEAR mxc={self.mxc} myc={self.myc}"
        if self.exception:
            str += f" {self.exception}"
        str += f" {super().__repr__()}"
        return str


class CGridUnstructured(CGrid):
    """SWAN unstructured computational grid."""

    def __repr__(self):
        return f"CGRID UNSTRUCTURED {super().__repr__()}"


if __name__ == "__main__":

    cgrid = CGridRegular(
        mdc=36, flow=0.04, fhigh=0.4, xlenc=100.0, ylenc=100.0, mxc=10, myc=10
    )
    print(cgrid.render())

    cgrid = CGridCurvilinear(mdc=36, flow=0.04, fhigh=0.4, mxc=10, myc=10)
    print(cgrid.render())

    cgrid = CGridUnstructured(mdc=36, flow=0.04, fhigh=0.4)
    print(cgrid.render())
