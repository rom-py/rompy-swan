# Physics

The physics commands set the source terms of SWAN's action balance equation: wind input, whitecapping, wave-wave interactions, depth-induced breaking, bottom friction and the processes needed in special cases, such as obstacles, vegetation or sea ice. In rompy-swan each command is a component named after it (`GEN3`, `BREAKING`, `FRICTION`, ...), and the [`PHYSICS`][rompy_swan.components.group.PHYSICS] group, the `physics` field of [`SwanConfig`][rompy_swan.config.SwanConfig], writes them in the order SWAN expects. Commands that are not set are not written, and SWAN then uses its default for that process.

## The PHYSICS group

Each field of [`PHYSICS`][rompy_swan.components.group.PHYSICS] takes one command, or one of its variants, and the group writes them in this order:

| Field | Components | SWAN command |
|---|---|---|
| `gen` | [`GEN1`][rompy_swan.components.physics.GEN1], [`GEN2`][rompy_swan.components.physics.GEN2], [`GEN3`][rompy_swan.components.physics.GEN3] | `GEN1`, `GEN2`, `GEN3` |
| `sswell` | [`SSWELL_ROGERS`][rompy_swan.components.physics.SSWELL_ROGERS], [`SSWELL_ARDHUIN`][rompy_swan.components.physics.SSWELL_ARDHUIN], [`SSWELL_ZIEGER`][rompy_swan.components.physics.SSWELL_ZIEGER] | `SSWELL` |
| `negatinp` | [`NEGATINP`][rompy_swan.components.physics.NEGATINP] | `NEGATINP` |
| `wcapping` | [`WCAPPING_KOMEN`][rompy_swan.components.physics.WCAPPING_KOMEN], [`WCAPPING_AB`][rompy_swan.components.physics.WCAPPING_AB] | `WCAPPING` |
| `quadrupl` | [`QUADRUPL`][rompy_swan.components.physics.QUADRUPL] | `QUADRUPL` |
| `breaking` | [`BREAKING_CONSTANT`][rompy_swan.components.physics.BREAKING_CONSTANT], [`BREAKING_BKD`][rompy_swan.components.physics.BREAKING_BKD] | `BREAKING` |
| `friction` | [`FRICTION_JONSWAP`][rompy_swan.components.physics.FRICTION_JONSWAP], [`FRICTION_COLLINS`][rompy_swan.components.physics.FRICTION_COLLINS], [`FRICTION_MADSEN`][rompy_swan.components.physics.FRICTION_MADSEN], [`FRICTION_RIPPLES`][rompy_swan.components.physics.FRICTION_RIPPLES] | `FRICTION` |
| `triad` | [`TRIAD`][rompy_swan.components.physics.TRIAD], [`TRIAD_DCTA`][rompy_swan.components.physics.TRIAD_DCTA], [`TRIAD_LTA`][rompy_swan.components.physics.TRIAD_LTA], [`TRIAD_SPB`][rompy_swan.components.physics.TRIAD_SPB] | `TRIAD` |
| `vegetation` | [`VEGETATION`][rompy_swan.components.physics.VEGETATION] | `VEGETATION` |
| `mud` | [`MUD`][rompy_swan.components.physics.MUD] | `MUD` |
| `sice` | [`SICE`][rompy_swan.components.physics.SICE], [`SICE_R19`][rompy_swan.components.physics.SICE_R19], [`SICE_D15`][rompy_swan.components.physics.SICE_D15], [`SICE_M18`][rompy_swan.components.physics.SICE_M18], [`SICE_R21B`][rompy_swan.components.physics.SICE_R21B] | `SICE` |
| `turbulence` | [`TURBULENCE`][rompy_swan.components.physics.TURBULENCE] | `TURBULENCE` |
| `bragg` | [`BRAGG`][rompy_swan.components.physics.BRAGG], [`BRAGG_FT`][rompy_swan.components.physics.BRAGG_FT], [`BRAGG_FILE`][rompy_swan.components.physics.BRAGG_FILE] | `BRAGG` |
| `limiter` | [`LIMITER`][rompy_swan.components.physics.LIMITER] | `LIMITER` |
| `obstacle` | [`OBSTACLES`][rompy_swan.components.physics.OBSTACLES] | one `OBSTACLE` per obstacle |
| `setup` | [`SETUP`][rompy_swan.components.physics.SETUP] | `SETUP` |
| `diffraction` | [`DIFFRACTION`][rompy_swan.components.physics.DIFFRACTION] | `DIFFRACTION` |
| `surfbeat` | [`SURFBEAT`][rompy_swan.components.physics.SURFBEAT] | `SURFBEAT` |
| `scat` | [`SCAT`][rompy_swan.components.physics.SCAT] | `SCAT` |
| `deactivate` | [`OFFS`][rompy_swan.components.physics.OFFS] | one `OFF` per process |

