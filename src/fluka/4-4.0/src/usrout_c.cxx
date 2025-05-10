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
    std::cout << "closeRootFile>" << std::endl;
    outputFile->Close();
}