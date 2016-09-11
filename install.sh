#!/bin/bash

# Check if running as root, otherwise exit 1
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

echo "Copying files to /usr/local/bin (replace original)..."
echo ""

rm /usr/local/bin/serpdm.py > /dev/null
rm /usr/local/bin/serpdm > /dev/null

cp ./serpdm.py /usr/local/bin/ > /dev/null
cp ./serpdm /usr/local/bin/ > /dev/null

chmod 755 /usr/local/bin/serpdm.py > /dev/null
chmod 755 /usr/local/bin/serpdm > /dev/null


chmod +x /usr/local/bin/serpdm.py > /dev/null
chmod +x /usr/local/bin/serpdm > /dev/null

echo ""
echo "Please ignore the errors above, this very basic install script should work regardless."
echo ""
echo "If you ran ./cythonize.sh successfully, you should be able to run ser-pdm without the .py ! Otherwise, you can attempt it again, and re-run this install script."
echo ""
echo "all done! Now ser-pdm.py should be available system wide!"

