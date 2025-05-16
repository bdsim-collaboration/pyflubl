#include <iostream>
#include "global_cxx.h"

extern "C" {
    void usreou_c_();
}

void usreou_c_() {
#ifdef DEBUG
    std::cout << "usreou_c_> neloss=" << eloss->n << std::endl;
#endif

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
