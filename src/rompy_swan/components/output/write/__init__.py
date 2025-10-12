"""
Output Write Components
=======================

This module contains components for writing SWAN output to files.

Usage
-----

Import specific write classes from their modules:

.. code-block:: python

    from rompy_swan.components.output.write.block import BLOCK
    from rompy_swan.components.output.write.table import TABLE
    from rompy_swan.components.output.write.specout import SPECOUT

Available Write Components
--------------------------

**Spatial Distributions** (`block.py`)
    - BLOCK - Write spatial distributions
    - BLOCKS - Write multiple spatial distributions

**Table Output** (`table.py`)
    - TABLE - Write table output

**Spectral Output** (`specout.py`)
    - SPECOUT - Write wave spectra

**Nested Output** (`nestout.py`)
    - NESTOUT - Write 2D boundary spectra for nested runs

Base Classes
------------

This package also defines the abstract base class `BaseWrite` that all write
components inherit from. Import it directly from this package:

.. code-block:: python

    from rompy_swan.components.output.write import BaseWrite
"""

from abc import ABC
from typing import Literal, Optional

from pydantic import Field, model_validator

from rompy_swan.components.base import BaseComponent
from rompy_swan.subcomponents.time import TimeRangeOpen

SPECIAL_NAMES = ["BOTTGRID", "COMPGRID", "BOUNDARY", "BOUND_"]


class BaseWrite(BaseComponent, ABC):
    """Base class for SWAN output writing.

    .. code-block:: text

        {MODEL_TYPE} sname='sname'

    This is the base class for all write components. It is not meant to be used
    directly.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.output.write import BaseWrite
        write = BaseWrite(
            sname="outgrid",
            fname="./output-grid.nc",
            times=dict(
                tbeg="2012-01-01T00:00:00",
                delt="PT30M",
                tfmt=1,
                dfmt="min",
                suffix="",
            )
        )
        print(write.render())

    """

    model_type: Literal["write", "WRITE"] = Field(
        default="write",
        description="Model type discriminator",
    )
    sname: str = Field(
        description=(
            "Name of the set of output locations in which the output is to be written"
        ),
        max_length=8,
    )
    fname: str = Field(
        description=(
            "Name of the data file where the output is written to The file format is "
            "defined by the file extension, use `.mat` for MATLAB binary (single "
            "precision) or `.nc` for netCDF format. If any other extension is used "
            "the ASCII format is assumed"
        ),
    )
    times: Optional[TimeRangeOpen] = Field(
        default=None,
        description=(
            "Time specification if the user requires output at various times. If this "
            "option is not specified data will be written for the last time step of "
            "the computation"
        ),
    )

    @model_validator(mode="after")
    def validate_special_names(self) -> "BaseWrite":
        special_names = ("COMPGRID", "BOTTGRID")
        snames = self.sname if isinstance(self.sname, list) else [self.sname]
        for sname in snames:
            if sname in special_names and self.model_type.upper() != "BLOCK":
                raise ValueError(f"Special name {sname} is only supported with BLOCK")
        return self

    @model_validator(mode="after")
    def validate_times(self) -> "BaseWrite":
        if self.times is not None:
            self.times.suffix = self.suffix
        return self

    @property
    def suffix(self) -> str:
        return ""

    def cmd(self) -> str:
        """Command file string for this component."""
        return ""
