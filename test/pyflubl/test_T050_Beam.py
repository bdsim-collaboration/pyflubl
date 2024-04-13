import pyflubl as _pfbl

def test_T050_Beam():

    b = _pfbl.Beam(10, 0.01)
    b.AddBeamPosition(1, 2, 3, 4, 5, 6)
    b.AddBeamPositionDSUMSPHEVOL(8,9)
    b.AddBeamAxes(10,11,12,13,14,15)
    assert(str(b) == 'BEAM, 10.0, 0.01, 0.0, 0.0, 0.0, 0.0, \nBEAMPOS, 1.0, 2.0, 3.0, 4.0, 5.0, , 6.0\nBEAMPOS, 8.0, 9.0, , , , , SPHE-VOL\nBEAMAXES, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, ')

    b = _pfbl.Beam(10, 0.01)
    b.AddBeamPosition(1, 2, 3, 4, 5, 6)
    b.AddBeamPositionDSUMCYLIVOL(7,8,9,10)
    b.AddBeamAxes(20,21,22,23,24,25)
    assert(str(b) == 'BEAM, 10.0, 0.01, 0.0, 0.0, 0.0, 0.0, \nBEAMPOS, 1.0, 2.0, 3.0, 4.0, 5.0, , 6.0\nBEAMPOS, 7.0, 8.0, 9.0, 10.0, , , CYLI-VOL\nBEAMAXES, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0, ')

    b = _pfbl.Beam(10, 0.01)
    b.AddBeamPosition(1, 2, 3, 4, 5, 6)
    b.AddBeamPositionDSUMCARTVOL(7,8,9,10,11,12)
    b.AddBeamAxes(20,21,22,23,24,25)
    assert(str(b) == 'BEAM, 10.0, 0.01, 0.0, 0.0, 0.0, 0.0, \nBEAMPOS, 1.0, 2.0, 3.0, 4.0, 5.0, , 6.0\nBEAMPOS, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, CART-VOL\nBEAMAXES, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0, ')

    b = _pfbl.Beam(10, 0.01)
    b.AddBeamPosition(1, 2, 3, 4, 5, 6)
    b.AddBeamPositionDSUMFLOOD(10)
    b.AddBeamAxes(10,11,12,13,14,15)
    assert(str(b) == 'BEAM, 10.0, 0.01, 0.0, 0.0, 0.0, 0.0, \nBEAMPOS, 1.0, 2.0, 3.0, 4.0, 5.0, , 6.0\nBEAMPOS, 10.0, , , , , , FLOOD\nBEAMAXES, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, ')

