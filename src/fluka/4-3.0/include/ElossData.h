
class ElossData {
    public:
        ElossData() {
            n = 0;
        }
        ~ElossData() {}

        void SetBranchAddresses(TTree *t) {
            std::string elossName = "eloss";
            t->Branch((elossName+".n").c_str(), &n,"n/I");
            t->Branch((elossName+".E").c_str(), &E);
            t->Branch((elossName+".S").c_str(), &S);
        }

        void Flush() {
            n = 0;
            E.clear();
            S.clear();
        }

        void Fill(double EIn, double SIn) {
            E.push_back(EIn);
            S.push_back(SIn);

            n++;
        }

        int n;
        std::vector<double> E;
        std::vector<double> S;
};