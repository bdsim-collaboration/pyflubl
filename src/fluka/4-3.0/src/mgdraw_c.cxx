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

/* Region number to region name lookup */
std::string regionname_lookup(int reg_number) {
#ifdef DEBUG
    std::cout << "regionname_lookup> " << reg_number << std::endl;
#endif
    auto regionname = (*bookkeeping)["regionnumber_regionname"][std::to_string(reg_number)];

#ifdef DEBUG
    std::cout << "regionname_lookup> " << reg_number << " " << regionname << std::endl;
#endif

    return regionname;
}

/* Region number to element lookup */
std::string element_lookup(int reg_number) {

    // look up region name
    auto region_name = regionname_lookup(reg_number);

    if(region_name == "BLKHOLE" ||
       region_name == "PARKING" ||
       region_name == "WORLD") {
           return std::string("");
       }

    auto element_name = std::string((*bookkeeping)["regionnumber_element"][std::to_string(reg_number)]);
    return element_name;
}

/* Region number to sampler lookup */
int sampler_lookup(int reg_number) {

    // look up region name
    auto region_name = regionname_lookup(reg_number);

    if(region_name == "BLKHOLE" ||
       region_name == "PARKING" ||
       region_name == "WORLD") {
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

/* Region number to local coordinate look up (unused right now TODO)*/
void localcoord_lookup(int reg_number, double *global, double *local) {
    auto element_name = element_lookup(reg_number);
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

    auto element_name = element_lookup(*newreg);

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

    auto element_name = element_lookup(*mreg);

    if(element_name != "") {
        eloss->Fill(*E, (*elementMap)[element_name].transformS(*X, *Y, *Z));
    }
}