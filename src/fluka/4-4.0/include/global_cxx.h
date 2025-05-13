#include "TFile.h"
#include "TTree.h"
#include "SamplerData.h"
#include <nlohmann/json.hpp>

using json = nlohmann::json;

// Global pointers
extern json *bookkeeping;

extern TFile* outputFile;
extern TTree* eventTree;
extern SamplerData **samplers;

extern int iEvt;