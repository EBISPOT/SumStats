# Summary Statistics Formatter

A general purpose formatter for summary statistics raw files.

The sum stats formatter's goal is to give a common format to the raw summary statistics file of interest.

It reads the header file and takes a first guess at what each column is. If you look into the [utils file]() you can see 
the guesses that it will make and the format we want to give to the sum stats file.

# Installation
- Clone the repository
- cd sum-stats-formatter
- pip install .

This will install the formatter on your python path and you should be able to use the scripts via command line.

# Available commands

You can see all available actions by typing:

`$ help-ss`

on your terminal. It will show you the range of commands you can execute on the file and some information about each one.

The actions you can perform (on a summary statistics file, i.e. csv, tsv, or other) are:

- `$ peek -f <filename>` 
   - will give you a peak into the file of interest displaying it's header and the first row of data
- `$ valid-headers` 
   -  will print a list of all known valid headers for inspiration
- `$ format -f <filename>` 
   - will try to automatically format the file
   - the new formatted file will by named `formatted_<filename>.tsv` and it will be created under the working directory
- `$ rename -f <filename>' -old <old name> -new <new name>` 
   - will rename the header given in the paramater '-old' to the header in the parameter '-new'
- `$ merge -f <filename>' : -left <first header> -right <second header> -d <delimiter> -new <new header>` 
   - will merge the columns of left header and right header into one column using the delimiter provided, 
   the new column header will be the one specified with the parameter '-new'
- `$ clean -f <filename>' : -header <header> -fixture <fixture>` 
   - will remove the sequence given as a fixture from the data in the column specified 
- `$ split -f <filename>' -header <header> -left <left header> -right <right header> -d <delimiter>` 
   - will split the column specified in '-header' using the delimiter provided
   - the split columns will be renamed using the parameters '-left' for the value on the left (after the split), 
   and '-right' for the value on the right (after the split)
- `$ swap -f <filename>' -left <left header> -right <right header>` 
   - will swap the data of left header and right header
- `$ compress -f <filename>'` 
   - will compress the file into a .tar.gz archive 
   
You can type `$ <command> -h` to get the argument explanation for each command. E.g.: `$ merge -h`

With this suite of commands you can semi-automate the formatting and then go in and perform any other 
renaming/merging/swapping/cleaning/splitting on the data columns.

NOTE: You will usually want to use the original file and first format the raw data, and then for any other commands that you will use,
you will provide as input (-f <filename>) the generated formatted file, named: `formatted_<filename>.tsv`.
   
