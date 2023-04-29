"""Computational grid for SWAN."""
from enum import Enum, IntEnum
import logging
from pydantic import validator, root_validator, conint, confloat, constr

from rompy.core import RompyBaseModel
from rompy.swan.components.base import BaseComponent, FormatEnum


logger = logging.getLogger(__name__)


class IDFMEnum(IntEnum):
    one = 1
    five = 5
    six = 6
    eight = 8


class UnstructuredEnum(str, Enum):
    """Enum for SWAN unstructured grid kinds."""
    adcirc = "adcirc"
    triangle = "triangle"
    easymesh = "easymesh"


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
    name: str = "Computational grid"
    mdc: int
    flow: float | None = None
    fhigh: float | None = None
    msc: conint(ge=3) | None = None
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
        repr = f"{self.dir_sector} mdc={self.mdc}"
        if self.flow is not None:
            repr += f" flow={self.flow}"
        if self.fhigh is not None:
            repr += f" fhigh={self.fhigh}"
        if self.msc is not None:
            repr += f" msc={self.msc}"
        return repr


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
        repr = (
            f"CGRID REGULAR xpc={self.xpc} ypc={self.ypc} alpc={self.alpc} "
            f"xlenc={self.xlenc} ylenc={self.ylenc} mxc={self.mxc} myc={self.myc} "
            f"{super().__repr__()}"
        )
        return repr


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
    fname: str
        Name of the coordinates file to read. These coordinates must be read from a
        file as a vector (x-coordinate, y-coordinate of each single grid point).
    fac: float
        SWAN multiplies all values that are read from file by `fac`. For instance if
        the values are given in unit decimeter, one should make `fac=0.1` to obtain
        values in m. To change sign use a negative `fac`.
    idla: int
        prescribes the order in which the values of bottom levels and other fields
        should be given in the file:
        - 1: SWAN reads the map from left to right starting in the upper-left-hand
          corner of the map (it is assumed that the x-axis of the grid is pointing
          to the right and the y-axis upwards). A new line in the map should start on
          a new line in the file.
        - 2: As `1` but a new line in the map need not start on a new line in the file.
        - 3: SWAN reads the map from left to right starting in the lower-left-hand corner
          of the map. A new line in the map should start on a new line in the file.
        - 4: As `3` but a new line in the map need not start on a new line in the file.
        - 5: SWAN reads the map from top to bottom starting in the lower-left-hand corner
          of the map. A new column in the map should start on a new line in the file.
        - 6: As `5` but a new column in the map need not start on a new line in the file.
    nhedf: int
        The number of header lines at the start of the file. The text in the header
        lines is reproduced in the print file created by SWAN. The file may start with
        more header lines than `nhedf` because the start of the file is often also the
        start of a time step and possibly also of a vector variable (each having header
        lines, see below, `nhedvec`).
    nhedvec: int
        For each vector variable: number of header lines in the file at the start of
        each component (e.g., x- or y-component).
    format: str
        File format, one of `"free"`, `"fixed"` or `"unformatted"`. If `"free"`, the
        file is assumed to use the FREE FORTRAN format. If `"fixed"`, the file is
        assumed to use a fixed format that must be specified by (only) one of `form` or
        `idfm` arguments. Use `"unformatted"` to read unformatted (binary) files
        (not recommended for ordinary use).
    form: str
        A user-specified format string in Fortran convention, e.g., '(10X,12F5.0)'.
        Only used if `format="fixed"`, do not use it if `idfm` is specified.
    idfm: int
        File format identifier interpreted as follows:
        - 1: Format according to BODKAR convention (a standard of the Ministry of
          Transport and Public Works in the Netherlands). Format string: (10X,12F5.0).
        - 5: Format (16F5.0), an input line consists of 16 fields of 5 places each.
        - 6: Format (12F6.0), an input line consists of 12 fields of 6 places each.
        - 8: Format (10F8.0), an input line consists of 10 fields of 8 places each.
        Only used if `format="fixed"`, do not use it if `form` is specified.

    """
    mxc: int
    myc: int
    xexc: float | None = None
    yexc: float | None = None
    fname: constr(max_length=80)
    fac: confloat(gt=0.0) = 1.0
    idla: conint(ge=1, le=6) = 1
    nhedf: int = 0
    nhedvec: int = 0
    format: FormatEnum = "free"
    form: str | None = None
    idfm: IDFMEnum | None = None

    @root_validator
    def check_exception_definition(cls, values: dict) -> dict:
        """Check exception values are prescribed correctly."""
        xexc = values.get("xexc")
        yexc = values.get("yexc")
        if (xexc is None and yexc is not None) or (yexc is None and xexc is not None):
            raise ValueError("xexc and yexc must be specified together")
        return values

    @root_validator
    def check_format_definition(cls, values: dict) -> dict:
        """Check the arguments specifying the file format are specified correctly."""
        format = values.get("format")
        form = values.get("form")
        idfm = values.get("idfm")
        if format == "free" and any([form, idfm]):
            logger.warn(f"FREE format specified, ignoring form={form} idfm={idfm}")
        elif format == "unformatted" and any([form, idfm]):
            logger.warn(f"UNFORMATTED format specified, ignoring form={form} idfm={idfm}")
        elif format == "fixed" and not any([form, idfm]):
            raise ValueError("FIXED format requires one of form or idfm to be specified")
        elif format == "fixed" and all([form, idfm]):
            raise ValueError("FIXED format accepts only one of form or idfm")
        return values

    @property
    def exception(self):
        if self.xexc is not None:
            return f"EXCEPTION xexc={self.xexc} xexc={self.yexc}"
        else:
            return ""

    @property
    def format_repr(self):
        if self.format == "free":
            repr = "FREE"
        elif self.format == "fixed" and self.form:
            repr = f"FORMAT form='{self.form}'"
        elif self.format == "fixed" and self.idfm:
            repr = f"FORMAT idfm={self.idfm}"
        elif self.format == "unformatted":
            repr = "UNFORMATTED"
        return repr

    def __repr__(self):
        repr = f"CGRID CURVILINEAR mxc={self.mxc} myc={self.myc}"
        if self.exception:
            repr += f" {self.exception}"
        repr += f" {super().__repr__()}"
        repr += (
            f"\nREADGRID COORDINATES fac={self.fac} fname='{self.fname}' idla={self.idla} "
            f"nhedf={self.nhedf} nhedvec={self.nhedvec} {self.format_repr}"
        )
        return repr


class CGridUnstructured(CGrid):
    """SWAN unstructured computational grid."""
    kind: UnstructuredEnum = "adcirc"
    fname: constr(max_length=80) | None = None

    @root_validator
    def check_fname_required(cls, values: dict) -> dict:
        """Check that fname needs to be provided."""
        kind = values.get("kind")
        fname = values.get("fname")
        if kind == "adcirc" and fname is not None:
            raise ValueError("fname must not be specified for ADCIRC grid")
        elif kind != "adcirc" and fname is None:
            raise ValueError(f"fname must be specified for {kind} grid")
        return values

    def __repr__(self):
        repr = f"CGRID UNSTRUCTURED {super().__repr__()}"
        repr += f"\nREADGRID UNSTRUCTURED {self.kind.upper()}"
        if self.kind in ["triangle", "easymesh"]:
            repr += f" fname='{self.fname}'"
        return repr


if __name__ == "__main__":

    cgrid = CGridRegular(
        mdc=36, flow=0.04, fhigh=0.4, xlenc=100.0, ylenc=100.0, mxc=10, myc=10
    )
    print(cgrid.render())

    cgrid = CGridCurvilinear(
        mdc=36, flow=0.04, fhigh=0.4, mxc=10, myc=10, fname="grid_coord.txt"
    )
    print(cgrid.render())

    cgrid = CGridUnstructured(mdc=36, flow=0.04, fhigh=0.4)
    print(cgrid.render())
