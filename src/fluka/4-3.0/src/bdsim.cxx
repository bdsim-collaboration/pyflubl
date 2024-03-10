#include "BDSIMClass.hh"

// JSON loading
#include <fstream>
#include <nlohmann/json.hpp>
using json = nlohmann::json;

// Handle floating point exceptions
#include <fpe.h>

extern "C" {
int bdsim_();
}

int bdsim_() {
    std::cout << "bdsim-fluka>" << std::endl;

    std::ifstream f("../flukaBdsim.json");
    json data = json::parse(f);
    std::cout << data["conversionData"] << std::endl;

    char bdsimExe[200] = "bdsim";
    char gmadInput[200];
    strcpy(gmadInput, (std::string("--file=../")+std::string(data["conversionData"]["bdsimGMADFileName"])).c_str());
    char batch[200] = "--batch";

    char *argv[3];
    argv[0] = bdsimExe;
    argv[1] = gmadInput;
    argv[2] = batch;

    /* Disable floating point exceptions in fortran */
    fedisableexcept(FE_ALL_EXCEPT);

    /* Initialise BDSIM */
    BDSIM* bds = new BDSIM(2,argv);
    if (!bds->Initialised())
    {std::cout << "bdsim-fluka> Intialisation failed" << std::endl; return 1;}

    std::cout << "bdsim-fluka> Custom execution" << std::endl;
    return 0;
}
