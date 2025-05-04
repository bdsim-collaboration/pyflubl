from pyg4ometry.fluka.card import Card as _Card
from ._BaseCard import BaseCard as _BaseCard

class Usrbin(_BaseCard):
    '''Boundary crossing fluence or current estimator'''

    CARTESIAN = 0
    CYLINDRICAL = 1
    REGION = 2
    CARTESIAN_XSYM = 3
    CARTESIAN_YSYM = 4
    CARTESIAN_ZSYM = 5
    CARTESIAN_XYZSYM = 6
    CYLINDRICAL_ZSYM = 7
    SPECIAL = 8

    CARTESIAN_STEP = 10
    CYLINDRICAL_STEP = 11
    REGION_STEP = 12
    CARTESIAN_XSYM_STEP = 13
    CARTESIAN_YSYM_STEP = 14
    CARTESIAN_ZSYM_STEP = 15
    CARTESIAN_XYZSYM_STEP = 16
    CYLINDRICAL_ZSYM_STEP = 17
    SPECIAL_STEP = 18

    gen_part = {"ALL-PART":201,
                "ALL-CHAR":202,
                "ALL-NEUT":203,
                "ALL-NEGA":204,
                "ALL-POSI":205,
                "NUCLEONS":206,
                "NUC&PI+-":207,
                "ENERGY":208,
                "PIONS+-":209,
                "BEAMPART":210,
                "EM-ENRGY":211,
                "MUONS":212,
                "E+&E-":213,
                "AP&AN":214,
                "KAONS":215,
                "STRANGE":216,
                "KAONS+-":217,
                "HAD-CHAR":218,
                "FISSIONS":219,
                "HE-FISS":220,
                "LE-FISS":221,
                "NEU-BALA":222,
                "HAD-NEUT":223,
                "KAONS0":224,
                "C-MESONS":225,
                "C-(A)BAR":226,
                "CHARMED":227,
                "DOSE":228,
                "UNB-ENER":229,
                "UNB-EMEN":230,
                "X-MOMENT":231,
                "Y-MOMENT":232,
                "Z-MOMENT":233,
                "ACTIVITY":234,
                "ACTOMASS":235,
                "SI1MEVNE":236,
                "HADGT20M":237,
                "NIEL-DEP":238,
                "DPA-SCO":239,
                "DOSE-EQ":240,
                "DOSE-EM":241,
                "NET-CHRG":242,
                "DOSEQLET":243,
                "RES-NIEL":244,
                "DPA-NRT":245,
                "LOWENNEU":246,
                "NTLOWENE":247,
                "ALL-IONS":248,
                "HEHAD-EQ":249,
                "THNEU-EQ":250,
                "RES-NUCL":251,
                "DOSE-H2O":252,
                "ALPHA-D":253,
                "SQBETA-D":254,
                "LGH-IONS":255,
                "HVY-IONS":256,
                "E+E-GAMM":257,
                "ANNIHRST":258,
                "ARC-DPA":259}

    def __init__(self,
                 binning=None, # what(1)
                 particle=None, #what(2)
                 lun=None, # what(3)
                 xmax=100, # what(4)
                 rmax=100, # what(4)
                 ymax=100, # what(5)
                 zmax=100, # what(6)
                 sdum = "",
                 xmin=-100, # cc what(1)
                 rmin=0,    # cc what(1)
                 ymin=-100, # cc what(2)
                 zmin=-100, # cc what(3)
                 nxbin=20,  # cc what(4)
                 nybin=20,  # cc what(5)
                 nzbin=20): # cc what(6)

        super().__init__()

        if binning == self.CARTESIAN or binning == self.CARTESIAN_STEP :
            self.card = _Card("USRBIN",
                              binning, particle, lun,
                              xmax, ymax, zmax, sdum)

            self.cardCont1 = _Card("USRBIN",
                                   xmin, ymin, zmin,
                                   nxbin, nybin, nzbin,
                                   "&")