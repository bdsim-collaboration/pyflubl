#include <iostream>
#include "global_cxx.h"

TFile *outputFile = nullptr;
TTree *eventTree = nullptr;
SamplerData *samplers = nullptr;

int iEvt = 0;

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