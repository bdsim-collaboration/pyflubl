      SUBROUTINE USROUT ()

      WRITE(*,*) "PYFLUBL-USROUT>"

* Call C/C++ function
      call usrout_c()

      RETURN
      END