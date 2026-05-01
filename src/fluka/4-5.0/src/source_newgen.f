*
*----------------------------------------------------------------------*
*                                                                      *
*     Copyright (C) 2020:  CERN                                        *
*     All Rights Reserved.                                             *
*                                                                      *
*     Source routine or FLUKA 4:                                       *
*                                                                      *
*     Created on 24 September 2020 by David Horvath & Roberto Versaci  *
*                                               ELI ERIC               *
*                                                                      *
*     Modified on 23 Jan 2024      by         David Horvath            *
*                                               ELI ERIC               *
*                                                                      *
*  This is a simplified user written source routine utilizing a        *
*  separate source routine library.                                    *
*                                                                      *
*  It is intended as an alternative new-user-friendly version of the   *
*  source.f routine. Existing FLUKA 4 source routines remain           *
*  compatible.                                                         *
*                                                                      *
*  Note that the beam card still has some meaning - in the scoring the *
*  maximum momentum used in deciding the binning is taken from the     *
*  beam momentum.  Other beam card parameters are obsolete.            *
*                                                                      *
*       Output variables:                                              *
*                                                                      *
*              nomore = if > 0 the run will be terminated              *
*                                                                      *
*----------------------------------------------------------------------*
*
*  Quick start guide:
*  ------------------
*
*  This user source routine template aims to modernize the legacy routine
*  by implementing modern Fortran conventions and to provide built in
*  sampling functions.
*
*  The users only need to change / add code between the BEGINNING and END
*  marks, one section for declaration of user variables, and one for
*  assigning values to the beam parameters.
*
*  By default there is no user variable defined, and all code lines for
*  parameter assignment are commented out. These comments start with the
*  symbol: '*'. To enable one, the '*' needs to be deleted.
*
*  (Note: In Fortran each code line should start in column 7 or further in.)
*
*  Every beam parameter has a default value based on the FLUKA input file.
*  A parameter assignment should only be used if the default value has to be
*  modified.
*
*  There are three ways to assign a value to a parameter:
*
*     1. Direct assignment: A parameter is equal to a value. For example:
*
*           momentum_energy = 0.1D0
*
*        If the parameter defined as a double precision, then the assigned
*        value should be represented as double precision as well so as to
*        not loose numerical precision. To do this a 'D' exponential mark
*        must be used.
*
*     2. Using a sampling function: A parameter is assigned to a value,
*        which is calculated by a separate function. For example:
*
*           coordinate_x = sample_flat_distribution( [min], [max] )
*
*        The parameters with the '[' and ']' brackets need to be replaced
*        with numbers, or user variables containing the desired values, like:
*
*           coordinate_x = sample_flat_distribution( -1.0D0, 1.0D0 )
*
*     3. Using a sampling subroutine: They are similar to function, but they
*        are not returning values directly; instead they modify the variables
*        in their argument list. For example:
*
*           call sample_annular_distribution( [rmin], [rmax], coordinate_x, coordinate_y )
*
*        The example above has two input parameters with brackets, and two
*        output parameters (without bracket). The input parameters have to be
*        provided, as for functions. The output parameter names usually don't
*        need to be changed, but there are cases, where a subset of possible
*        output parameters has to be selected.
*
*  For further details see the FLUKA manual.
*
*----------------------------------------------------------------------*

      module source_variables

         implicit none

         integer, save :: particle_code
         integer, save :: heavyion_atomic_number, heavyion_mass_number, heavyion_isomer

         double precision, save :: momentum_energy, particle_weight
         logical, save :: energy_logical_flag

         double precision, save :: divergence_x, divergence_y
         logical, save :: gaussian_divergence_logical_flag

         double precision, save :: coordinate_x, coordinate_y, coordinate_z

         integer, save :: direction_flag
         double precision, save :: direction_cosx, direction_cosy, direction_cosz

         double precision, save :: polarization_cosx, polarization_cosy, polarization_cosz

         double precision, save :: particle_age
         double precision, save :: kshort_component
         double precision, save :: delayed_radioactive_decay

      end module source_variables

      include 'source_library.inc'

