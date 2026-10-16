# Numerics

Two commands set SWAN's numerical methods: `PROP` chooses the propagation scheme in geographic space, and `NUMERIC` sets when the iterations of a computation stop and how the implicit schemes in direction and frequency space behave. They are the [`prop`][rompy_swan.config.SwanConfig.prop] and [`numeric`][rompy_swan.config.SwanConfig.numeric] fields of [`SwanConfig`][rompy_swan.config.SwanConfig], written after the physics. SWAN's defaults suit most models; this page explains the options and when to change them. The time step of a nonstationary run is not set here but by the run period (see [below](#the-time-step-of-nonstationary-runs)).

## Propagation scheme: PROP

Without `PROP`, or with `PROP()` and no scheme, SWAN chooses the scheme from the mode and the grid:

| Computation | SWAN's scheme |
|---|---|
| Stationary, regular or curvilinear grid | SORDUP, second-order upwind |
| Nonstationary, regular or curvilinear grid | S&L, third-order Stelling and Leendertse |
| Unstructured grid | first-order upwind |

[`PROP`][rompy_swan.components.numerics.PROP] changes it with its [`scheme`][rompy_swan.components.numerics.PROP.scheme]:

- [`BSBT`][rompy_swan.subcomponents.numerics.BSBT]: the first-order upwind scheme. It is robust and unconditionally stable but more diffusive. Use it with large nonstationary time steps (Courant numbers above 10), with grids that change resolution abruptly (the higher-order schemes lose accuracy on curvilinear grids that do not vary gradually), or when SWAN advises it in `PRINT`.
- [`GSE`][rompy_swan.subcomponents.numerics.GSE]: the S&L scheme with added diffusion against the garden-sprinkler effect, the break-up of swell into separate rays over long distances. Its [`waveage`][rompy_swan.subcomponents.numerics.GSE.waveage], a [`Delt`][rompy_swan.subcomponents.time.Delt], should match the travel time of the waves across the domain.

```python exec="on" source="above" result="text" session="numerics"
from datetime import timedelta

from rompy_swan.components.numerics import PROP
from rompy_swan.subcomponents.numerics import BSBT, GSE
from rompy_swan.subcomponents.time import Delt

print(PROP().render())
print(PROP(scheme=BSBT()).render())
print(PROP(scheme=GSE(waveage=Delt(delt=timedelta(hours=12), dfmt="hr"))).render())
```

The added diffusion makes the S&L scheme conditionally stable. If a run with `GSE` becomes unstable, the SWAN manual suggests, in order: a smaller time step, a lower `waveage`, a finer directional resolution, or a coarser geographic resolution. On unstructured grids the first-order scheme already damps the garden-sprinkler effect.

## When to stop iterating: NUMERIC STOPC

SWAN solves each stationary computation, and each nonstationary time step, iteratively. The [`stop`][rompy_swan.components.numerics.NUMERIC.stop] field of [`NUMERIC`][rompy_swan.components.numerics.NUMERIC] sets the stopping criterion. [`STOPC`][rompy_swan.subcomponents.numerics.STOPC], SWAN's default criterion (Zijlema and Van der Westhuysen, 2005), stops when, in more than `npnts` percent of the wet grid points, the change in Hs from one iteration to the next is small and the iteration curve of Hs has flattened:

| Field | Meaning | SWAN default |
|---|---|---|
| `dabs` | maximum absolute change in Hs (m) | 0.005 (0.05 with the QC model of `SCAT`) |
| `drel` | maximum relative change in Hs | 0.01 |
| `curvat` | maximum curvature of the iteration curve of Hs, normalised with Hs | 0.005 |
| `npnts` | percentage of wet points that must meet the criteria | 99.5 |
| `mode` | maximum number of iterations: [`STAT`][rompy_swan.subcomponents.numerics.STAT] or [`NONSTAT`][rompy_swan.subcomponents.numerics.NONSTAT] | see below |
| `limiter` | the action limiter: the maximum change per iteration of the energy density in a spectral bin, as a fraction of the Phillips level | 0.1 |

The `mode` sets the iterations for the kind of computation:

- `STAT(mxitst=...)` for stationary computations (`COMPUTE`, `COMPUTE_STAT`): at most `mxitst` iterations, SWAN default 50. Its `alfa` adds frequency-dependent under-relaxation, recommended with diffraction (`alfa=0.01`).
- `NONSTAT(mxitns=...)` for the time steps of `COMPUTE_NONSTAT`: at most `mxitns` iterations per step, SWAN default 1. One iteration per step is enough with steps of 10 minutes or less; more help with longer steps.

```python exec="on" source="above" result="text" session="numerics"
from rompy_swan.components.numerics import NUMERIC
from rompy_swan.subcomponents.numerics import NONSTAT, STAT, STOPC

print(NUMERIC().render())
print(NUMERIC(stop=STOPC(dabs=0.005, drel=0.01, curvat=0.005, npnts=99.5, mode=STAT(mxitst=50))).render())
print(NUMERIC(stop=STOPC(npnts=99.5, mode=NONSTAT(mxitns=3))).render())
```

Raise `mxitst` or lower `npnts` when a stationary computation stops before converging (`PRINT` reports the accuracy reached at each iteration); tighten `dabs`, `drel` and `curvat` for sensitivity studies, where small differences between runs matter.

[`ACCUR`][rompy_swan.subcomponents.numerics.ACCUR] is the older criterion on changes in Hs and Tm01 (`drel`, `dhoval`, `dtoval`, `npnts`), obsolete since SWAN 41.01 and kept for old configurations. A maximum of zero iterations, `STAT(mxitst=0)`, is a quick way to check that SWAN reads every input without computing:

```python exec="on" source="above" result="text" session="numerics"
from rompy_swan.subcomponents.numerics import ACCUR

print(NUMERIC(stop=ACCUR(drel=0.02, dhoval=0.02, dtoval=0.02, npnts=98.0, mode=STAT(mxitst=0))).render())
```

## Refraction and frequency shifting: DIRIMPL, SIGIMPL, CTHETA, CSIGMA

These options tune the implicit schemes for refraction (propagation in direction) and frequency shifting (propagation in frequency, with currents or time-varying depth). They rarely need changing.

| Field | Component | What it sets | SWAN default |
|---|---|---|---|
| `dirimpl` | [`DIRIMPL`][rompy_swan.subcomponents.numerics.DIRIMPL] | `cdd`: 0 is a central scheme (most accurate, may oscillate), 1 a first-order upwind scheme (diffusive, better with strong depth or current gradients) | 0.5 |
| `sigimpl` | [`SIGIMPL`][rompy_swan.subcomponents.numerics.SIGIMPL] | `css`, the same choice for frequency shifting, and the SIP solver's stopping criterion `eps2`, output `outp` and iterations `niter` | `css=0.5` |
| `ctheta` | [`CTHETA`][rompy_swan.subcomponents.numerics.CTHETA] | limits the directional turning rate with a CFL criterion `cfl` | not active; 0.9 when given |
| `csigma` | [`CSIGMA`][rompy_swan.subcomponents.numerics.CSIGMA] | limits the frequency-shifting rate with a CFL criterion `cfl` | not active; 0.9 when given |

`CTHETA` and `CSIGMA` help where a coarse bathymetry or current turns the waves or shifts their frequency excessively at single grid points, for example at steep shelf edges. Use `cdd=1` or `css=1` when strong gradients cause wiggles in the results.

```python exec="on" source="above" result="text" session="numerics"
from rompy_swan.subcomponents.numerics import CSIGMA, CTHETA, DIRIMPL, SIGIMPL

numeric = NUMERIC(
    dirimpl=DIRIMPL(cdd=1.0),
    sigimpl=SIGIMPL(css=0.5),
    ctheta=CTHETA(cfl=0.9),
    csigma=CSIGMA(cfl=0.9),
)
print(numeric.render())
```

## The set-up solver: NUMERIC SETUP

With wave-induced set-up (the `SETUP` physics command), SWAN solves an extra equation for the set-up. The `setup` field of `NUMERIC`, a [`SETUP`][rompy_swan.subcomponents.numerics.SETUP] from `rompy_swan.subcomponents.numerics` (not the physics `SETUP`), sets the solver's stopping criterion `eps2`, its output to `PRINT` (`outp`, 0 to 3) and its maximum iterations `niter`:

```python exec="on" source="above" result="text" session="numerics"
from rompy_swan.subcomponents.numerics import SETUP

print(NUMERIC(stop=STOPC(mode=STAT(mxitst=50)), setup=SETUP(eps2=1e-6, outp=0, niter=1000)).render())
```

## The time step of nonstationary runs

In nonstationary mode, the computational time step `deltc` of `COMPUTE NONSTATIONARY` is the `interval` of the run period, a [`TimeRange`][rompy.core.time.TimeRange]; see [Stationary and nonstationary runs](modes.md). The SWAN manual advises steps of at most 10 minutes, and a Courant number (the number of cells the fastest waves cross in one step) below 10 with the higher-order S&L scheme. Above that SWAN stops with an error in `PRINT`; shorten the step or use `PROP BSBT`.

The fastest waves are the longest swell, with a deep-water group velocity of g T / (4π). For the longest period of the spectral grid (1 / `flow`):

```python exec="on" source="above" result="text" session="numerics"
import numpy as np


def courant(flow: float, dx_degrees: float, latitude: float, step: timedelta) -> float:
    """Courant number of the longest swell on a spherical grid."""
    group_velocity = 9.81 * (1 / flow) / (4 * np.pi)  # m/s
    dx = dx_degrees * 111_000 * np.cos(np.deg2rad(latitude))  # m, east-west cell size
    return group_velocity * step.total_seconds() / dx


for dx in [0.5, 0.02]:
    for minutes in [10, 30, 60]:
        value = courant(flow=0.04, dx_degrees=dx, latitude=-32.0, step=timedelta(minutes=minutes))
        print(f"dx={dx}°, {minutes:2d} min: Courant number {value:5.1f}")
```

On a coarse regional grid a step of an hour is fine; on a 2 km coastal grid, 10 minutes is close to the limit. For small domains, a series of stationary computations (`COMPUTE_STAT` in nonstationary mode) is an alternative to many short steps.

## When to change the defaults

| Symptom | Setting to try |
|---|---|
| Nonstationary run stops with a CFL error | shorter run interval, or `PROP(scheme=BSBT())` |
| Swell breaks into rays far from its source | `PROP(scheme=GSE(waveage=...))` |
| Stationary computation does not converge | higher `STAT(mxitst=...)`, lower `npnts`; with diffraction `alfa=0.01` |
| Wiggles near steep bathymetry or strong currents | `DIRIMPL(cdd=1.0)`, `SIGIMPL(css=1.0)`, `CTHETA`, `CSIGMA` |
| Sensitivity runs differ by less than the convergence tolerance | tighter `dabs`, `drel`, `curvat` |

## In YAML

```python exec="on" source="above" result="text" session="numerics"
import yaml

config = yaml.safe_load(
    """
    prop:
      scheme:
        model_type: bsbt
    numeric:
      stop:
        model_type: stopc
        npnts: 99.5
        mode:
          model_type: nonstat
          mxitns: 3
      dirimpl:
        cdd: 1.0
    """
)
prop = PROP.model_validate(config["prop"])
numeric = NUMERIC.model_validate(config["numeric"])
print(prop.render())
print(numeric.render())
```

```python exec="on"
from rompy_docs.notebooks import see_also

print(see_also("swan", ["numerics", "components"]))
```
