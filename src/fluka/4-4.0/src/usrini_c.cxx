#include <fstream>
#include <iostream>
#include "global_cxx.h"

TFile *outputFile = nullptr;
TTree *eventTree = nullptr;
std::map<std::string, ElementData> *elementMap = nullptr;
SamplerData **samplers = nullptr;
ElossData *eloss = nullptr;
json *bookkeeping = nullptr;

int iEvt = 0;

extern "C" {
    void usrini_c_();  // Fortran 77 adds underscore
}

void loadBookkeeping();
void dumpBookkeeping();
void createElementData();
void openRootFile();
void createEventTree();


void usrini_c_() {
    std::cout << "usrini_c_" << std::endl;

    loadBookkeeping();
    dumpBookkeeping();
    createElementData();
    openRootFile();
    createEventTree();
}

void loadBookkeeping() {
    std::cout << "loadBookkeeping>" << std::endl;
    std::ifstream f("/tmp/pyflubl/test/pyflubl/run_IPAC_2025/IPAC_2025.json");
    //std::ifstream f("/tmp/pyflubl/test/pyflubl/run_T300_Usricall/T300_Usricall.json");
    if(!f) {
        std::cerr << "Could not open JSON file." << std::endl;
    }
    bookkeeping = new json();
    f >> *bookkeeping;

    //std::cout << (*bookkeeping).dump(4) << std::endl;
}

void dumpBookkeeping() {
    std::cout << "dumpBookkeeping>" << std::endl;

    for (auto& [key, value] : (*bookkeeping).items()) {
        std::cout << "dumpBookkeeping> key=" << key << std::endl;
    }
}

void createElementData() {
    // Create element map

    elementMap = new std::map<std::string, ElementData>();

    // loop over elements and make ElementData for later usage
    for (const auto& [elementname, elementinfo] : (*bookkeeping)["elements"].items()) {
        std::cout << "createElementData> " << elementname << std::endl;

        auto rotation_json = elementinfo["rotation"];
        auto translation_json = elementinfo["translation"];

        double x = translation_json[0];
        double y = translation_json[1];
        double z = translation_json[2];

        double m11 = rotation_json[0][0];
        double m12 = rotation_json[0][1];
        double m13 = rotation_json[0][2];

        double m21 = rotation_json[1][0];
        double m22 = rotation_json[1][1];
        double m23 = rotation_json[1][2];

        double m31 = rotation_json[2][0];
        double m32 = rotation_json[2][1];
        double m33 = rotation_json[2][2];

        auto e = ElementData(elementname,
                             x,y,z,
                             m11, m12, m13,
                             m21, m22, m23,
                             m31, m32, m33);

        (*elementMap)[elementname] = e;
    }

}

void openRootFile() {
    std::cout << "openRootFile>" << std::endl;
    outputFile = new TFile("pyflubl.root","CREATE");
}

void createEventTree() {
    std::cout << "createEventTree>" << std::endl;
    eventTree = new TTree("event","event");

    // number of samplers
    auto nsampler = (*bookkeeping)["samplernames_samplernumber"].size();
    std::cout << "createEventTree> nsampler=" << nsampler << std::endl;

    // create sampler data structures array
    samplers = new SamplerData*[nsampler];

    // loop over sampler names and allocate data structure
    int idx = 0;
    for (const auto& [samplername, samplernumber] : (*bookkeeping)["samplernames_samplernumber"].items()) {
        std::cout << "createEventTree> " << samplername<< std::endl;
        samplers[idx] = new SamplerData();
        samplers[idx]->SetBranchAddresses(eventTree, samplername);
        samplers[idx]->Flush();
        idx++;
    }

    // make eloss
    eloss = new ElossData();
    eloss->Flush();
    eloss->SetBranchAddresses(eventTree);
}