A typical coastal model sets the generation, breaking, friction and triads:

```python exec="on" source="above" result="text" session="physics"
from rompy_swan.components.group import PHYSICS
from rompy_swan.components.physics import BREAKING_CONSTANT, FRICTION_JONSWAP, GEN3, TRIAD

physics = PHYSICS(
    gen=GEN3(),
    breaking=BREAKING_CONSTANT(alpha=1.0, gamma=0.73),
    friction=FRICTION_JONSWAP(cfjon=0.038),
    triad=TRIAD(),
)
print(physics.render())
```

### What SWAN does without a command

| Process | Without a command | Switch on or change with |
|---|---|---|
| Wind input and whitecapping | third-generation, WESTHUYSEN since SWAN 41.45 (KOMEN before) | `GEN3(source_terms=...)`, `WCAPPING_*` |
| Quadruplets | on with third-generation physics | `QUADRUPL`; off with `OFF QUADRUPL` |
| Depth-induced breaking | on, constant breaker index (`alpha=1.0`, `gamma=0.73`) | `BREAKING_CONSTANT`, `BREAKING_BKD`; off with `OFF BREAKING` |
| Bottom friction | **off** | `FRICTION_*` |
| Triads | **off** | `TRIAD`, `TRIAD_DCTA`, `TRIAD_LTA`, `TRIAD_SPB` |
| Set-up, diffraction, vegetation, mud, sea ice, obstacles, ... | off | their components |

Friction and triads matter in shallow water, so coastal models usually switch them on. Writing the defaults you rely on, as above, also keeps the command file readable and independent of the SWAN version.

## Wave generation: GEN1, GEN2 and GEN3

[`GEN3`][rompy_swan.components.physics.GEN3] runs SWAN in third-generation mode. Its [`source_terms`][rompy_swan.components.physics.GEN3.source_terms] choose the package of wind input and whitecapping formulations, and default to SWAN's default, WESTHUYSEN, which rompy-swan writes explicitly:

| Package | Formulations | Own options |
|---|---|---|
| [`WESTHUYSEN`][rompy_swan.subcomponents.physics.WESTHUYSEN] | Yan (1987) wind input, saturation-based whitecapping (Van der Westhuysen et al., 2007) | `cds2`, `br` |
| [`KOMEN`][rompy_swan.subcomponents.physics.KOMEN] | WAM cycle 3 (Komen et al., 1984) | `cds2`, `stpm` |
| [`JANSSEN`][rompy_swan.subcomponents.physics.JANSSEN] | WAM cycle 4 (Janssen, 1991) | `cds1`, `delta` |
| [`ST6`][rompy_swan.subcomponents.physics.ST6] | Rogers et al. (2012) wind input and whitecapping | `a1sds`, `a2sds` (required), `p1sds`, `p2sds`, ... |
| [`ST6C1`][rompy_swan.subcomponents.physics.ST6C1] to [`ST6C5`][rompy_swan.subcomponents.physics.ST6C5] | ST6 with the calibrations listed in the SWAN manual | none |

```python exec="on" source="above" result="text" session="physics"
from rompy_swan.subcomponents.physics import JANSSEN, KOMEN, ST6C1, WESTHUYSEN

for terms in [WESTHUYSEN(), KOMEN(), JANSSEN(), ST6C1()]:
    print(GEN3(source_terms=terms).render())
```

All packages take `agrow=True`, which adds the linear wave growth term of Cavaleri and Malanotte-Rizzoli (1981) with coefficient `a` (SWAN default 0.0015). It helps waves grow from calm seas; the ST6 calibrations switch it on.

```python exec="on" source="above" result="text" session="physics"
print(GEN3(source_terms=KOMEN(cds2=2.36e-5, agrow=True)).render())
```

ST6 is meant to be used with the non-breaking swell dissipation `SSWELL` (below), which the ST6 presets do not add:

