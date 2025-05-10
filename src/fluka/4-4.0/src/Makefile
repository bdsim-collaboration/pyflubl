FLUKA_ROOT_PATH=/tmp/fluka4-4.0/
FLUKA_BIN=$(FLUKA_ROOT_PATH)/bin

FFF=$(FLUKA_BIN)/fff
LFLUKA=$(FLUKA_BIN)/lfluka
CXX=g++
RM=rm

%.o : %.cxx
	$(CXX) -c $<

%.o : %.f
	$(FFF) $<

fluka: usrini.o usrini_c.o source.o mgdraw.o
	$(LFLUKA) -m fluka usrini.o usrini_c.o source.o mgdraw.o

clean:
	$(RM) -rf *.o fluka