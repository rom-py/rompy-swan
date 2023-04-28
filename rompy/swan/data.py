import logging
import os

from pydantic import root_validator

from rompy.core import DataGrid

from .grid import SwanGrid

logger = logging.getLogger(__name__)


class SwanDataGrid(DataGrid):
    """This class is used to write SWAN data from a dataset.

    Parameters
    ----------
    path: str
            Optional local file path
    url: str
            Optional remote file url
    catalog: str
            Optional intake catalog
    dataset: str
            Optional intake dataset id
    params: dict
            Optional parameters to pass to the intake catalog
    filter: Filter
            Optional filter specification to apply to the dataset
    xarray_kwargs: dict
            Optional keyword arguments to pass to xarray.open_dataset
    netcdf_kwargs: dict
            Optional keyword arguments to pass to xarray.Dataset.to_netcdf
    var: str
            Variable name to write


    """

    z1: str
    z2: str = None
    var: str = "WIND"

    # root validator
    @root_validator
    def ensure_z1_in_data_vars(cls, values):
        params = values.get("params")
        data_vars = params.get("data_vars", [])
        for z in [values.get("z1"), values.get("z2")]:
            if z and z not in data_vars:
                logger.debug(f"Adding {z} to data_vars")
                data_vars.append(z)
        values["params"]["data_vars"] = data_vars
        return values

    def get(self, staging_dir: str, grid: SwanGrid = None):
        inpwind, readwind = self.ds.swan.to_inpgrid(
            output_file=os.path.join(staging_dir, f"{self.id}.grd"),
            z1=self.z1,
            z2=self.z2,
            grid=grid,
            var=self.var,
        )
        return inpwind, readwind