*=== Source ===========================================================*

      subroutine SOURCE ( nomore )

      use source_library
      use source_variables

      implicit none

      double precision xdummy
      integer :: nomore, debug_lines = 100
      logical, save :: first_run = .true., debug_logical_flag = .false.

      type(phase_space) phase_space_entry

      ! Function declarations

      double precision sample_flat_momentum_energy
      double precision sample_gaussian_momentum_energy
      double precision sample_maxwell_boltzmann_energy
      double precision sample_histogram_momentum_energy
      double precision sample_spectrum_momentum_energy
      double precision sample_discrete_momentum_energy

      double precision sample_flat_distribution
      double precision sample_gaussian_distribution
      double precision sample_histogram_file
      double precision sample_spectrum_file
      double precision sample_discrete_file

      double precision FLRNDM

      ! ====================================
      ! BEGINNING of user declared variables
      ! ====================================



      ! ==============================
      ! END of user declared variables
      ! ==============================

      nomore = 0

      write(*,*) "PYFLUBL-SOURCE>"

      call initialization()

      if ( first_run ) then
         ! ==================================
         call source_newgen_init_c()

         ! ==================================
         ! BEGINNING of custom initialization
         ! ==================================



         ! ============================
         ! END of custom initialization
         ! ============================

         first_run = .false.
      end if

      ! ==============================
      ! BEGINNING of customizable code
      ! ==============================

      write(*,*) "PYFLUBL-SOURCE>"
      write(*,*) "PYFLUBL-SOURCE>", whatou(1), whatou(2), whatou(3), whatou(4), whatou(5), whatou(6)
      write(*,*) "PYFLUBL-SOURCE>", whatou(7), whatou(8), whatou(9), whatou(10), whatou(11), whatou(12)
      write(*,*) "PYFLUBL-SOURCE>", whatou(13), whatou(14), whatou(15), whatou(16), whatou(17), whatou(18)

      ! ==================================
      call source_newgen_c(particle_code)

      ! 1. Accessing variables from the SOURCE card
      ! ===========================================
      ! Values set on the SOURCE card can be accessed with the following variables:
      !    Numerical values (double precision):
      !       WHASOU(1), WHATSOU(2), .., WHASOU(18)
      !    SDUM text (8 character):
      !       SDUSOU


      ! 2. Primary particle
      ! ===================


      ! 2.1. Particle code
      ! ------------------
      ! FLUKA particle code of the primary
      !    See section 5.1 of the FLUKA manual for the list of particle code
      ! Default:
      !    Particle code of the primary defined on the BEAM card if present, otherwise 1 (proton)

*      particle_code = ...


      ! 2.2. Heavy ion / Radioactive isotope
      ! ------------------------------------
      ! If the HEAVYION or ISOTOPE particle type (particle_code = -2) has been selected
      ! on the BEAM card, the ion can be specified with the following parameters:
      ! Defaults:
      !    Specified on HI-PROPE card (if present), otherwise Z=6, A=12, I=0 (12C)

*      heavyion_atomic_number = ...
*      heavyion_mass_number = ...
*      heavyion_isomer = ...


      ! 3. Particle momentum / energy and weight
      ! ========================================


      ! 3.1. Momentum & Energy
      ! ----------------------
      ! Set the momentum [GeV/c] or the kinetic energy [GeV] of the primary particle
      ! For heavy ions values are per nuclear mass unit.
      ! Default:
      !    Momentum calculated from values set on the BEAM card (if present), 200 GeV/c otherwise

*      momentum_energy = ...


      ! 3.2. Energy flag
      ! ----------------
      ! Select between momentum and energy
      ! If the energy flag is:
      !    .false. : The momentum_energy variable contains the momentum of the particle
      !    .true.  : The momentum_energy variable contains the kinetic energy of the particle
      ! Default:
      !    .false.

*      energy_logical_flag = .true.


      ! 3.3. Particle weight
      ! --------------------
      ! Sets the initial weight of the primary
      ! Default:
      !    1.0D0

*      particle_weight = ...


      ! 3.4. Sampling functions and subroutines
      ! ---------------------------------------


      ! 3.4.1. Flat distribution
      ! ------

*      momentum_energy = sample_flat_momentum_energy( [min], [max] )


      ! 3.4.2. Gaussian distribution
      ! ------

*      momentum_energy = sample_gaussian_momentum_energy( [mean], [fwhm] )


      ! 3.4.3. Maxwell-Boltzmann distribution
      ! ------
      !    Temperature is given in GeV, energy flag must be .true.

