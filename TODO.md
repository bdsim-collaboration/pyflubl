# TODO list

* Flexible material (g4 material, fluka material)
* Lattice for custom FLUKA and GDML objects 
* Magnetic field for dipole and quadrupole objects 
* Scoring mesh 
* Samplers 
* Labelling of external g4 geometry (vacuum and outer container)
* Labelling of external fluka geometry (vacuum for field)
* ~~Options similar to BDSIM for beampipe and external "container" volume~~
* Ask CERN group for (original) FLUKA magnet geometry
* ~~FLUKA and GDML input custom objects with files and code~~
* ~~Define FLUKA beamline element~~
* ~~Flexible geometry source (g4registry, fregistry)~~
* ~~Fix bend rotation~~ 
* ~~Add generic rotation (transform3d)~~

## BDSIM elements

1. ~~drift~~
2. ~~rbend~~
3. ~~sbend~~
4. ~~quadrupole~~
5. sextupole
6. octupole
7. decapole
8. ~~multipole~~ -> drift
9. ~~thinmultipole~~ impossible
10. vkicker
11. hkicker
12. tkicker
13. ~~rf~~ impossible -> drift
14. ~~rfx~~ impossible -> drift
15. ~~rfy~~ impossible -> drift
17. ~~target~~
18. ~~rcol~~
19. ~~ecol~~
20. ~~jcol~~
21. degrader
22. muspoiler
23. ~~shield~~
24. ~~dump~~
25. solenoid
26. ~~wirescanner~~
27. ~~laser~~ impossible
28. ~~gap~~
29. crystalcol
30. undulator
31. ~~transform3d~~ impossible
32. ~~matrix~~ impossible
33. ~~thinmatrix~~ impossible
34. ~~element~~
35. ~~marker~~ impossible
36. ct

## Fluka scoring cards

1. usrtrack (single dif $d\phi / dE$)
2. usrcoll
3. usrbdx (double diff $d\phi / dEd\Omega$)
4. ~~usrbin (spatial distribution)~~
5. usryield 
6. score
7. resnucle
8. detect
9. eventbin
10. ~~rotprbin~~
11. tcquench
12. ~~userdump~~
13. auxscore

## Fluka input options 

1. ~~ASSIGNMAt~~
1. AUTOIMBS
1. AUXSCORE
1. ~~BEAM~~
1. ~~BEAMAXES~~
1. ~~BEAMPOSit~~
1. BIASING
1. COMPOUND
1. CORRFACT
1. CRYSTAL
1. DCYSCORE
1. DCYTIMES
1. ~~DEFAULTS~~
1. DELTARAY
1. DETECT
1. DETGEB
1. DISCARD
1. ~~ELCFIELD~~
1. EMF
1. EMF-BIAS
1. EMFCUT
1. EMFFIX
1. EMFFLUO
1. EMFRAY
1. EVENTBIN
1. EVENTDAT
1. EXPTRANS
1. ~~FIXED~~
1. FLUKAFIX
1. ~~FREE~~
1. GCR-SPE
1. ~~GEOBEGIN~~
1. ~~GEOEND~~
1. ~~GLOBAL~~
1. HI-PROPErt
1. IONFLUCT
1. IONTRANS
1. IRRPROFIle
1. LAM-BIAS
1. LOW-BIAS
1. LOW-DOWN
1. LOW-MAT
1. LOW-NEUT
1. LOW-PWXS
1. MAT-PROP
1. MATERIAL
1. MCSTHRESh
1. ~~MGNCREATe~~
1. ~~MGNDATA~~
1. ~~MGNFIELD~~
1. MULSOPT
1. MUPHOTON
1. OPEN
1. OPT-PROD
1. OPT-PROP
1. PAIRBREM
1. PART-THRes
1. PHOTONUC
1. PHYSICS
1. PLOTGEOM
1. POLARIZAti
1. PROFILE
1. RAD-BIOL
1. RADDECAY
1. ~~RANDOMIZe~~
1. RESNUCLEi
1. ~~ROT-DEFIni~~
1. ~~ROTPRBIN~~
1. SCORE
1. ~~SOURCE~~
1. SPECSOUR
1. SPOTBEAM
1. SPOTDIR
1. SPOTPOS
1. SPOTTRAN
1. ~~START~~
1. STEPSIZE
1. STERNHEIme
1. ~~STOP~~
1. SYRASTEP
1. TCQUENCH
1. THRESHOLd
1. TIME-CUT
1. ~~TITLE~~
1. TPSSCORE
1. ~~USERDUMP~~
1. USERWEIG
1. USRBDX
1. ~~USRBIN~~
1. USRCOLL
1. USRGCALL
1. ~~USRICALL~~
1. ~~USROCALL~~
1. USRTRACK
1. USRYIELD
1. WW-FACTOr
1. WW-PROFIle
1. WW-THRESh