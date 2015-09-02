#!/bin/bash

#Create route if it does not exist previously
mkdir -p $HOME/Documents/Arduino/libraries/

#Remove previous bitbloqLibs library if it exists:
rm -rf $HOME/Documents/Arduino/libraries/bitbloqLibs

cd $HOME/Documents/Arduino/libraries/

#Download the new version:
curl -L "https://github.com/bq/bitbloqLibs/archive/v0.0.1.zip"  -o "v0.0.1.zip"
unzip v0.0.1.zip -d .
rm -rf v0.0.1.zip*
mv bitbloqLibs-0.0.1 bitbloqLibs