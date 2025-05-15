#include <vector>

#define NSAMPLERMAX 20000

class SamplerData {
    public :
        SamplerData() {
            n = 0;
            z = 0;
        }

        ~SamplerData() {}

        void SetBranchAddresses(TTree *t, std::string samplerName) {
            t->Branch((samplerName+".n").c_str(), &n,"n/I");
            t->Branch((samplerName+".energy").c_str(), &energy, "energy[n]/D");
            t->Branch((samplerName+".x").c_str(), x ,"x[n]/D");
            t->Branch((samplerName+".y").c_str(), y, "y[n]/D");
            t->Branch((samplerName+".z").c_str(), &z, "z/D");
            t->Branch((samplerName+".xp").c_str(), xp ,"x[n]/D");
            t->Branch((samplerName+".yp").c_str(), yp, "y[n]/D");
            t->Branch((samplerName+".zp").c_str(), zp, "z[n]/D");
        }

        void SetBranchAddresses1(TTree *t, std::string samplerName) {
            t->Branch(samplerName.c_str(), this, "n/I:energy[n]/D:x[n]/D:y[n]/D:z/D");
        }

        void Flush() {
            n = 0;
            z = 0;
        }

        void Fill(double energyIn, double xIn, double yIn, double zIn,
                  double xpIn, double ypIn, double zpIn, double pIn, double TIn) {
            if(n>=NSAMPLERMAX)
                return;

            energy[n] = energyIn;
            x[n] = xIn;
            y[n] = yIn;
            z = zIn;
            xp[n] = xpIn;
            yp[n] = ypIn;
            zp[n] = zpIn;
            p[n] = pIn;
            T[n] = TIn;

            n++;
        }

        int n;

        double energy[NSAMPLERMAX];

        double x[NSAMPLERMAX];
        double y[NSAMPLERMAX];
        double z;

        double xp[NSAMPLERMAX];
        double yp[NSAMPLERMAX];
        double zp[NSAMPLERMAX];

        double p[NSAMPLERMAX];
        double T[NSAMPLERMAX];

        int   partID[NSAMPLERMAX];
};