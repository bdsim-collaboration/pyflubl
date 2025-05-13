#include <fstream>
#include <iostream>
#include "global_cxx.h"

extern "C" {
    void mgdraw_bxdraw_c_(int *mreg, int *newreg, double *x, double *y, double *z);
}

void mgdraw_bxdraw_c_(int *mreg, int *newreg, double *x, double *y, double *z) {
    std::cout << "mgdraw_bxdraw_c_> " << *mreg << " " << *newreg << " " << *x << " " << *y << " " << *z << std::endl;
    samplers[0]->Fill(0,*x, *y, *z,0, 0, 0, 0, 0);
}