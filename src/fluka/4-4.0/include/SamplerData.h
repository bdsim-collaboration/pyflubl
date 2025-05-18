#include <vector>

class SamplerData {
    public :
        SamplerData() {
            n = 0;
            z = 0;
        }

        ~SamplerData() {}

        void SetBranchAddresses(TTree *t, std::string samplerName) {
            t->Branch((samplerName+".n").c_str(), &n,"n/I");
            t->Branch((samplerName+".energy").c_str(), &energy);
            t->Branch((samplerName+".x").c_str(), &x );
            t->Branch((samplerName+".y").c_str(), &y);
            t->Branch((samplerName+".z").c_str(), &z, "z/D");
            t->Branch((samplerName+".xp").c_str(), &xp);
            t->Branch((samplerName+".yp").c_str(), &yp);
            t->Branch((samplerName+".zp").c_str(), &zp);
            t->Branch((samplerName+".T").c_str(), &T);
            t->Branch((samplerName+".partID").c_str(), &partID);
        }

        void Flush() {
            n = 0;
            z = 0;

            energy.clear();
            x.clear();
            y.clear();
            xp.clear();
            yp.clear();
            zp.clear();
            T.clear();
            partID.clear();
        }

        void Fill(double energyIn, double xIn, double yIn, double zIn,
                  double xpIn, double ypIn, double zpIn, double TIn, int partIDIn) {

            energy.push_back(energyIn);
            x.push_back(xIn);
            y.push_back(yIn);
            z = zIn;
            xp.push_back(xpIn);
            yp.push_back(ypIn);
            zp.push_back(zpIn);
            T.push_back(TIn);
            partID.push_back(partIDIn);

            n++;
        }

        int n;

        std::vector<double> energy;

        std::vector<double> x;
        std::vector<double> y;
        double z;

        std::vector<double> xp;
        std::vector<double> yp;
        std::vector<double> zp;

        std::vector<double> T;

        std::vector<int>    partID;
};