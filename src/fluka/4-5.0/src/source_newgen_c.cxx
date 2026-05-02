#include <iostream>

#include "TMatrixD.h"
#include "TDecompChol.h"
#include "TRandom3.h"
#include "TVectorD.h"

#define DEBUG 1
extern "C" {
    double flnrrn_(double* xdummy);
    void source_newgen_init_c_();
    void source_newgen_c_(double *whasou,int *particle_code);
    void source_newgen_twiss_c_(double emitx, double alpx, double betx, double etax, double etaxp,
                                double emity, double alpy, double bety, double etay, double etayp);
}

void source_newgen_init_c_() {
#if DEBUG
    std::cout << "source_newgen_init_c> " << std::endl;
#endif
}

void source_newgen_c_(double *whasou, int *particle_code) {
#if DEBUG
    std::cout << "source_newgen_c> " << whasou[0] << std::endl;
#endif
    if (whasou[0] == 1) {
      source_newgen_twiss_c_(whasou[1], whasou[2], whasou[3], whasou[4], whasou[5],
                             whasou[6], whasou[7], whasou[8], whasou[9], whasou[10]);
    }
}

void source_newgen_twiss_c_(double emitx, double alpx, double betx, double etax, double etaxp,
                            double emity, double alpy, double bety, double etay, double etayp) {
#if debug
    std::cout << "source_newgen_twiss_c> " << emitx << " " << alpx << " " << betx << " " << etax << " " << etaxp << std::endl;
    std::cout << "source_newgen_twiss_c> " << emity << " " << alpy << " " << bety << " " << etay << " " << etayp << std::endl;
#endif

    int ndim = 6;

    // Mean
    TVectorD mean(ndim);

    // calcualte sigma matrix
    TMatrixD sigma(ndim, ndim);

    sigma[0][0] =  emitx * betx;
    sigma[0][1] = -emitx * alpx;
    sigma[0][2] = 0.0;
    sigma[0][3] = 0.0;
    sigma[0][4] = 0.0;
    sigma[0][5] = 0.0;

    sigma[1][0] = -emitx * alpx;
    sigma[1][1] =  emitx * betx;
    sigma[1][2] = 0.0;
    sigma[1][3] = 0.0;
    sigma[1][4] = 0.0;
    sigma[1][5] = 0.0;

    sigma[2][0] = 0.0;
    sigma[2][1] = 0.0;
    sigma[2][2] =  emity * bety;
    sigma[2][3] = -emity * alpy;
    sigma[2][4] = 0.0;
    sigma[2][5] = 0.0;

    sigma[3][0] = 0.0;
    sigma[3][1] = 0.0;
    sigma[3][2] = -emity * alpy;
    sigma[3][3] =  emity * bety;
    sigma[3][4] = 0.0;
    sigma[3][5] = 0.0;

    sigma[4][0] = 0.0;
    sigma[4][1] = 0.0;
    sigma[4][2] = 0.0;
    sigma[4][3] = 0.0;
    sigma[4][4] = 0.0;
    sigma[4][5] = 0.0;

    sigma[5][0] = 0.0;
    sigma[5][1] = 0.0;
    sigma[5][2] = 0.0;
    sigma[5][3] = 0.0;
    sigma[5][4] = 0.0;
    sigma[5][5] = 0.0;

    TDecompChol chol(sigma);
    chol.Decompose();          // Cholesky decomposition: sigma = L * L^T
    TMatrixD L = chol.GetU();  // Upper triangular in ROOT
    L.Transpose(L);            // Convert to lower triangular

    // TRandom3 rng(42);
    double xdummy = 0.0;
    TVectorD z(6);
    for (int j = 0; j < ndim; j++)
        // FLNRRN random number generate
        z[j] = flnrrn_(&xdummy);

    // Transform: x = mean + L * z
    TVectorD x = mean + L * z;

#if DEBUG
    std::cout << "source_newgen_twiss_c> " << z[0] << " " << z[1] << " " << z[2] << " "
                                           << z[3] << " " << z[4] << " " << z[5] << std::endl;
#endif

}