*      momentum_energy = sample_maxwell_boltzmann_energy( [temperature] )


      ! 3.4.4. Sampling from histogram
      ! ------
      !    Possible [unit]s: "TeV",   "GeV",   "MeV",   "keV"    "eV"
      !                      "TeV/c", "GeV/c", "MeV/c", "keV/c", "eV/c"
      !                      "J"
      !    Histogram file has to have 3 columns:
      !       - Emin (of the bin)
      !       - Emax (of the bin)
      !       - dN/dE (bin height; NOTE: doesn't need to be normalized)
      !    Sampling from different files treated separately, up to 100 files.

*      momentum_energy = sample_histogram_momentum_energy( [filename], [unit] )


      ! 3.4.5. Sampling from spectrum
      ! ------
      !    Possible [unit]s: "TeV",   "GeV",   "MeV",   "keV"    "eV"
      !                      "TeV/c", "GeV/c", "MeV/c", "keV/c", "eV/c"
      !                      "J"
      !    Spectrum file has to have 2 columns:
      !       - Energy
      !       - Intensity
      !    Sampling from different files treated separately, up to 100 files.

*      momentum_energy = sample_spectrum_momentum_energy( [filename], [unit] )


      ! 3.4.6. Sampling from discrete spectrum lines
      ! ------
      !    Possible [unit]s: "TeV",   "GeV",   "MeV",   "keV"    "eV"
      !                      "TeV/c", "GeV/c", "MeV/c", "keV/c", "eV/c"
      !                      "J"
      !    Discrete spectrum file has to have 2 columns:
      !       - Energy
      !       - Intensity
      !    Sampling from different files treated separately, up to 100 files.

*      momentum_energy = sample_discrete_momentum_energy( [filename], [unit] )


      ! 3.4.7. Exponential distribution
      ! ------
      !    Input variables:
      !       - e_min [GeV]
      !       - e_max [GeV]
      !       - intensity_ratio = (int_e_max / int_e_min)
      !    Output variables:
      !       - momentum_energy
      !       - particle_weight

*      call sample_exponential_energy_weight( [e_min], [e_max], [intensity_ratio], momentum_energy, particle_weight )


      ! 4. Beam angular divergence
      ! ==========================


      ! 4.1. Divergence value
      ! ---------------------
      ! Sets the beam divergence in the X-Z (divergence_x) and Y-Z (divergence_y) planes [rad]
      ! Divergences are applied before beam direction
      ! Defaults:
      !    Set on the BEAM card if present (converted to radians), 0.0 otherwise

*      divergence_x = ...
*      divergence_y = ...


      ! 4.2. Divergence type
      ! --------------------
      ! Selects between flat and Gaussian divergence.
      ! If it is set to:
      !    .false. : The divergence is flat - Divergence values are taken as full opening angle
      !    .true.  : The divergence is Gaussian - Divergence values are taken as FWHM of the distribution
      ! Default:
      !    Set in the BEAM card (if present), .false. otherwise

*      gaussian_divergence_logical_flag = .true.


      ! 5. Beam starting position
      ! =========================


      ! 5.1. Coordinates
      ! ----------------
      ! Sets the starting coordinates (x,y,z) of the beam [cm]
      ! Defaults:
      !    Coordinates set on the BEAMPOS card if present, (0.0D0, 0.0D0, 0.0D0) otherwise

*      coordinate_x = ...
*      coordinate_y = ...
*      coordinate_z = ...


      ! 5.2. Sampling functions and subroutines
      ! ---------------------------------------


      ! 5.2.1. Annular distribution
      ! ------
      ! Applies an annular distribution to any two coordinates
      !    Input variables:
      !       - rmin [cm]
      !       - rmax [cm]
      !       - Two coordinates of the center of the annular distribution (coordinate_[a/b]) [cm]
      !         Replace [a] and [b] with "x", "y", or "z".
      !    Output variables:
      !       - Modified coordinates of the sampled location (input values have been overwritten)

*      call sample_annular_distribution( [rmin], [rmax], coordinate_[a], coordinate_[b] )


      ! 6. Beam direction
      ! =================


      ! 6.1. Direction cosines
      ! ----------------------
      ! Sets the direction cosines of the beam with respect to the X,Y and Z-axis
      ! Defaults:
      !    Set on the BEAMPOS card if present, otherwise (0.0D0, 0.0D0, 1.0D0)

*      direction_cosx = ...
*      direction_cosy = ...
*      direction_cosz = ...


      ! 6.2. Direction flag
      ! -------------------
      ! Sets how the direction cosines are treated
      ! Possible values:
      !    0 : All 3 direction cosines are taken into account (values will be normalized)
      !    1 : Only direction cosines with respect to the X- and Y-axis are taken into account, the third cosine (Z) is calculated
      !           with a positive sign
      !    2 : Only direction cosines with respect to the X- and Y-axis are taken into account, the third cosine (Z) is calculated
      !           with a negative sign
      !    Default:
      !        0

*      direction_flag = ...


      ! 6.3. Sampling functions and subroutines
      ! ---------------------------------------

      ! 6.3.1. Isotropic distribution
      ! ------
      !    Output variables:
      !       - direction_cosx
      !       - direction_cosy
      !       - direction_cosz

*      call sample_isotropic_direction( direction_cosx, direction_cosy, direction_cosz )


      ! 7. Other changeable parameters
      ! ==============================
      ! For most of the uses none of these parameters should be changed from the defaults


      ! 7.1. Polarization cosines
      ! -------------------------
      ! The three inputs indicate the direction cosines of the particle polarization
      ! Defaults:
      !    (-2.0D0, 0.0D0, 0.0D0)

*      polarization_cosx = ...
*      polarization_cosy = ...
*      polarization_cosz = ...


      ! 7.2. Particle age
      ! -----------------
      ! Sets the starting age of the primary particle in seconds
      ! Default:
      !    0.0D0

*      particle_age = ...


      ! 7.3. Kshort component
      ! ---------------------
      ! Sets The Kshort component of the K0/K0bar
      ! Default:
      !    -2.0D

*      kshort_component = ...


      ! 7.4. Delayed radioactive decay
      ! ------------------------------
      ! Sets the delay for the radioactive decay with respect to the standard primary zero time
      ! Default:
      !    0.0D0

*      delayed_radioactive_decay = ...


      ! 8. General sampling functions
      ! =============================
      ! General sampling functions for coordinates, direction, etc. Should not be used for
      ! momentum / energy sampling.


      ! 8.1. Flat distribution
      ! ----------------------

*      ... = sample_flat_distribution([min], [max])


      ! 8.2. Gaussian distribution
      ! --------------------------

*       ... = sample_gaussian_distribution([mean], [fwhm])


      ! 8.3. Sampling from histogram file
      ! ---------------------------------
      ! Sampling from different files treated separately, up to 100 files.
      ! See 'sample_histogram_momentum_energy' for more details.

*      ... = sample_histogram_file([filename], [scaling_factor])


      ! 8.4. Sampling from spectrum file
      ! --------------------------------
      ! Sampling from different files treated separately, up to 100 files.
      ! See 'sample_spectrum_momentum_energy' for more details.

*      ... = sample_spectrum_file([filename], [scaling_factor])


      ! 8.5. Sampling from dicrete spectrum file
      ! ----------------------------------------
      ! Sampling from different files treated separately, up to 100 files.
      ! See 'sample_discrete_momentum_energy' for more details.

*      ... = sample_dictrete_file([filename], [scaling_factor])


      ! 9. Sampling from phase space file
      ! =================================
      ! Allows to read particle information from a phase space file and sets the primary accordingly


      ! 9.1. Input variables
      ! --------------------
      ! - [filename]
      ! - [energy_unit]:
      !      Possible [energy unit]s: "TeV",   "GeV",   "MeV",   "keV"    "eV"
      !                               "TeV/c", "GeV/c", "MeV/c", "keV/c", "eV/c"
      !                               "J"
      ! - [length_unit]:
      !      Possible [length_unit]s: "km", "m", "cm", "mm"
      ! - [sequential_logical_flag]:
      !      Possible values:
      !         .false. : Particles from the phase space file selected randomly
      !         .true.  : Particles from the phase space file read sequentially, the simulation stops if all particles has been read


      ! 9.2. File format
      ! ----------------
      ! The phase space file has to contain the following columns in this order:

      ! - Particle code [integer]

      ! - Particle momentum / energy [double precision]

      ! - Starting X coordinate [double precision]
      ! - Starting Y coordinate [double precision]
      ! - Starting Z coordinate [double precision]

      ! - Starting X direction cosine [double precision]
      ! - Starting Y direction cosine [double precision]
      ! - Starting Z direction cosine [double precision]

      ! - Particle weight [double precision]


      ! 9.3. Output variables
      ! ---------------------
      ! - phase_space_entry: Variable containing information of a single particle from the phase space file
      ! - nomore: Flag to indicate that all particles has been read


      ! 9.4. Subroutine call
      ! --------------------

*      call read_phase_space_file( [filename], [energy_unit], [length_unit], phase_space_entry, [sequential_logical_flag], nomore )


      ! 9.5. Reading information from 'phase_space_entry' variable
      ! ----------------------------------------------------------
      ! The information stored in the 'phase_space_entry' has to be copied to the appropriate variables

*      particle_code   = phase_space_entry%pc
*      momentum_energy = phase_space_entry%m_e

*      energy_logical_flag = .true.

*      coordinate_x = phase_space_entry%x
*      coordinate_y = phase_space_entry%y
*      coordinate_z = phase_space_entry%z

*      direction_cosx = phase_space_entry%u
*      direction_cosy = phase_space_entry%v
*      direction_cosz = phase_space_entry%w

*      particle_weight = phase_space_entry%wei


      ! 10. Debugging
      ! ============


      ! 10.1. Debug logical flag
      ! ------------------------
      ! Enables or disables the printout of the beam parameters for debugging
      ! Possible values:
      !    .false. : Debug output disabled (Default)
      !    .true.  : Debug output enabled

*      debug_logical_flag = .true.


      ! 10.2. Debug lines
      ! -----------------
      ! Sets the maximum number of lines printed in the debug output
      ! Default:
      !    100

*      debug_lines = ...


      ! ==============================================
      ! END of customizable code - Do not change below
      ! ==============================================

      if ( nomore .eq. 0 ) then

         call set_primary()

         if ( debug_logical_flag ) call print_primary( debug_lines )

      end if

      return
*=== End of subroutine Source =========================================*
      end
