"""Handle Package Management
A packqage is a zip file made of:
- a template file, which is a pickle dict a widget element
- a script file, python script modifying template elemnets behaviour
- an optionnal image file, displayed when browsing through the package
"""

import wx,widgets,os
from contextlib import closing
from zipfile import ZipFile, ZIP_DEFLATED


def zipdir(basedir, archivename):
    assert os.path.isdir(basedir)
    with closing(ZipFile(archivename, "w", ZIP_DEFLATED)) as z:
        for root, dirs, files in os.walk(basedir):
            #NOTE: ignore empty directories
            for fn in files:
                absfn = os.path.join(root, fn)
                zfn = absfn[len(basedir)+len(os.sep):] #XXX: relative path
                z.write(absfn, zfn)

class Package:
    def __init__(self,filename):
        self.filename=filename
        names=ZipFile(filename).namelist()
        if 'template.tmpl' not in names:
            raise ValueError('Empty or Malformed Package:%s'%filename)
        
    def _gettemplate(self):
        return ZipFile(self.filename).open('template.tmpl')

    template=property(_gettemplate)
    
    def _getscript(self):
        try:
            return ZipFile(self.filename).open('script.py')
        except KeyError:
            return None    

    script=property(_getscript)
    
    def _geticon(self):
        try:
            return ZipFile(self.filename).open('icon.jpg')
        except KeyError:
            return None

    icon=property(_geticon)
    
    
    @classmethod
    def fromFolder(klass,folderName,archname):
        #Create a zip
        zipdir(folderName,archname)
        #Return a package
        return klass(archname)
        
        
    
        
        
        
        