=======
History
=======

Wavespectra is an open source project that was started at MetOcean Solutions and open
sourced in April 2018. In July 2019 it was moved into the wavespectra github open
source organisation and transitioned into a fully community developed project. This
changelog covers the release history since v3.0 when wavespectra was open-sourced.


********
Releases
********

3.14.0 (2023-07-03)
___________________

Internal Changes
----------------
* Redefine packaging via pyproject.toml to conform to PEP517/518 (`PR77 <https://github.com/wavespectra/wavespectra/pull/87>`_).
* All packaging metadata removed from setup.py and moved to pyproject.toml. The
  setup.py file is now only used to build the Fortran module.
* Removed the MANIFEST.in file, package data now handled in pyproject.toml.
* Removed the requirements folder, requirements now handled in pyproject.toml.
* Removed some packaging attributes from wavespectra.__init__.py, now handled in
  pyproject.toml.
* New docs theme: sphinx_rtd_theme by pydata_sphinx_theme, fixes issue with rtd not working with sphinx>=7.0.
* Add readthedocs config.


3.13.0 (2023-01-09)
___________________

New Features
------------
* Support for CSV Spotter files in `read_spotter`_ by by `ryancoe`_  (`PR77 <https://github.com/wavespectra/wavespectra/pull/77>`_).
* New reader `read_ndbc` for NDBC netcdf datasets (`PR80 <https://github.com/wavespectra/wavespectra/pull/80>`_).

Bug Fixes
---------
* Fix bug in 2D spectra construction in `read_ndbc_ascii`_ due to wrong scaling (`GH70 <https://github.com/wavespectra/wavespectra/issues/70>`_).
* Ensure directions are continuous when reading from Funwave file with split directions.

Internal Changes
----------------
* New github action to test and publish package on new releases.

Deprecation
-----------
* Replace previous NDBC ASCII reader `read_ndbc` by `read_ndbc_ascii`.

.. _`ryancoe`: https://github.com/ryancoe
.. _`read_spotter`: https://github.com/wavespectra/wavespectra/blob/master/wavespectra/input/spotter.py
.. _`read_ndbc_ascii`: https://github.com/wavespectra/wavespectra/blob/master/wavespectra/input/ndbc_ascii.py





.. _`CSIRO`: https://www.csiro.au/en/
