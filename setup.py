# -*- coding: UTF-8 -*-
from distutils.core import setup
import py2exe,sys

from glob import glob 

if "designer" in sys.argv:
    name="mse_designer"
    scripts=['designer.py']
    dist_dir="MSEDESIGNER_DST"
    sys.argv.remove('designer')
else:
    name="bgm"
    scripts=['bgm.py']
    dist_dir="BGM_DST"

if __name__=='__main__':

    if 'py2exe' not in sys.argv: 
        sys.argv.append('py2exe')
        
setup(
    name=name,
    scripts=scripts,
    options={
        "py2exe":
                {
                    "dist_dir":
                            dist_dir,
                            "compressed": 0, 
                                "optimize":2
                }
    },
    
    data_files=[('img',[i for i in glob('img/*')]),
        ('.',['bgm.ini',]), 
        ('.',['blank.PNG',]), 
        #~ ('.',['DL.png',]), 
        #~ ('.',['docs.png',]), 
    ],
    windows=[
        {	
            "script":scripts[0],
            "icon_resources": [(1, "img/favicon.ico")],

        }
    ],
)

import shutil 
shutil.rmtree('build')