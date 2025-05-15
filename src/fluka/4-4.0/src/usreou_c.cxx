#include <iostream>
#include "global_cxx.h"

extern "C" {
    void usreou_c_();
}

void usreou_c_() {
    std::cout << "usreou_c_" << std::endl;

    // fill output
    eventTree->Fill();

    // loop over samplers and flush
    int idx = 0;
    for (const auto& samplername : (*bookkeeping)["samplernames_samplernumber"]) {
        samplers[idx]->Flush();
        idx++;
    }

    eloss->Flush();

    iEvt += 1;
}
