#include <iostream>
#include "global_cxx.h"

TFile *outputFile = nullptr;

extern "C" {
    void usrini_c_();  // Fortran 77 adds underscore
}

void openRootFile();

void usrini_c_() {
    std::cout << "usrini_c_" << std::endl;

    openRootFile();

    outputFile->Close();
}

void openRootFile() {
    std::cout << "openRootFile>" << std::endl;
    outputFile = new TFile("pyflubl.root","CREATE");
}