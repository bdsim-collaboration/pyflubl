#include <fstream>
#include <iostream>
#include <string>
#include "global_cxx.h"

#include <nlohmann/json.hpp>
using json = nlohmann::json;

extern "C" {
    void mgdraw_bxdraw_c_(int *mreg, int *newreg, double *x, double *y, double *z);
}

std::string element_loopup(int reg_number) {

    // black hole and air
    if(reg_number <= 2 ) { // TODO can this change?
        return std::string("");
    }

    auto element_name = std::string((*bookkeeping)["regionnumber_element"][std::to_string(reg_number)]);
    return element_name;
}

int sampler_lookup(int reg_number) {

    // black hole and air
    if(reg_number <= 2 ) {
        return -1;
    }

    auto element_name = std::string((*bookkeeping)["regionnumber_element"][std::to_string(reg_number)]);
    auto category = std::string((*bookkeeping)["elements"][element_name]["category"]);

    if (category == "sampler") {
        int sampler_number = (*bookkeeping)["samplernames_samplernumber"][element_name];
        return sampler_number;
    }
    return -1;
}

void localcoord_lookup(int reg_number, double *global, double *local) {
    auto element_name = element_loopup(reg_number);
}

void mgdraw_bxdraw_c_(int *mreg, int *newreg, double *X, double *Y, double *Z) {
    std::cout << "mgdraw_bxdraw_c_> " << *mreg << " " << *newreg << " " << *X << " " << *Y << " " << *Z << std::endl;

    double x, y, z;

    auto element_name = element_loopup(*newreg);

    (*elementMap)[element_name].transform(*X, *Y, *Z, x, y, z);

    auto isampler = sampler_lookup(*newreg);
    if (isampler >= 0) {
        samplers[isampler]->Fill(0, x, y, z, 0, 0, 0, 0, 0);
    }
}