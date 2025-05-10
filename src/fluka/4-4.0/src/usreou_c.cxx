#include <iostream>
#include "global_cxx.h"

extern "C" {
    void usreou_c_();
}

void usreou_c_() {
    std::cout << "usreou_c_" << std::endl;

    eventTree->Fill();

    iEvt += 1;
}
