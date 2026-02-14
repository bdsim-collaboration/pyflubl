#include <iostream>
#include "global_cxx.h"

extern "C" {
    void usrout_c_();
}


void closeRootFile();

void usrout_c_() {
    std::cout << "usrout_c_" << std::endl;

    closeRootFile();
}

void closeRootFile() {

    eventTree->Write();

    std::cout << "closeRootFile>" << std::endl;
    if(outputFile)
        outputFile->Close();
}