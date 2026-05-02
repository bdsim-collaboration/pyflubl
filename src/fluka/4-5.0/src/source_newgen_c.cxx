#include <iostream>

extern "C" {
    void source_newgen_init_c_();
    void source_newgen_c_(double *whasou,int *particle_code);
    void source_newgen_twiss_c_(double emitx, double alpx, double betx, double etax, double etaxp,
                                double emity, double alpy, double bety, double etay, double etayp);
}

void source_newgen_init_c_() {
    std::cout << "source_newgen_init_c> " << std::endl;
}

void source_newgen_c_(double *whasou, int *particle_code) {
    std::cout << "source_newgen_c> " << whasou[0] << std::endl;
    if (whasou[0] == 1) {
      source_newgen_twiss_c_(whasou[1], whasou[2], whasou[3], whasou[4], whasou[5],
                             whasou[6], whasou[7], whasou[8], whasou[9], whasou[10]);
    }
}

void source_newgen_twiss_c_(double emitx, double alpx, double betx, double etax, double etaxp,
                            double emity, double alpy, double bety, double etay, double etayp) {
    std::cout << "source_newgen_twiss_c> " << emitx << " " << alpx << std::endl;
}
