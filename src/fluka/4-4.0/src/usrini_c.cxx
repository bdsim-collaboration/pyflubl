#include <fstream>
#include <iostream>
#include "global_cxx.h"

TFile *outputFile = nullptr;
TTree *eventTree = nullptr;
SamplerData **samplers = nullptr;
json *bookkeeping = nullptr;

int iEvt = 0;

extern "C" {
    void usrini_c_();  // Fortran 77 adds underscore
}

void loadBookkeeping();
void dumpBookkeeping();
void openRootFile();
void createEventTree();


void usrini_c_() {
    std::cout << "usrini_c_" << std::endl;

    loadBookkeeping();
    dumpBookkeeping();
    openRootFile();
    createEventTree();
}

void loadBookkeeping() {
    std::cout << "loadBookkeeping>" << std::endl;
    std::ifstream f("/tmp/pyflubl/test/pyflubl/run_T300_Usricall/T300_Usricall.json");
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
        std::cout << samplername<< std::endl;
        samplers[idx] = new SamplerData();
        samplers[idx]->SetBranchAddresses(eventTree, samplername);
        samplers[idx]->Flush();
        idx++;
    }

    eventTree->Branch("eventnr", &iEvt, "eventnr/I");
}