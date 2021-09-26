#!/bin/bash

NEUTRON_SOLARIS_DIR=$DEST/neutron-solaris

if [[ "$1" == "stack" && "$2" == "install" ]]; then
    cd $NEUTRON_SOLARIS_DIR
    echo "Installing neutron-solaris."
    setup_develop $NEUTRON_SOLARIS_DIR

    echo "Successfully installed neutron-solaris."
fi
