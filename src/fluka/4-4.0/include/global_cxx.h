#include "TFile.h"
#include "TTree.h"
#include "ElementData.h"
#include "SamplerData.h"
#include "ELossData.h"
#include <nlohmann/json.hpp>

using json = nlohmann::json;

// Global pointers
extern json *bookkeeping;
extern std::map<std::string, ElementData> *elementMap;

extern TFile* outputFile;
extern TTree* eventTree;
extern SamplerData **samplers;
extern ElossData *eloss;

extern int iEvt;

// #define DEBUG 1