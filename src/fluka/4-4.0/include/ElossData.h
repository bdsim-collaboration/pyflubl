#define NELOSSMAX 20000
class ElossData {
    public:
        ElossData() {}
        ~ElossData() {}

        void SetBranchAddresses(TTree *t) {
            std::string elossName = "eloss";
            t->Branch((elossName+".n").c_str(), &n,"n/I");
            t->Branch((elossName+".E").c_str(), E ,"E[n]/D");
            t->Branch((elossName+".S").c_str(), S, "S[n]/D");
        }

        void Flush() {
            n = 0;
        }

        void Fill(double EIn, double SIn) {
            E[n] = EIn;
            S[n] = SIn;

            n++;
        }


        int n;
        double E[NELOSSMAX];
        double S[NELOSSMAX];

};