```python exec="on" source="above" result="text" session="physics"
from rompy_swan.components.physics import SSWELL_ZIEGER

print(PHYSICS(gen=GEN3(source_terms=ST6C1()), sswell=SSWELL_ZIEGER()).render())
```

[`GEN1`][rompy_swan.components.physics.GEN1] and [`GEN2`][rompy_swan.components.physics.GEN2] select SWAN's first- and second-generation formulations, with their coefficients (`cf10`, `cf20`, ..., `cdrag`, `umin`). Without options they write the bare command, and SWAN uses its defaults:

```python exec="on" source="above" result="text" session="physics"
from rompy_swan.components.physics import GEN1, GEN2

print(GEN1().render())
print(GEN2(cf10=188.0, cdrag=0.0012).render())
```

### Wind drag and other settings

The wind drag formulation is part of the source terms: [`wind_drag`][rompy_swan.subcomponents.physics.WESTHUYSEN.wind_drag] is `"wu"` (Wu, 1982, SWAN's default, written as `DRAG WU`) or `"fit"` (Zijlema et al., 2012) for the WESTHUYSEN, KOMEN and JANSSEN packages. ST6 has its own formulations, `"hwang"` (default), `"fan"` and `"ecmwf"`, and a debias factor `cdfac` that SWAN only supports with `hwang`:

```python exec="on" source="above" result="text" session="physics"
from pydantic import ValidationError

from rompy_swan.subcomponents.physics import ST6

print(GEN3(source_terms=WESTHUYSEN(wind_drag="fit")).render())
try:
    ST6(a1sds=4.7e-7, a2sds=6.6e-6, wind_drag="fan", cdfac=0.89)
except ValidationError as err:
    print(err.errors()[0]["msg"])
```

Other settings that affect the physics belong to the [`SET`][rompy_swan.components.startup.SET] command, the `set` field of the startup group: the cap on the wind drag coefficient [`cdcap`][rompy_swan.components.startup.SET.cdcap], the scaling of wind input by the open-water fraction in sea ice [`icewind`][rompy_swan.components.startup.SET.icewind], the maximum Froude number of currents [`froudmax`][rompy_swan.components.startup.SET.froudmax], gravity and water density. SWAN takes winds at 10 m elevation; rompy-swan has no setting for another height, so convert the winds before using them as input.

```python exec="on" source="above" result="text" session="physics"
from rompy_swan.components.startup import SET

print(SET(cdcap=2.5e-3, direction_convention="nautical").render())
```

!!! note
    `SET` is written at the start of the command file, before `GEN3`, and the `GEN` commands reset the power of the spectral tail. A [`pwtail`][rompy_swan.components.startup.SET.pwtail] set in `SET` is therefore overridden, and rompy-swan logs a warning when it is given.

## Whitecapping and swell dissipation

Each `GEN3` package includes a whitecapping formulation. `WCAPPING` replaces it, and is mainly used to tune or combine formulations:

- [`WCAPPING_KOMEN`][rompy_swan.components.physics.WCAPPING_KOMEN]: pulse-based whitecapping of Komen et al. (1984), with `cds2` (SWAN default 2.36e-5), `stpm`, `powst`, `delta` (default 1 since SWAN 40.91A) and `powk`;
- [`WCAPPING_AB`][rompy_swan.components.physics.WCAPPING_AB]: saturation-based whitecapping of Alves and Banner (2003), with `cds2` and `br`, and with `current=True` the current-induced dissipation of Van der Westhuysen (2012), coefficient `cds3`.

The swell dissipation `SSWELL` damps non-breaking swell: [`SSWELL_ROGERS`][rompy_swan.components.physics.SSWELL_ROGERS], [`SSWELL_ARDHUIN`][rompy_swan.components.physics.SSWELL_ARDHUIN] or [`SSWELL_ZIEGER`][rompy_swan.components.physics.SSWELL_ZIEGER]. [`NEGATINP`][rompy_swan.components.physics.NEGATINP] adds negative wind input for waves running against the wind; it is meant for use with `SSWELL ZIEGER`, and the group logs a warning when it is used without it.

```python exec="on" source="above" result="text" session="physics"
from rompy_swan.components.physics import NEGATINP, WCAPPING_AB

print(WCAPPING_AB(cds2=5.0e-5, br=1.75e-3, current=True, cds3=0.8).render())
print(PHYSICS(sswell=SSWELL_ZIEGER(b1=0.00025), negatinp=NEGATINP(rdcoef=0.04)).render())
```

## Quadruplets: QUADRUPL

Four-wave interactions are on by default with `GEN3`, computed with the Discrete Interaction Approximation (DIA). [`QUADRUPL`][rompy_swan.components.physics.QUADRUPL] changes the numerical procedure [`iquad`][rompy_swan.components.physics.QUADRUPL.iquad] (SWAN default 2, explicit per sweep; 3 or 8 per iteration, advised with currents; 4 multiple DIA; 51 to 53 the exact XNL computation) and the DIA coefficients `lambd` (written as `lambda`), `cnl4` and the shallow-water scaling `csh1` to `csh3`:

```python exec="on" source="above" result="text" session="physics"
from rompy_swan.components.physics import QUADRUPL

print(QUADRUPL(iquad=3, lambd=0.25).render())
```

!!! warning "Quadruplets need wind"
    SWAN refuses to compute quadruplets when there is no wind: a model forced only by boundary swell stops with an error. Switch them off with `OFF QUADRUPL`, as in [Your first model](../getting-started/first-model.md):

    ```python exec="on" source="above" result="text" session="physics"
    from rompy_swan.components.physics import OFF, OFFS

    physics = PHYSICS(gen=GEN3(), deactivate=OFFS(offs=[OFF(physics="quadrupl")]))
    print(physics.render())
    ```

## Triads: TRIAD

Three-wave interactions move energy to higher frequencies (and to the infragravity band) in shallow water. They are off unless set.

| Component | Writes | Method |
|---|---|---|
| [`TRIAD`][rompy_swan.components.physics.TRIAD] | `TRIAD` | SWAN's default method (DCTA in SWAN 41.45 and later) |
| [`TRIAD_DCTA`][rompy_swan.components.physics.TRIAD_DCTA] | `TRIAD DCTA` | Distributed Collinear Triad Approximation (Booij et al., 2009), `trfac`, `p`, collinear or not (`noncolinear`) |
| [`TRIAD_LTA`][rompy_swan.components.physics.TRIAD_LTA] | `TRIAD LTA` | Lumped Triad Approximation (Eldeberky, 1996), `trfac`, `cutfr` |
| [`TRIAD_SPB`][rompy_swan.components.physics.TRIAD_SPB] | `TRIAD SPB` | Becq-Girard et al. (1999), `trfac`, `a`, `b` |

The DCTA, LTA and SPB methods take the parametrisation of the biphase, [`ELDEBERKY`][rompy_swan.subcomponents.physics.ELDEBERKY] (SWAN's default) or [`DEWIT`][rompy_swan.subcomponents.physics.DEWIT]:

```python exec="on" source="above" result="text" session="physics"
from rompy_swan.components.physics import TRIAD_DCTA, TRIAD_LTA
from rompy_swan.subcomponents.physics import DEWIT, ELDEBERKY

print(TRIAD().render())
print(TRIAD_DCTA(trfac=4.4, biphase=DEWIT(lpar=1.0)).render())
print(TRIAD_LTA(trfac=0.8, cutfr=2.5, biphase=ELDEBERKY(urcrit=0.63)).render())
```

The options of `TRIAD` itself (`itriad`, `trfac`, `cutfr`, `a`, `b`, `ucrit`, `urslim`) follow the syntax of SWAN before 41.45. With a current SWAN, set the method with one of the other three components.

## Depth-induced breaking: BREAKING

Breaking is on by default in SWAN, with a constant breaker index. The two variants:

- [`BREAKING_CONSTANT`][rompy_swan.components.physics.BREAKING_CONSTANT]: Battjes and Janssen (1978) with a constant breaker index `gamma` (SWAN default 0.73) and dissipation coefficient `alpha` (default 1.0);
- [`BREAKING_BKD`][rompy_swan.components.physics.BREAKING_BKD]: Salmon et al. (2015), with a breaker index that depends on the bottom slope and the dimensionless depth, `alpha`, `gamma0` (default 0.54) and `a1` to `a3`. It suits beaches and varying bathymetry better than a constant index.

```python exec="on" source="above" result="text" session="physics"
from rompy_swan.components.physics import BREAKING_BKD

print(BREAKING_CONSTANT().render())
print(BREAKING_CONSTANT(alpha=1.0, gamma=0.73).render())
print(BREAKING_BKD(alpha=1.0, gamma0=0.54, a1=7.59, a2=-8.06, a3=8.09).render())
```

## Bottom friction: FRICTION

Bottom friction is off unless set:

| Component | Writes | Formulation | Coefficient (SWAN default) |
|---|---|---|---|
| [`FRICTION_JONSWAP`][rompy_swan.components.physics.FRICTION_JONSWAP] | `FRICTION JONSWAP CONSTANT` | Empirical (Hasselmann et al., 1973) | `cfjon` (0.038 m²/s³) |
| [`FRICTION_COLLINS`][rompy_swan.components.physics.FRICTION_COLLINS] | `FRICTION COLLINS` | Drag law (Collins, 1972) | `cfw` (0.015) |
| [`FRICTION_MADSEN`][rompy_swan.components.physics.FRICTION_MADSEN] | `FRICTION MADSEN` | Eddy viscosity (Madsen et al., 1988) | roughness `kn` (0.05 m) |
| [`FRICTION_RIPPLES`][rompy_swan.components.physics.FRICTION_RIPPLES] | `FRICTION RIPPLES` | Ripple formation (Smith et al., 2011) | sediment specific gravity `s` (2.65) and diameter `d` (0.0001 m) |

```python exec="on" source="above" result="text" session="physics"
from rompy_swan.components.physics import FRICTION_COLLINS, FRICTION_MADSEN, FRICTION_RIPPLES

for friction in [
    FRICTION_JONSWAP(cfjon=0.038),
    FRICTION_COLLINS(cfw=0.015),
    FRICTION_MADSEN(kn=0.05),
    FRICTION_RIPPLES(s=2.65, d=0.0002),
]:
    print(friction.render())
```

A friction coefficient that varies in space is read from an input grid (`var="friction"`, see [Input grids and forcing](input-grids.md)). The `FRICTION` command is still needed to choose the formulation; its coefficient is then ignored.

## Set-up: SETUP

[`SETUP`][rompy_swan.components.physics.SETUP] computes the wave-induced set-up and adds it to the depth. SWAN sets the set-up to zero at the deepest point of the grid; [`supcor`][rompy_swan.components.physics.SETUP.supcor] adds a constant to impose another value.

```python exec="on" source="above" result="text" session="physics"
from rompy_swan.components.physics import SETUP

print(SETUP().render())
print(SETUP(supcor=0.05).render())
```

!!! warning
    Set-up is only meaningful on open coasts, not in closed basins such as lakes and estuaries. SWAN does not compute it correctly in spherical coordinates, nor on unstructured grids, nor in parallel (MPI or OpenMP) runs.

## Diffraction: DIFFRACTION

[`DIFFRACTION`][rompy_swan.components.physics.DIFFRACTION] adds SWAN's phase-decoupled diffraction approximation, reasonable behind breakwaters with a beach down-wave but not in harbours. The grid near the tip of the obstacle should resolve 1/5 to 1/10 of the dominant wave length. Diffraction computations often converge poorly: the SWAN manual recommends under-relaxation, `NUMERIC STOPC ... STAT alfa=0.01` (see [Numerics](numerics.md)), or smoothing with `smpar` and `smnum`.

```python exec="on" source="above" result="text" session="physics"
from rompy_swan.components.numerics import NUMERIC
from rompy_swan.components.physics import DIFFRACTION
from rompy_swan.subcomponents.numerics import STAT, STOPC

print(DIFFRACTION().render())
print(DIFFRACTION(idiffr=1, smpar=0.2, smnum=10).render())
print(NUMERIC(stop=STOPC(mode=STAT(mxitst=50, alfa=0.01))).render())
```

## Obstacles: OBSTACLE

An [`OBSTACLE`][rompy_swan.components.physics.OBSTACLE] is a sub-grid line, such as a breakwater or dam, through which waves are transmitted and against which they are reflected. The `obstacle` field takes an [`OBSTACLES`][rompy_swan.components.physics.OBSTACLES] list, written as one `OBSTACLE` command per obstacle. Each obstacle has a [`LINE`][rompy_swan.subcomponents.physics.LINE] of corner points, which must cross at least one line of the computational grid, and optionally:

| Field | Options |
|---|---|
| `transmission` | [`TRANSM`][rompy_swan.subcomponents.physics.TRANSM] constant coefficient (SWAN default 0, full blockage); [`TRANS1D`][rompy_swan.subcomponents.physics.TRANS1D] per frequency; [`TRANS2D`][rompy_swan.subcomponents.physics.TRANS2D] per frequency and direction; [`GODA`][rompy_swan.subcomponents.physics.GODA] and [`DANGREMOND`][rompy_swan.subcomponents.physics.DANGREMOND], computed from the obstacle height and the incident waves (`DAM`) |
| `reflection` | [`REFL`][rompy_swan.subcomponents.physics.REFL] constant coefficient `reflc` (SWAN default 1.0 when given) |
| `reflection_type` | [`RSPEC`][rompy_swan.subcomponents.physics.RSPEC] specular (default) or [`RDIFF`][rompy_swan.subcomponents.physics.RDIFF] diffuse reflection |
| `freeboard` | [`FREEBOARD`][rompy_swan.subcomponents.physics.FREEBOARD]: transmission and reflection that depend on the freeboard `hgt` |

```python exec="on" source="above" result="text" session="physics"
from rompy_swan.components.physics import OBSTACLE, OBSTACLES
from rompy_swan.subcomponents.physics import GODA, LINE, RDIFF, REFL, TRANSM

breakwater = OBSTACLE(
    transmission=TRANSM(trcoef=0.3),
    reflection=REFL(reflc=0.5),
    reflection_type=RDIFF(pown=1.0),
    line=LINE(xp=[115.735, 115.745], yp=[-32.065, -32.055]),
)
dam = OBSTACLE(
    transmission=GODA(hgt=1.5, alpha=2.6, beta=0.15),
    line=LINE(xp=[115.70, 115.72, 115.74], yp=[-32.10, -32.10, -32.09]),
)
print(PHYSICS(obstacle=OBSTACLES(obstacles=[breakwater, dam])).render())
```

SWAN checks that `reflc² + trcoef² ≤ 1`. [`OBSTACLE_FIG`][rompy_swan.components.physics.OBSTACLE_FIG], also accepted in the list, places the source of free infragravity energy radiated from the shoreline (Ardhuin et al., 2014).

## Vegetation, mud, sea ice and turbulence

[`VEGETATION`][rompy_swan.components.physics.VEGETATION] adds dissipation by vegetation, Suzuki et al. (2011) (`iveg=1`) or Jacobsen et al. (2019) (`iveg=2`, a single layer only). Give the plant height, stem diameter, number of stems per m² and drag coefficient per vertical layer, as lists of the same length:

```python exec="on" source="above" result="text" session="physics"
from rompy_swan.components.physics import VEGETATION

print(VEGETATION(height=[0.5, 1.0], diamtr=[0.01, 0.005], nstems=[400, 100], drag=[1.0, 0.8]).render())
```

[`MUD`][rompy_swan.components.physics.MUD] damps waves over a muddy bottom (Ng, 2000), with the layer thickness `layer`, density `rhom` and viscosity `viscm`. [`TURBULENCE`][rompy_swan.components.physics.TURBULENCE] adds dissipation by turbulent viscosity, by default derived from the depth and current (`CURRENT`, factor `tbcur`).

`SICE` adds dissipation by sea ice; the variants are the formulations of the SWAN manual:

| Component | Writes | Formulation |
|---|---|---|
| [`SICE`][rompy_swan.components.physics.SICE] | `SICE` | SWAN's default, R19 |
| [`SICE_R19`][rompy_swan.components.physics.SICE_R19] | `SICE R19` | Rogers et al. (2019), polynomial in frequency, `c0` to `c6` |
| [`SICE_D15`][rompy_swan.components.physics.SICE_D15] | `SICE D15` | Doble et al. (2015), `chf` |
| [`SICE_M18`][rompy_swan.components.physics.SICE_M18] | `SICE M18` | Meylan et al. (2018), `chf` |
| [`SICE_R21B`][rompy_swan.components.physics.SICE_R21B] | `SICE R21B` | Rogers et al. (2021), `chf`, `npf` |

```python exec="on" source="above" result="text" session="physics"
from rompy_swan.components.physics import MUD, SICE_R21B, TURBULENCE

print(MUD(layer=2.0, rhom=1300.0, viscm=0.0076).render())
print(TURBULENCE(ctb=0.01, tbcur=0.004).render())
print(SICE_R21B(aice=0.8, chf=2.9, npf=4.5).render())
```

Mud layer thickness, plant density, ice concentration and ice thickness can vary in space: they are then read from input grids (`mudlay`, `nplants`, `aice`, `hice`), and the value in the command is ignored. Constant ice is given with the `ICE` command of the forcing group; see [Input grids and forcing](input-grids.md).

## Infragravity waves and scattering

- [`SURFBEAT`][rompy_swan.components.physics.SURFBEAT] switches on the infragravity energy module of Reniers and Zijlema (2022), which follows the transfer of sea-swell energy to bound infragravity waves. Options: the infragravity frequency bin `df`, the number of wave pairs `nmax`, the energy threshold `emin` and the frequency `spacing` (`"uniform"` or `"logarithmic"`).
- [`SCAT`][rompy_swan.components.physics.SCAT] adds the generation and propagation of cross-correlations between waves scattered by rapid variations of bathymetry and currents, the quasi-coherent (QC) approach of Smit and Janssen (2013), relevant for narrow-band swell over shallow topography. Giving both truncations `alpha` and `qmax` logs a warning, since SWAN uses the smaller.
- `BRAGG`, [`BRAGG_FT`][rompy_swan.components.physics.BRAGG_FT] and [`BRAGG_FILE`][rompy_swan.components.physics.BRAGG_FILE] add Bragg scattering by small-scale bottom undulations (Ardhuin and Herbers, 2002), with the bottom spectrum computed by SWAN, by FFT or read from a file.

```python exec="on" source="above" result="text" session="physics"
from rompy_swan.components.physics import BRAGG_FT, SCAT, SURFBEAT

print(SURFBEAT(df=0.01, nmax=50000, emin=0.05, spacing="logarithmic").render())
print(SCAT(iqcm=1, rfac=1.0).render())
print(BRAGG_FT(nreg=10, cutoff=5.0).render())
```

## Limiter: LIMITER

SWAN limits the change of action density per iteration (the action limiter, set in [Numerics](numerics.md)). [`LIMITER`][rompy_swan.components.physics.LIMITER] switches the quadruplets off for good where the Ursell number exceeds `ursell` (SWAN default 10), and stops applying the action limiter to decreasing action density once the fraction of breaking waves exceeds `qb` (default 1).

```python exec="on" source="above" result="text" session="physics"
from rompy_swan.components.physics import LIMITER

print(LIMITER(ursell=10.0, qb=1.0).render())
```

## Switching processes off: OFF

[`OFF`][rompy_swan.components.physics.OFF] switches off a process SWAN includes by default. The `deactivate` field takes an [`OFFS`][rompy_swan.components.physics.OFFS] list, written as one `OFF` command each, after the other physics commands:

| `physics` | Switches off |
|---|---|
| `windgrowth` | wind input (in `GEN1`, `GEN2`, `GEN3`) |
| `quadrupl` | quadruplets (needed without wind) |
| `wcapping` | whitecapping |
| `breaking` | depth-induced breaking |
| `refrac` | refraction (propagation in direction space) |
| `fshift` | frequency shifting |
| `bndchk` | the check of the wave height imposed at the boundary |

```python exec="on" source="above" result="text" session="physics"
offs = OFFS(offs=[OFF(physics="quadrupl"), OFF(physics="bndchk")])
print(PHYSICS(gen=GEN3(), deactivate=offs).render())
```

Switching off refraction or frequency shifting is meant for tests.

## In YAML

In a YAML configuration the physics go under the `physics` key, and each variant is chosen by its `model_type`:

```python exec="on" source="above" result="text" session="physics"
import yaml

physics = PHYSICS.model_validate(
    yaml.safe_load(
        """
        gen:
          model_type: gen3
          source_terms:
            model_type: komen
            agrow: true
        breaking:
          model_type: bkd
          alpha: 1.0
          gamma0: 0.54
        friction:
          model_type: madsen
          kn: 0.05
        triad:
          model_type: dcta
        deactivate:
          offs:
            - physics: quadrupl
        """
    )
)
print(physics.render())
```

To compare physics settings, derive variants of one configuration with `model_copy(update={"physics": ...})` and give each its own run id; the [physics sensitivity](https://rom-py.github.io/rompy-notebooks/notebooks/swan/examples/physics_sensitivity/) example runs WESTHUYSEN, KOMEN and ST6 this way.

```python exec="on"
from rompy_docs.notebooks import see_also

print(see_also("swan", ["physics", "components"]))
```
