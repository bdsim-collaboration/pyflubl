#include <iostream>

extern "C" {
    void source_newgen_init_c_();
    void source_newgen_c_(int *particle_code);
}

void source_newgen_init_c_() {
    std::cout << "source_newgen_init_c> " << std::endl;
}

void source_newgen_c_(int *particle_code) {
    std::cout << "source_newgen_c> " << std::endl;

}