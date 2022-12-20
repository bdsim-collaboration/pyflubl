#!/bin/sh

flukaTar=$1
osType=$2

scriptDir=`pwd`
flukaPath=`tar tf $flukaTar | head -1 | tr "/" \ \  | awk '{ printf "%s", $1}'`

echo $flukaTar $osType $flukaPath $pwd

tar xf $flukaTar
rm -rf $flukaPath-$osType
cp -r $flukaPath $flukaPath-$osType

make -c $flukaPath-$osType/src

cd $scriptPath/$flukaPath/bin
fff ../../mgdraw.f
fff ../../magfld.f
fff ../../source.f
lfluka -o fluka -m fluka ../../mgdraw.o ../../magfld.o ../../source.o

rm -rf  $scriptPath/*.o
