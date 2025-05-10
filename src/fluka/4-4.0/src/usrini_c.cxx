#include <iostream>

extern "C" {
    void usrini_c_();  // Fortran 77 adds underscore
}

void usrini_c_() {
    std::cout << "usrini_c_" << std::endl;
}