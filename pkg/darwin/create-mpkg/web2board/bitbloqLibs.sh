#!/bin/bash

userName=$( who | head -1| cut -d  " " -f 1) && sudo chown -R $userName ~/Documents/Arduino | echo 'Result:'$0