# Updating the MDP model
The model processing pipeline is unfortunately somewhat convoluted at the moment, but once you know the order to run the scripts in, and which files to change it's not too complicated. The server does not accept a normal prism file with hardcoded values as an input. Instead, your prism file must first be converted to an annotated template, so that the starting values, provided by the user through the interface, may be inserted.

## Generating a template
The prism file must first be transformed by the provided scripts `convert.py` and `strat_generator.py` before it is ready to be used by the server. Keep in mind that your prism file must also include annotations, in the form of comments, that tell the scripts where to make their changes (these annotations are described [further down](#a-note-on-the-templating-syntax)).

When the prism file has been properly annotated, run the script  `convert.py`. You will be met by the following prompt,

`Model file to convert to template:`

Simply input the name of `yourfile.pm` and press the enter key. This script will create (or overwrite if it already exists) a file called `generated.pm`. This is a template file generated from your original prism file, which has been modified so that it can accept the input given by the user through the interface. However, before it can be used, it must go through another transformation which creates the DTMC files for the various strategies defined in `strategy.json`. 

To do this, you simply run another script, called `strat_generator.py`. Follow the instructions using the file `generated.pm` instead of your original prism file. When it has finished, this script should have created a corresponding `dtmc_strategy_name.pm` file for each strategy.

### Success
At this point, you should be done, with the model files successfully updated! As long as the names of all your strategies have been added to the list of available strategies found in the `main.js` server, the generated files should be automatically recognized. The `generated.pm` file, is no longer necessary and may be deleted, but the new DTMC files must be left untouched.

### A note on the templating syntax
In order for your prism file to be transformed by the provided scripts, it must be annotated with comments following a simple syntax that shows where insertions should be made.

For instance, there might be a line in the car module which looks like this: 

`car_v : [0..max_speed] init 0;`

This line sets the cars initial velocity to a hardcoded value, which is useful for testing purposes, but as this is a value that can be changed in the interface it must be replaced in the template. So that `convert.py` knows to make this change, and what to change it too, you would append a comment to the end of the line: 

`car_v : [0..max_speed] init 0; // {car_v}`

This comment should follow the format: `// {variable_name}`. In this case, the hardcoded value will be replaced by the given variable, resulting in a line that looks like this:

`car_v : [0..max_speed] init {car_v};`

The possible variable names are: 

`person_x, person_y, car_x, car_y, top_corner_x, top_corner_y,  bottom_corner_x, bottom_corner_y`

The `convert.py` script has support for replacing values in both `init` and `=` assignment statements.

## Future improvements

Much could be done to improve the template generation workflow. Some ideas follow:

- connect the `convert.py` and `stat_generator.py` scripts together/combine them
- make scripts take command line arguments instead of reading from standard input (would help with auto-completing file names)
    - alternatively, make them read from standardized file locations