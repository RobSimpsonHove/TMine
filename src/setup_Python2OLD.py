
# This runs with argument py2exe, and builds a dist folder
# First: delete dist/ & build/
# Then run this > python setup.py py2exe

from distutils.core import setup
import py2exe

setup(console=['Tmine37_Python2OLD.py'])

# then you need to:

## Zip /dist and /utils to TM.zip

## Install instructions:
dummy='''
-	Download file
-	Unzip somewhere, it should create a folder called TMine37
-	Copy your kill list and save list to the TMine37/utils/ directory.
-	Copy the executable TMiner37.exe that is in the dist/ directory
-	Go to the directory you want the shortcut (desktop perhaps?)
-	Right click and paste 'shortcut'
-	Right-click the short-cut it to get 'properties'
-	Make sure that the 'Start In' directory is TMine35 (or whatever you named the unzipped directory)
'''