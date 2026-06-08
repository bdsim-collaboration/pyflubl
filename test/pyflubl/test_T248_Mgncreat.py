import pyflubl
import numpy as np
import os as _os

def test_T248_Mgncreat_mgndata() :
    this_dir = _os.path.dirname(_os.path.abspath(__file__))

    x = np.array([-10, 10, -10, 10])
    y = np.array([-10,-10,  10, 10])
    Bx = np.array([-1, -1, 1, 1 ])
    By = np.array([-1, 1, -1, 1])
    Bz = np.array([0,0,0,0])

    x = x.reshape((2,2))
    y = y.reshape((2,2))
    Bx = Bx.reshape((2,2))
    By = By.reshape((2,2))
    Bz = Bz.reshape((2,2))

    print(np.stack([x, y, Bx, By, Bz]).transpose().shape)

    fluka_field = pyflubl.Field.Field2D(np.stack([x, y, Bx, By, Bz]).transpose(), name="plasma")

    fluka_field.Resample(10,10, method='linear')
    fluka_field.MakeCards()
    fluka_field.Write(this_dir + "/" + "T248_Mgncreat_mgndata.inp")
    fluka_field.Plot()