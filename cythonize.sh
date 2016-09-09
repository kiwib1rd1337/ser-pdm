#!/bin/bash
echo "Cleaning up previous compilation, if it exists..."
rm ./serpdm.c
rm ./serpdm
echo "Cythonizing ser-pdm.py..."
cython --embed -o serpdm.c ./serpdm.py
echo "DONE. Now attempting to compile serpdm.c"
gcc -Os -I /usr/include/python2.7 -o serpdm serpdm.c -lpython2.7 -lpthread -lm -lutil -ldl
echo "all done! Now try executing ./serpdm . It SHOULD be faster!"
