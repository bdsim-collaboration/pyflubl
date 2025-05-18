#include <fstream>
#include <iostream>
#include <string>
#include "global_cxx.h"

#include <nlohmann/json.hpp>
using json = nlohmann::json;

extern "C" {
    void mgdraw_bxdraw_c_(int *mreg, int *newreg,
                          double *X, double *Y, double *Z,
                          double *Xdc, double *Ydc, double *Zdc,
                          double *etot, double *T, int *partID);
    void mgdraw_endraw_c_(int *mreg,
                          double *X, double *Y, double *Z,
                          double *E);
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

void mgdraw_bxdraw_c_(int *mreg, int *newreg,
                      double *X, double *Y, double *Z,
                      double *Xdc, double *Ydc, double *Zdc,
                      double *etot, double *T,
                      int *partID) {
#ifdef DEBUG
    std::cout << "mgdraw_bxdraw_c_> " << *mreg << " " << *newreg << " "
                                      << *X << " " << *Y << " " << *Z << " "
                                      << *Xdc << " " << *Ydc << " " << *Zdc << " "
                                      << *etot << " " <<  " " << *T << " "
                                      << *partID << std::endl;
#endif

    double x, y, z;
    double xdc, ydc, zdc;
    double xp, yp, zp;

    auto element_name = element_loopup(*newreg);

    (*elementMap)[element_name].transform(*X, *Y, *Z, x, y, z);
    (*elementMap)[element_name].transformDirection(*Xdc, *Ydc, *Zdc, xdc, ydc, zdc);

    xp = (*Xdc)/(*Zdc);
    yp = (*Ydc)/(*Zdc);
    zp = 0;

    auto isampler = sampler_lookup(*newreg);
    if (isampler >= 0) {
        samplers[isampler]->Fill(*etot, x, y, z, xp, yp, zp, *T, *partID);
    }
}

void mgdraw_endraw_c_(int *mreg, double *X, double *Y, double *Z, double *E) {
#ifdef DEBUG
    std::cout << "mgdraw_endraw_c_" << " " << *mreg << " " << *X << " " << *Y << " " << *Z << " "
              << *E << std::endl;
#endif

    auto element_name = element_loopup(*mreg);

    if(element_name != "") {
        eloss->Fill(*E, (*elementMap)[element_name].transformS(*X, *Y, *Z));
    }
}