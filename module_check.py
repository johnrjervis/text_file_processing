"""
Example code for the text file processing (TFP) module. (November 2021.)

The basic procedure is:
- define a class that inherits from tfp.FileProcessor
- create an instance of tfp.FolderProcessor and pass the new subclass of FileProcessor as the ProcessObject argument

On initialisation, the FolderProcessor instance creates a FileProcessor object for every file in the input folder and calls that object's process_data() method.

Example 1 shows how the TFP module can be used to create one output file per input file.
All files in the 'data' folder are read as input (using the argument "infolder = 'data'" for the instance of tfp.FolderProcessor).
The process_data() method of this class is quite simple: it just appends a line of text to the end of the file via the add_final_line() method.
Because the generate_output_filename() method is overridden in this class, the file names in the output folder are different from those in the input folder.
(The default behaviour is for filenames to be the same in both folders.)
Note that unless the argument "overwrite = True" is supplied when instantiating tfp.FolderProcessor, existing files in the output folder will not be overwritten if the script is run again.
Because the 'outfolder' argument for the instance of tfp.FolderManager is set to 'example_output' the output files will be written to this folder when the code is run.

Example 2 shows how the module can be used to create a single summary file for a set of input files.
This is achieved by specifying the 'outfile' argument when creating an instance of tfp.FolderProcessor (in this case, its value is 'example_output/averages.csv').
The process_data() method of the CalculateAveragesFromCSV class is a bit more substantial in this example; it calls a couple of methods:
the first of these splits the input csv file into a list that contains one list for each column in the input file,
the second method calculates the average for each list of column values.

Example 3 shows how the module can be used to output text to the terminal via print commands.
This is useful for a quick summary of the input files.
In this case, the GrepData class uses tfp.FileProcessor's built-in grep_data() method to look for the string '#2' in the input files.
"""

# text_file_processing.py needs to be in the same folder as this file
import text_file_processing as tfp


# Example 1

class AppendAndRename(tfp.FileProcessor):
    """A class for renaming a batch of files"""
    def __init__(self, infolder, outfolder, filename, outfile, additional_args):
        super(AppendAndRename, self).__init__(infolder, outfolder, filename, outfile, additional_args)

    def process_data(self):
        """The function called by FolderManager"""
        inputdata = self.get_input_data()
        updateddata = self.add_final_line(inputdata)
        self.write_data_to_file(updateddata)

    def generate_output_filename(self):
        """Adds the string '-updated' to the end of the filename"""
        filename, extension = self.filename.split('.')
        return filename + '-updated.' + extension

    def add_final_line(self, dataset):
        """Adds a line of text to the input dataset (should be a list)"""
        finalline = 'This line was added by the AppendAndRename class'
        return dataset + [finalline]


example1 = tfp.FolderProcessor(infolder = 'data', outfolder = 'example_output', ProcessObject = AppendAndRename, overwrite = True)


# Example 2

class CalculateAveragesFromCSV(tfp.FileProcessor):
    """A class for calculating column averages from CSV data"""
    def __init__(self, infolder, outfolder, filename, outfile, additional_args):
        super(CalculateAveragesFromCSV, self).__init__(infolder, outfolder, filename, outfile, additional_args)

    def process_data(self):
        """The function called by FolderManager"""
        inputdata = self.get_input_data()
        ordereddata = self.group_csv_data(inputdata)
        averages = self.calculate_csv_averages(ordereddata)
        self.write_data_to_file(averages)

    def group_csv_data(self, dataset):
        result = []
        for line in dataset:
            data = line.split(',')
            for i in range(len(data)):
                try:
                    result[i].append(data[i])
                except IndexError:
                    result.append([data[i]])
                    assert result[i][-1] == data[i]
        #print(result)
        return result

    def calculate_csv_averages(self, dataset):
        result = 'Averages for {0},'.format(self.filename)
        for subdataset in dataset:
            total = 0
            count = 0
            for value in subdataset:
                try:
                    total += float(value.strip())
                    count +=1
                except ValueError:
                    pass
            result += str(total / count) + ',' if count else 'NaN,'
        # Strip out the trailing comma and end the line with a newline character
        result = result[:-1] + '\n'
        return result


example2 = tfp.FolderProcessor(infolder = 'data', ProcessObject = CalculateAveragesFromCSV, outfile = 'example_output/averages.csv')


# Example 3

class GrepData(tfp.FileProcessor):
    """A class for finding strings in the input files"""
    def __init__(self, infolder, outfolder, filename, outfile, additional_args):
        super(GrepData, self).__init__(infolder, outfolder, filename, outfile, additional_args)

    def process_data(self):
        inputdata = self.get_input_data()
        self.grep_string('#2', inputdata)


example3 = tfp.FolderProcessor(infolder = 'data', ProcessObject = GrepData, verbose = False)

