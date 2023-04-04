from __future__ import annotations

import os
from datetime import datetime
from typing import List

from pydantic import BaseModel, PrivateAttr, validator

from rompy import TEMPLATES_DIR
from rompy.templates.base.model import Template as BaseTemplate
from rompy.types import Coordinate


class OutputLocs(BaseModel):
    coords: List[Coordinate] = [["115.61", "-32.618"], ["115.686067", "-32.532381"]]


class Template(BaseTemplate):
    template: str = os.path.join(TEMPLATES_DIR, "swan")
    out_start: datetime = datetime(2020, 2, 21, 4)
    out_intvl: str = "1.0 HR"
    output_locs: OutputLocs = OutputLocs()
    cgrid: str = "REG 115.68 -32.76 77 0.39 0.15 389 149"
    cgrid_read: str = ""
    wind_grid: str = "REG 115.3 -32.8 0.0 2 3 0.3515625 0.234375  NONSTATION 20200221.040000  10800.0 S"
    wind_read: str = "SERIES 'extracted.wind' 1 FORMAT '(3F8.1)'"
    bottom_grid: str = "REG 115.68 -32.76 77 390 150 0.001 0.001 EXC -99.0"
    bottom_file: str = "bathy.bot"
    friction: str = "MAD"
    friction_coeff: str = "0.1"
    spectra_file: str = "boundary.spec"

    @validator("out_start", "out_intvl", pre=True)
    def validate_out_start_intvl(cls, v):
        return cls.validate_compute_start_stop(v)

    @validator("friction")
    def validate_friction(cls, v):
        if v not in ["MAD", "MANN", "FRICTION"]:
            raise ValueError(
                "friction must be one of MAD, MANN, FRICTION"
            )  # TODO Raf to add actual friction options
        return v

    @validator("friction_coeff")
    def validate_friction_coeff(cls, v):
        # TODO Raf to add sensible friction coeff range
        if float(v) > 1:
            raise ValueError("friction_coeff must be less than 1")
        if float(v) < 0:
            raise ValueError("friction_coeff must be greater than 0")
        return v
