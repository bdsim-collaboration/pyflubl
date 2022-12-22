cmake_minimum_required (VERSION 3.2)
project (flukaBdsim LANGUAGES C CXX Fortran)

# fluka includes 
set(FLUKA_INCLUDE_DIR "/Users/sboogert/Dropbox/Physics/coderepos/pyflubl/src/fluka/4-3.0/fluka4-3.0/include/")
set(FLUKA_LIBRARY_DIR "/Users/sboogert/Dropbox/Physics/coderepos/pyflubl/src/fluka/4-3.0/fluka4-3.0/lib/")

# enable_language(fortran)
set(CMAKE_FORTRAN_COMPILER "/opt/local/bin/gfortran")

# add_compile_options(-O -Wall -fcheck=all -g -fbacktrace)

# point cmake to my own custom installation directory that's not a system dir
# this is where BDSIMConfig.cmake exists
set(CMAKE_PREFIX_PATH /Users/sboogert/Dropbox/Physics/coderepos/bdsim/bdsim/.install_intel_g4.11.00.p03/lib/cmake/bdsim/)

# required RPATH
set(CMAKE_INSTALL_RPATH "${Geant4_LIBRARY_DIR};${CMAKE_INSTALL_PREFIX}/lib;${ROOT_LIBRARY_DIR}")

# find the package and set up variables
find_package(BDSIM REQUIRED)

# make a program and link to bdsim libraries
add_executable(flukaBdsim src/magfld.f src/source.f src/usrini.f src/usrout.f src/mgdraw.f)
add_library(bdsimFlukaCxx SHARED src/bdsim.cxx src/magfldBdsim.cxx src/sourceBdsim.cxx src/mgdrawBdsim.cxx)
# add_library(bdsimFlukaFort src/magfld.f src/source.f src/usrini.f src/usrout.f src/mgdraw.f)
target_include_directories(bdsimFlukaCxx PUBLIC ${BDSIM_INCLUDE_DIR} ${CMAKE_SOURCE_DIR}/include)
target_include_directories(flukaBdsim PUBLIC ${FLUKA_INCLUDE_DIR})
target_link_libraries(bdsimFlukaCxx ${BDSIM_LIBRARIES})
target_link_libraries(flukaBdsim bdsimFlukaCxx)
target_link_libraries(flukaBdsim ${FLUKA_LIBRARY_DIR}/libfluka.a stdc++ supc++ m)

