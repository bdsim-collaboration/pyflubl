FLUKA_ROOT_PATH=/tmp/fluka4-4.0/
FLUKA_BIN=$(FLUKA_ROOT_PATH)/bin

FFF=$(FLUKA_BIN)/fff
LFLUKA=$(FLUKA_BIN)/lfluka
CXX=g++
RM=rm
ROOT_LIB = "-L/tmp/root/lib -lCore -lImt -lRIO -lNet -lHist -lGraf -lGraf3d -lGpad -lROOTVecOps -lTree -lTreePlayer -lRint -lPostscript -lMatrix -lPhysics -lMathCore -lThread -lMultiProc -lROOTDataFrame"
ROOT_INC := $(shell root-config --cflags)

%.o : %.cxx
	$(CXX) -I../include $(ROOT_INC) -c $<

%.o : %.f
	$(FFF) $<

fluka: usrini.o usrini_c.o source.o mgdraw.o mgdraw_bxdraw_c.o usreou.o usreou_c.o usrout.o usrout_c.o
	$(LFLUKA) $(ROOT_LIB) -m fluka usrini.o usrini_c.o source.o mgdraw.o mgdraw_bxdraw_c.o usreou.o usreou_c.o usrout.o usrout_c.o

clean:
	$(RM) -rf *.o fluka