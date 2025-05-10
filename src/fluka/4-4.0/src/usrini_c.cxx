#include <fstream>
#include <iostream>
#include "global_cxx.h"
#include <nlohmann/json.hpp>

TFile *outputFile = nullptr;
TTree *eventTree = nullptr;
SamplerData *samplers = nullptr;

int iEvt = 0;

using json = nlohmann::json;

extern "C" {
    void usrini_c_();  // Fortran 77 adds underscore
}

void loadBookkeeping();
void openRootFile();
void createEventTree();

void usrini_c_() {
    std::cout << "usrini_c_" << std::endl;

    loadBookkeeping();
    openRootFile();
    createEventTree();
}

void loadBookkeeping() {
    std::cout << "loadBookkeeping>" << std::endl;
    std::ifstream f("/tmp/pyflubl/test/pyflubl/run_T300_Usricall/T300_Usricall.json");
    if(!f) {
        std::cerr << "Could not open JSON file." << std::endl;
    }
    json data = json::parse(f);
}

void openRootFile() {
    std::cout << "openRootFile>" << std::endl;
    outputFile = new TFile("pyflubl.root","CREATE");
}

void createEventTree() {
    std::cout << "createEventTree>" << std::endl;
    eventTree = new TTree("event","event");

    eventTree->Branch("eventnr", &iEvt, "eventnr/I");
}