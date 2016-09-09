#!/bin/bash

# Check if running as root, otherwise exit 1
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

echo "Removing files from /usr/local/bin"
echo ""

rm /usr/local/bin/serpdm.py
rm /usr/local/bin/serpdm

echo ""
echo "Please ignore the errors above, this very basic uninstall script should work regardless."
echo ""
echo "all done! Now ser-pdm.py should be removed from the system!"
