from rompy.core import DataGrid

from .grid import SwanGrid


class SwanDataGrid(DataGrid):
    """This class is used to write SWAN data from a dataset.

    parameters
    ----------

    """

    def stage(self, staging_dir: str, grid: SwanGrid = None):
        inpwind, readwind = self.ds.swan.to_inpgrid(
            dest_path=os.path.join(staging_dir, f"{self.type}.nc"),
            var="WIND",
            grid=grid,
            z1="u10",
            z2="v10",
        )
        return inpwind, readwind
