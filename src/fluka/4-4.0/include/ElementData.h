#include "TVectorD.h"
#include "TMatrixD.h"

class ElementData {
    public:

        ElementData() {}

        ElementData(std::string name) {}

        ElementData(std::string nameIn, double SIn,
                    double x, double y, double z,
                    double m11, double m12, double m13,
                    double m21, double m22, double m23,
                    double m31, double m32, double m33) {
            name = nameIn;
            S = SIn*100; // S in meters so multiply 100 to cm
            matrix(0,0) = m11;
            matrix(0,1) = m12;
            matrix(0,2) = m13;
            matrix(1,0) = m21;
            matrix(1,1) = m22;
            matrix(1,2) = m23;
            matrix(2,0) = m31;
            matrix(2,1) = m32;
            matrix(2,2) = m33;

            translation(0) = x/10; // x,y,z in mm so divide 10 to cm
            translation(1) = y/10;
            translation(2) = z/10;

            matrix_inv = matrix;
            matrix.Invert();
        }
        ~ElementData() {}

        void print() {
        }

        void transform(double X, double Y, double Z,
                       double &x, double &y, double &z) {
            TVectorD pos = TVectorD(3);
            pos(0) = X;
            pos(1) = Y;
            pos(2) = Z;

            TVectorD posprime = matrix * (pos-translation);
            x = posprime(0);
            y = posprime(1);
            z = posprime(2);
        }

        void transformDirection(double x, double y, double z,
                                double &xp, double &yp, double &zp) {
            TVectorD dir = TVectorD(3);
            dir(0) = x;
            dir(1) = y;
            dir(2) = z;

            TVectorD posprime = matrix * dir;
            xp = posprime(0);
            yp = posprime(1);
            zp = posprime(2);
        }

        double transformS(double X, double Y, double Z) {
            double x,y,z;
            transform(X,Y,Z,x,y,z);
            return S+z;
        }

        std::string name;
        double S;
        TVectorD translation = TVectorD(3);
        TMatrixD matrix = TMatrixD(3,3);
        TMatrixD matrix_inv = TMatrixD(3,3);

};