# v4.0 (Nov 2021) Added a method for changing the filenames.
# v4.1 (Nov 2021) Added check to see whether outfolder exists to prevent terminal output being blocked if overwrite does not exist.
# v4.2 (Nov 2021) Added a dataset argunment to InOut.write_data_to_file()
# v4.3 (Nov 2021) Generate objects now compares the output filename against the list of files to not to overwrite
#                 Otherwise, overwrite mode does not work if InOut.generate_output_filename() is overridden
# v4.4 (Nov 2021) Added the grep_string() method to FileProcessor to add grep-like functionality

# The processing function should be a subclass of InOut and should have a process_data function
# This function can either output text to the terminal (e.g. file-checking)
# Alternatively, it can process the input files and either output a single summary file or one processed file per input file

# Remember that module names cannot include dashes! (Use underscores instead.)


import os

class FileProcessor(object):
    """Defines the input and output information for data processing subclasses"""
    def __init__(self, infolder, outfolder, filename, outfile, additional_args):
        self.inpath = infolder + '/' + filename
        self.outfolder = outfolder
        self.filename = filename
        self.outfile = outfile
        self.additional_args = additional_args
        self.statusverbose = None

    def get_input_data(self):
        """Opens the infile and returns a list of its lines (works for python 2.x)"""
        filedata = open(self.inpath, 'r')
        result = filedata.readlines()
        filedata.close()
        return result

    def write_data_to_file(self, dataset):
        """Opens the outfile and writes the contents of dataset to the file (works for python 2.x)"""
        if self.outfile:
            # Case for a single summary file, so need to append data
            outtarget = open(self.outfile, 'a')
        else:
            # One file for each input file, so use write mode
            outputfilepath = self.outfolder + '/' + self.generate_output_filename()
            outtarget = open(outputfilepath, 'w')
        for line in dataset:
            outtarget.write(line)
        # Close the file in either case: data will be appended if it's a summary file
        outtarget.close()

    def process_data(self):
        """Prints the filename - this method should be overridden by the subclass"""
        # If self.get_input_data() is required call it here so that the file reading is performed inside FolderManager's try/except block
        # If writing data to one file for each input file, this method should populate a dataset (typically a list of strings) and then call self.write_data_to_file(dataset)
        # Alternatively, it can use print() to output text to the terminal
        print(self.filename)

    def generate_output_filename(self):
        """Does not change the filename"""
        # The subclass should override this method if the output filenames are to be different from the input filenames
        return self.filename

    def grep_string(self, string, dataset, printdata = True):
        """Searches for a string in the lines of a dataset, and prints or returns the results"""
        matches = []
        for i in range(len(dataset)):
            if string in dataset[i]:
                matches.append(i)
        if printdata:
            for match in matches:
                print('String "{0}" found on line {1} in file {2}: ("{3}")'.format(string, match + 1, self.filename, dataset[match].strip('\n')))
        else:
            # Add the filename so that it is clear which file the matches were found in
            result = [self.filename] + matches
            return result

class FolderProcessor(object):
    """Runs an object's process_data function on all files in a folder"""
    def __init__(self, infolder = "input", outfolder = "output", ProcessObject = FileProcessor, verbose = True, outfile = None, overwrite = False, **additional_args):
        # Default behaviour is each file in ./input is processed with the ProcessObject and the results are saved in a file (with the same name as the input file) in ./output
        self.infolder = infolder
        self.outfolder = outfolder
        self.ProcessObject = ProcessObject
        # If verbose is true, commentary is written to the terminal (see process_folder)
        self.verbose = verbose
        # Outfile will be used to create a single summary file if this value is supplied (see InOut.write_data_to_file)
        self.outfile = outfile
        if self.outfile:
            # Add a header in write mode now to overwrite any previous files
            fileObj = open(outfile, 'w')
            fileObj.write('Summary of results:\n\n')
            # Close now: InOut will append data
            fileObj.close()
        self.overwrite = overwrite
        # It is left to subclasses of InOut to test for additional args and use as required
        self.additional_args = additional_args
        # If called without any arguments, this class will list the files in "./input"
        self.fileslist = os.listdir(infolder)
        # Sort the list of input files - otherwise this will be in a random order
        self.fileslist.sort()
        self.objectlist = self.generate_objects()
        self.process_folder()

    def generate_objects(self):
        """Generates a data processing object for each file in the infolder"""
        result = []
        # Create a list of files not to overwrite (not relevant if writing to a summary file)
        # For output to terminal mode, the outfolder will likely not exist - don't want an OSError to halt the script
        try:
            os.listdir(self.outfolder)
            isoutfolder = True
        except OSError:
            isoutfolder = False
        #print('{0}, {1}, {2}'.format(not self.overwrite, not self.outfile, isoutfolder))
        if ((not self.overwrite) and (not self.outfile) and (isoutfolder)):
            preservelist = os.listdir(self.outfolder)
            #print(preservelist)
        else:
            preservelist = []
        for eachfile in self.fileslist:
            newProcessObject = self.ProcessObject(self.infolder, self.outfolder, eachfile, self.outfile, self.additional_args)
            # Need to check output filename (not input filename!) to see if the output file already exists
            outputfile = newProcessObject.generate_output_filename() 
            if outputfile in preservelist:
                print('Output already exists for {0} ... ignoring this file'.format(eachfile))
            else:
                result.append(newProcessObject)
        return result

    def process_folder(self):
        """Calls the process_data method for each of the data processing objects in self.objectlist"""
        for eachobject in self.objectlist:
            # Start by running the object's process_data function
            try:
                eachobject.process_data()
                if eachobject.statusverbose:
                    comment = eachobject.statusverbose
                else:
                    # If the processing object has no comment attribute, verbose mode just prints "Processed file ... filename ... OK"
                    comment = '\t... OK'
            except Exception as e:
                comment = '\t... FAILED: {0} [{1}]'.format(e, e.__class__)               
            # default is self.verbose = True
            if self.verbose:
                print('Processing file ... {0} {1}'.format(eachobject.filename, comment))
        if self.verbose:
            print(' ')

