#include "BDSIMClass.hh"

extern "C" {
  int bdsim_();
}

int bdsim_() {
    std::cout << "bdsim-fluka>" << std::endl;

    BDSIM* bds = new BDSIM();
    if (!bds->Initialised())
    {std::cout << "Intialisation failed" << std::endl; return 1;}

    std::cout << "Custom stuff here" << std::endl;
}
