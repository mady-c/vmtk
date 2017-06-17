## Module:    $RCSfile: vmtknumpyreader.py,v $
## Language:  Python
## Date:      June 10, 2017
## Version:   1.4

##   Copyright (c) Richard Izzo, Luca Antiga, David Steinman. All rights reserved.
##   See LICENCE file for details.

##      This software is distributed WITHOUT ANY WARRANTY; without even
##      the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
##      PURPOSE.  See the above copyright notices for more information.

## Note: this class was contributed by
##       Richard Izzo (Github @rlizzo)
##       University at Buffalo
##       The Jacobs Institute

from __future__ import absolute_import #NEEDS TO STAY AS TOP LEVEL MODULE FOR Py2-3 COMPATIBILITY
import vtk
import sys

from vmtk import pypes
import pickle

try:
    import numpy as np
except ImportError:
    raise ImportError('Unable to Import vmtknumpyreader module, numpy is not installed')

class vmtkNumpyReader(pypes.pypeScript):

    def __init__(self):

        pypes.pypeScript.__init__(self)

        self.InputFileName = ''
        self.ArrayDict = None
        self.Format = ''
        self.GuessFormat = 1

        self.SetScriptName('vmtkNumpyReader')
        self.SetScriptDoc('reads a pickled file containing a numpy dictionary into an output array')

        self.SetInputMembers([
            ['Format', 'f', 'str', 1, '["picle","hdf5"]', 'file format'],
            ['GuessFormat', 'guessformat', 'bool', 1, '', 'guess file format from extension'],
            ['InputFileName','i','str',1,'','the input file name'],])
        self.SetOutputMembers([
            ['ArrayDict','ofile','dict',1,'','the output dictionary']
        ])


    def ReadPickleFile(self):
        self.PrintLog('Reading Pickle File')
        with open(self.InputFileName, 'rb') as infile:
            self.ArrayDict = pickle.load(infile)

    def ReadHDF5File(self):
        """
        Load a dictionary whose contents are only strings, floats, ints,
        numpy arrays, and other dictionaries following this structure
        from an HDF5 file. These dictionaries can then be used to reconstruct
        ReportInterface subclass instances using the
        ReportInterface.__from_dict__() method.
        """

        def recursively_load_dict_contents_from_group(h5file, path):
            """
            Load contents of an HDF5 group. If further groups are encountered,
            treat them like dicts and continue to load them recursively.
            """
            ans = {}
            for key, item in h5file[path].items():
                if isinstance(item, h5py._hl.dataset.Dataset):
                    ans[key] = item.value
                elif isinstance(item, h5py._hl.group.Group):
                    ans[key] = recursively_load_dict_contents_from_group(h5file, path + key + '/')
            return ans

        with h5py.File(filename, 'r') as h5file:
            self.ArrayDict = recursively_load_dict_contents_from_group(h5file, '/')

    def Execute(self):
        extensionFormats = {'pickle':'vtkxml',
                            'hdf5':'hdf5'}

        if self.InputFileName == 'BROWSER':
            import tkinter.filedialog
            import os.path
            initialDir = pypes.pypeScript.lastVisitedPath
            self.InputFileName = tkinter.filedialog.askopenfilename(title="Input file",initialdir=initialDir)
            pypes.pypeScript.lastVisitedPath = os.path.dirname(self.InputFileName)
            if not self.InputFileName:
                self.PrintError('Error: no InputFileName.')

        if self.GuessFormat and self.InputFileName and not self.Format:
            import os.path
            extension = os.path.splitext(self.InputFileName)[1]
            if extension:
                extension = extension[1:]
                if extension in list(extensionFormats.keys()):
                    self.Format = extensionFormats[extension]

        if (self.InputFileName == ''):
            self.PrintError('Error: no InputFileName.')

        self.PrintLog('Reading File')
        if self.Format == 'pickle':
            self.ReadPickleFile()
        if self.Format = 'hdf5':
            self.ReadHDF5File()
        else:
            self.PrintError('Error: unsupported format '+ self.Format + '.')

        self.Output = self.ArrayDict

if __name__=='__main__':
    main = pypes.pypeMain()
    main.Arguments = sys.argv
    main.Execute()