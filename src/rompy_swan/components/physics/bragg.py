"""SWAN Bragg scattering components.

This module contains components for configuring Bragg scattering in SWAN.
"""

from typing import Literal, Optional

from pydantic import Field

from rompy_swan.components.base import BaseComponent
from rompy_swan.types import IDLA


class BRAGG(BaseComponent):
    """Bragg scattering.

    .. code-block:: text

        BRAGG [ibrag] [nreg] [cutoff]

    Using this optional command, the user activates a source term to represent the
    scattering of waves due to changes in the small-scale bathymetry based on the
    theory of Ardhuin and Herbers (2002). If this command is not used, SWAN will not
    account for Bragg scattering.

    The underlying process is related to the bed elevation spectrum that describes the
    random variability of the bathymetry at the scale of the wave length on top of a
    slowly varying depth. To input this spectrum in the model, two options are
    available. One option is to read a spectrum from a file. This single bottom
    spectrum will subsequently be applied in all active grid points. The assumption
    being made here is that the inputted bottom is gently sloping. Note that the bottom
    spectrum must be given as a function of the wave number `k`.

    Another option is to compute the spectrum by a Fourier transform from `x` to `k` of
    the bed modulations around a computational grid point. First, one must define a
    square region with a fixed size around the grid point in order to perform the
    Fourier transform. The size should correspond to a multiple of the wave length at
    which refraction is resolved (i.e. consistent with the mild slope assumption).
    Next, the amplitude modulation of the small-scale bathymetry is obtained by
    substracting a slowly varying bed level from the inputted high-resolution
    bathymetric data within this square region. Here, the smooth bed level is achieved
    using a bilinear fit. During the computation, however, SWAN employs the gently
    sloping bed as the mean of the original bathymetry within the given square around
    each computational grid point. Finally, the corresponding bottom spectrum is
    computed with an FFT.

    Notes
    -----
    The Bragg scattering source term to the action balance equation gives rise to a
    fairly stiff equation. The best remedy is to run SWAN in the nonstationary mode
    with a relatively small time step or in the stationary mode with some under
    relaxation (see command `NUM STAT [alfa]`).

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics import BRAGG
        bragg = BRAGG(nreg=200)
        print(bragg.render())
        bragg = BRAGG(ibrag=1, nreg=200, cutoff=5.0)
        print(bragg.render())

    """

    model_type: Literal["bragg", "BRAGG"] = Field(
        default="bragg", description="Model type discriminator"
    )
    ibrag: Optional[Literal[1, 2, 3]] = Field(
        default=None,
        description=(
            "Indicates the computation of Bragg scattering term:\n\n* 1: source term "
            "is calculated per sweep and bottom spectrum is interpolated at the "
            "difference wave number a priori (thus requiring storage)\n* 2: source "
            "term is calculated per sweep and bottom spectrum is interpolated at the "
            "difference wave number per sweep (no storage)\n* 3: source term is "
            "calculated per iteration and bottom spectrum is interpolated at the "
            "difference wave number per iteration (no storage)\n\n(SWAN default: 1)"
        ),
    )
    nreg: int = Field(
        description=(
            "Size of square region around computational grid point (centered) for "
            "computing the mean depth and, if desired, the bed elevation spectrum. It "
            "is expressed in terms of the number of grid points (per direction) "
            "of the inputted bottom grid"
        ),
    )
    cutoff: Optional[float] = Field(
        default=None,
        description=(
            "Cutoff to the ratio between surface and bottom wave numbers. Note: see"
            "the Scientific/Technical documentation for details (SWAN default: 5.0)"
        ),
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "BRAGG"
        if self.ibrag is not None:
            repr += f" ibrag={self.ibrag}"
        if self.nreg is not None:
            repr += f" nreg={self.nreg}"
        if self.cutoff is not None:
            repr += f" cutoff={self.cutoff}"
        return repr


class FT(BRAGG):
    """Bragg scattering with bottom spectrum computed from FFT.

    .. code-block:: text

        BRAGG [ibrag] [nreg] [cutoff] FT

    If this keyword is present the bottom spectrum will be computed in each active
    grid point using a Fast Fourier Transform (FFT).

    Notes
    -----
    The depth in each computational grid point is computed as the average of the
    inputted (high-resolution) bed levels within the square region.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics.bragg import FT
        bragg = FT(nreg=350)
        print(bragg.render())
        bragg = FT(ibrag=2, nreg=350, cutoff=5.0)
        print(bragg.render())

    """

    model_type: Literal["ft", "FT"] = Field(
        default="ft", description="Model type discriminator"
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        return f"{super().cmd()} FT"


class FILE(BRAGG):
    """Bragg scattering with bottom spectrum from file.

    .. code-block:: text

        BRAGG [ibrag] [nreg] [cutoff] FILE 'fname' [idla] [mkx] [mky] [dkx] [dky]

    The bed elevation spectrum `FB(kx, ky)` is read from a file.

    Notes
    -----
    This spectrum is taken to be uniform over the entire computational domain.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics.bragg import FILE
        bragg = FILE(fname="bottom_spectrum.txt", nreg=500, mkx=99, dkx=0.1)
        print(bragg.render())
        kwargs = dict(
            ibrag=3,
            nreg=500,
            cutoff=5.0,
            fname="bottom_spectrum.txt",
            mkx=99,
            mky=149,
            dkx=0.1,
            dky=0.1,
        )
        bragg = FILE(**kwargs)
        print(bragg.render())

    """

    model_type: Literal["file", "FILE"] = Field(
        default="file", description="Model type discriminator"
    )
    fname: str = Field(
        description="Name of file containing the bottom spectrum",
        max_length=36,
    )
    idla: Optional[IDLA] = Field(
        default=None,
        description=("Order in which the values should be given in the input files"),
    )
    mkx: int = Field(
        description=(
            "Number of cells in x-direction of the wave number grid related to bottom "
            "spectrum (this is one less than the number of points in this direction)"
        ),
    )
    mky: Optional[int] = Field(
        default=None,
        description=(
            "Number of cells in y-direction of the wave number grid related to bottom "
            "spectrum (this is one less than the number of points in this direction)"
            "(SWAN default: `mky = mkx`)"
        ),
    )
    dkx: float = Field(
        description=(
            "Mesh size in x-direction of the wave number grid related to bottom "
            "spectrum (1/m)"
        ),
    )
    dky: Optional[float] = Field(
        default=None,
        description=(
            "Mesh size in y-direction of the wave number grid related to bottom "
            "spectrum (1/m) (SWAN default: `dky = dkx`)"
        ),
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = f"{super().cmd()} FILE fname='{self.fname}'"
        if self.idla is not None:
            repr += f" idla={self.idla.value}"
        repr += f" mkx={self.mkx}"
        if self.mky is not None:
            repr += f" mky={self.mky}"
        repr += f" dkx={self.dkx}"
        if self.dky is not None:
            repr += f" dky={self.dky}"
        return repr
