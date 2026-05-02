#include <iostream>

#include "TMatrixD.h"
#include "TDecompChol.h"
#include "TRandom3.h"
#include "TVectorD.h"

#define DEBUG 1

TVectorD mean(6);
TMatrixD cholSigmaL(6,6);

extern "C" {
    double flnrrn_(double* xdummy);
    void source_newgen_init_c_(double *whasou);
    void source_newgen_twiss_init_c_(double emitx, double alpx, double betx, double etax, double etaxp,
                                     double emity, double alpy, double bety, double etay, double etayp,
                                     double espread,
                                     double x0, double xp0, double y0, double yp0, double T0, double E0);

    void source_newgen_c_(double *whasou, int *particle_code, double *momentum_energy,
                          double *coordinate_x, double *coordinate_y, double *coordinate_z,
                          double *direction_cosx, double *direction_cosy, double *direction_cosz);
    void source_newgen_twiss_c_(int *particle_code, double *momentum_energy,
                                double *coordinate_x, double *coordinate_y, double *coordinate_z,
                                double *direction_cosx, double *direction_cosy, double *direction_cosz);
}

void source_newgen_init_c_(double *whasou) {
#if DEBUG
    std::cout << "source_newgen_init_c> " << whasou[0] << std::endl;
#endif

    if (whasou[0] == 1) {
        source_newgen_twiss_init_c_(whasou[1], whasou[2], whasou[3], whasou[4], whasou[5],
                                    whasou[6], whasou[7], whasou[8], whasou[9], whasou[10],
                                    whasou[11],
                                    whasou[12], whasou[13], whasou[14], whasou[15], whasou[16], whasou[17]);
    }
}

void source_newgen_twiss_init_c_(double emitx, double alpx, double betx, double etax, double etaxp,
                                 double emity, double alpy, double bety, double etay, double etayp,
                                 double espread,
                                 double x0, double xp0, double y0, double yp0, double T0, double E0) {
#if DEBUG
    std::cout << "source_newgen_twiss_c> x (e, a, b, eta, etap)   : " << emitx << " " << alpx << " " << betx << " " << etax << " " << etaxp << std::endl;
    std::cout << "source_newgen_twiss_c> y (e, a, b, eta, etap)   : " << emity << " " << alpy << " " << bety << " " << etay << " " << etayp << std::endl;
    std::cout << "source_newgen_twiss_c> espread                  : " << espread << std::endl;
    std::cout << "source_newgen_twiss_c> x0, xp0, y0, yp0, T0, E0 : " << x0 << " " << xp0 << " " << y0 << " " << yp0 << " " << T0 << " " << E0 << std::endl;
#endif

    int ndim = 6;

    // Mean
    mean[0] = x0;
    mean[1] = xp0;
    mean[2] = y0;
    mean[3] = yp0;
    mean[4] = T0;
    mean[5] = E0;

    // calcualte sigma matrix
    TMatrixD sigma(ndim, ndim);

    // compute gamma
    double gamx = (1.+pow(alpx,2))/betx;
    double gamy = (1.+pow(alpy,2))/bety;

    // fill sigma matrix
    sigma[0][0] =  emitx * betx;
    sigma[0][1] = -emitx * alpx;
    sigma[0][2] = 0.0;
    sigma[0][3] = 0.0;
    sigma[0][4] = 0.0;
    sigma[0][5] = 0.0;

    sigma[1][0] = -emitx * alpx;
    sigma[1][1] =  emitx * gamx;
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
    sigma[3][3] =  emity * gamy;
    sigma[3][4] = 0.0;
    sigma[3][5] = 0.0;

    sigma[4][0] = 0.0;
    sigma[4][1] = 0.0;
    sigma[4][2] = 0.0;
    sigma[4][3] = 0.0;
    sigma[4][4] = 1e-9;
    sigma[4][5] = 0.0;

    sigma[5][0] = 0.0;
    sigma[5][1] = 0.0;
    sigma[5][2] = 0.0;
    sigma[5][3] = 0.0;
    sigma[5][4] = 0.0;
    sigma[5][5] = 1e-9;

    TDecompChol chol(sigma);
    chol.Decompose();          // Cholesky decomposition: sigma = L * L^T
    cholSigmaL = chol.GetU();  // Upper triangular in ROOT
    cholSigmaL.Transpose(cholSigmaL);            // Convert to lower triangular
}

void source_newgen_c_(double *whasou, int *particle_code, double *momentum_energy,
                      double *coordinate_x, double *coordinate_y, double *coordinate_z,
                      double *direction_cosx, double *direction_cosy, double *direction_cosz) {
#if DEBUG
    std::cout << "source_newgen_c> " << whasou[0] << std::endl;
#endif
    if (whasou[0] == 1) {
      source_newgen_twiss_c_(particle_code, momentum_energy,
                             coordinate_x, coordinate_y, coordinate_z,
                             direction_cosx, direction_cosy, direction_cosz);
    }
}

void source_newgen_twiss_c_(int *particle_code, double *momentum_energy,
                            double *coordinate_x, double *coordinate_y, double *coordinate_z,
                            double *direction_cosx, double *direction_cosy, double *direction_cosz) {
    double xdummy = 0.0;
    TVectorD z(6);
    for (int j = 0; j < 6; j++)
        // FLNRRN random number generate
        z[j] = flnrrn_(&xdummy);

    // Transform: x = mean + cholSigmaL * z
    z = mean + cholSigmaL * z;

    // Assign coordinates
    *coordinate_x = z[0]*100;
    *coordinate_y = z[2]*100;
    *coordinate_z = 0;

    // Assign direction cosines
    *direction_cosx = z[1];
    *direction_cosy = z[3];
    *direction_cosz = sqrt(1-pow(*direction_cosx,2)-pow(*direction_cosy,2));

    // If the energy has been set via SOURCE card
    if (mean[5] != 0) {
        *momentum_energy = z[5];
    }

#if DEBUG
    std::cout << "source_newgen_twiss_c> " << z[0] << " " << z[1] << " " << z[2] << " "
                                           << z[3] << " " << z[4] << " " << z[5] << std::endl;
#endif

}

