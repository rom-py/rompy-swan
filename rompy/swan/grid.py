from typing import Optional

import numpy as np
from pydantic import root_validator, validator

from rompy.core.grid import RegularGrid


class SwanGrid(RegularGrid):
    gridtype: Optional[str] = "REG"
    exc: Optional[float] = None
    gridfile: Optional[str] = None

    @validator("gridtype")
    def validate_gridtype(cls, v):
        if v not in ["REG", "CURV"]:
            raise ValueError("gridtype must be one of REG or CURV")
        return v

    @root_validator
    def validate_grid(cls, values):
        gridtype = values["gridtype"]
        x = values["x"]
        y = values["y"]
        x0 = values["x0"]
        y0 = values["y0"]
        dx = values["dx"]
        dy = values["dy"]
        nx = values["nx"]
        ny = values["ny"]
        gridfile = values["gridfile"]

        if gridtype == "REG":
            # test if x is numpy array or None
            if isinstance(x, np.ndarray) or isinstance(y, np.ndarray):
                if any([x0, y0, dx, dy, nx, ny]):
                    raise ValueError(
                        "x, y provided explicitly, cant process x0, y0, dx, dy, nx, ny"
                    )
                return values
            for var in [x0, y0, dx, dy, nx, ny]:
                if var is None:
                    raise ValueError(
                        "x0, y0, dx, dy, nx, ny must be provided for REG grid"
                    )
        elif gridtype == "CURV":
            if not gridfile:
                raise ValueError("gridfile must be provided for CURV grid")
        else:
            raise ValueError("Unknown SwanGrid type = " + str(gridtype))
        return values

    def _regen_grid(self):
        if self.gridtype == "REG":
            _x, _y = self._gen_reg_cgrid()
        elif self.gridtype == "CURV":
            _x, _y = self._gen_curv_cgrid()
        self.x = _x
        self.y = _y

    def _gen_curv_cgrid(self):
        """loads a SWAN curvilinear grid and returns cgrid lat/lons and
        command to be used in SWAN contol file. The Default grid is one I made using
        Deltares' RGFGrid tool and converted to a SWAN-friendly formate using Deltares
        OpenEarth code "swan_io_grd.m"

        """
        # number of grid cells in the 'x' and 'y' directions:
        # (you can get this from d3d_qp.m or other Deltares OpenEarth code)
        nX = self.nx
        nY = self.ny

        grid_Data = open(self.gridpath).readlines()
        ix = grid_Data.index("x-coordinates\n")
        iy = grid_Data.index("y-coordinates\n")
        lons = []
        lats = []
        for idx in np.arange(ix + 1, iy):
            lons.append(re.sub("\n", "", grid_Data[idx]).split())
        for idx in np.arange(iy + 1, len(grid_Data)):
            lats.append(re.sub("\n", "", grid_Data[idx]).split())
        flatten = lambda l: [item for sublist in l for item in sublist]
        lons = np.array(flatten(lons)).astype(np.float)
        lats = np.array(flatten(lats)).astype(np.float)

        x = np.reshape(lats, (nX, nY))
        y = np.reshape(lons, (nX, nY))

        return x, y

    # # The folling properties and setters are necessary
    # # to ensure the grid is regnerated when any one of them changes
    # TODO this needs ot be ported to a framework that works with pydantic
    # @property
    # def x0(self):
    #     return self._x0
    #
    # @x0.setter
    # def x0(self, x0):
    #     self._x0 = x0
    #     self._regen_grid()
    #
    # @property
    # def y0(self):
    #     return self._y0
    #
    # @y0.setter
    # def y0(self, y0):
    #     self._y0 = y0
    #     self._regen_grid()
    #
    # @property
    # def rot(self):
    #     return self._rot
    #
    # @rot.setter
    # def rot(self, rot):
    #     self._rot = rot
    #     self._regen_grid()
    #
    # @property
    # def dx(self):
    #     return self._dx
    #
    # @dx.setter
    # def dx(self, dx):
    #     self._dx = dx
    #     self._regen_grid()
    #
    # @property
    # def dy(self):
    #     return self._dy
    #
    # @dy.setter
    # def dy(self, dy):
    #     self._dy = dy
    #     self._regen_grid()
    #
    # @property
    # def nx(self):
    #     return self._nx
    #
    # @nx.setter
    # def nx(self, nx):
    #     self._nx = nx
    #     self._regen_grid()
    #
    # @property
    # def ny(self):
    #     return self._ny
    #
    # @ny.setter
    # def ny(self, ny):
    #     self._ny = ny
    #     self._regen_grid()
    #
    # @property
    # def exc(self):
    #     return self._exc
    #
    # @exc.setter
    # def exc(self, exc):
    #     self._exc = exc
    #
    @property
    def inpgrid(self):
        if self.gridtype == "REG":
            inpstr = f"REG {self.x0} {self.y0} {self.rot} {self.nx-1:0.0f} {self.ny-1:0.0f} {self.dx} {self.dy}"
            if self.exc is not None:
                inpstr += f" EXC {self.exc}"
            return inpstr
        elif self.gridtype == "CURV":
            raise NotImplementedError("Curvilinear grids not supported yet")
            # return f'CURVilinear {self.nx-1:0.0f} {self.ny-1:0.0f} \nREADGRID COOR 1 \'{os.path.basename(self.gridpath)}\' 1 0 1 FREE'

    @property
    def cgrid(self):
        if self.gridtype == "REG":
            return f"REG {self.x0} {self.y0} {self.rot} {self.dx*self.nx} {self.dy*self.ny} {self.nx-1:0.0f} {self.ny-1:0.0f}"
        elif self.gridtype == "CURV":
            raise NotImplementedError("Curvilinear grids not supported yet")
            # return (f'CURVilinear {self.nx-1:0.0f} {self.ny-1:0.0f}',f'READGRID COOR 1 \'{os.path.basename(self.gridpath)}\' 1 0 1 FREE')

    @property
    def cgrid_read(self):
        if self.gridtype == "REG":
            return ""
        elif self.gridtype == "CURV":
            raise NotImplementedError("Curvilinear grids not supported yet")

    def nearby_spectra(self, ds_spec, dist_thres=0.05, plot=True):
        """Find points nearby and project to the boundary

        Parameters
        ----------
        ds_spec: xarray.Dataset
            an XArray dataset of wave spectra at a number of points.
            Dataset variable names standardised using wavespectra.read_*
            functions.

            See https://wavespectra.readthedocs.io/en/latest/api.html#input-functions
        dist_thres: float, optional [Default: 0.05]
            Maximum distance to translate the input spectra to the grid boundary
        plot: boolean, optional [Default: True]
            Generate a plot that shows the applied projections

        Returns
        -------
        xarray.Dataset
            A subset of ds_spec with lat and lon coordinates projected to the boundary
        """

        bbox = self.bbox(buffer=dist_thres)
        minLon, minLat, maxLon, maxLat = bbox

        inds = np.where(
            (ds_spec.lon > minLon)
            & (ds_spec.lon < maxLon)
            & (ds_spec.lat > minLat)
            & (ds_spec.lat < maxLat)
        )[0]
        ds_spec = ds_spec.isel(site=inds)

        # Work out the closest spectral points
        def _nearestPointOnLine(p1, p2, p3):
            # calculate the distance of p3 from the line between p1 and p2 and return
            # the closest point on the line

            from math import fabs, sqrt

            a = p2[1] - p1[1]
            b = -1.0 * (p2[0] - p1[0])
            c = p2[0] * p1[1] - p2[1] * p1[0]

            dist = fabs(a * p3[0] + b * p3[1] + c) / sqrt(a**2 + b**2)
            x = (b * (b * p3[0] - a * p3[1]) - a * c) / (a**2 + b**2)
            y = (a * (-b * p3[0] + a * p3[1]) - b * c) / (a**2 + b**2)

            return dist, x, y

        bx, by = self.boundary_points()
        pol = np.stack([bx, by])

        # Spectra points
        ds_spec.lon.load()
        ds_spec.lat.load()
        ds_spec["lon_original"] = ds_spec["lon"]
        ds_spec["lat_original"] = ds_spec["lat"]
        p3s = list(zip(ds_spec.lon.values, ds_spec.lat.values))

        if plot:
            fig, ax = self.plot()
            ax.scatter(ds_spec.lon, ds_spec.lat)

        specPoints = []
        specPointCoords = []
        for i in range(pol.shape[1] - 1):
            p1 = pol[:, i]
            p2 = pol[:, i + 1]
            line = np.stack((p1, p2))
            output = np.array(
                list(map(lambda xi: _nearestPointOnLine(p1, p2, xi), p3s))
            )
            dists = output[:, 0]
            segmentPoints = output[:, 1:]
            inds = np.where((dists < dist_thres))[0]

            # Loop through the points projected onto the line
            for ind in inds:
                specPoint = ds_spec.isel(site=ind)

                segLon = segmentPoints[ind, 0]
                segLat = segmentPoints[ind, 1]

                if plot:
                    ax.plot(
                        [segLon, specPoint.lon],
                        [segLat, specPoint.lat],
                        color="r",
                        lw=2,
                    )
                    ax.scatter(specPoint.lon, specPoint.lat, marker="o", color="b")
                    ax.scatter(segLon, segLat, marker="x", color="g")

                specPoint["lon"] = segLon
                specPoint["lat"] = segLat
                specPoints.append(specPoint)

            logger.debug(f"Segment {i} - Indices {inds}")

        if plot:
            fig.show()

        ds_boundary = xr.concat(specPoints, dim="site")
        return ds_boundary

    def __repr__(self):
        return f"SwanGrid: {self.gridtype}, {self.nx}x{self.ny}"
