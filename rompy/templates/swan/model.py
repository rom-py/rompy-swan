from __future__ import annotations

from typing import List

from pydantic import BaseModel, PrivateAttr

from rompy.templates.base.model import Template as BaseTemplate


class OutputLocs(BaseModel):
    coords: List[List[str]] = [["115.61", "-32.618"], ["115.686067", "-32.532381"]]


class Template(BaseTemplate):
    out_start: str = "20200221.040000"
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
