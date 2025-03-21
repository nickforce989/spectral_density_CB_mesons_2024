using Pkg
Pkg.activate(".")
Pkg.instantiate()

using HiRepParsing
using HDF5
using ArgParse

# This script parses the log files in the directory 'dir', and saves them as an hdf5-file
# in the location provided by 'h5file'.

# It creates a single hdf5 file for all log files. Measurements performed on the same ensemble
# are written in distinct hdf5 groups labelled  by the variable `ensemble`

s = ArgParseSettings()
@add_arg_table s begin
    "log_dir"
    help = "Directory containing log files"
    required = true
    "output_h5"
    help = "Where to write the resulting HDF5 file"
    required = true
end

parsed_args = parse_args(ARGS, s)

dir = expanduser(parsed_args["log_dir"])
h5file = expanduser(parsed_args["output_h5"])
use_regex_parsing = false

function main(dir, h5file)

    # I have defined a reference variable for the last saved ensemble.
    # If the ensemble changes, we save also information on the lattice setup (coupling, size, bare masses)
    # to the hdf5 file. This is controlled by the option 'setup', which writes the parameters to the file
    # if 'setup == true'
    ensemble0 = ""
    # (This is not very robust and depends o the naming scheme of the output files)

    # loop over all files in the directory
    for file in readdir(dir, join = true)

        # I am just making sure, that we only look at raw log files.
        # Any files that does not end with '.txt' is ignored
        endswith(file, ".txt") || continue

        # set up a regular expression, that matches the measurement type and the different smearing levels.
        # Note that the steps in the smearing levels are hard-coded
        name = first(splitext(basename(file)))
        types = ["TRIPLET"]

        # parse the ensemble name from the filename
        # (again this depends strongly on the naming scheme)
        # Check if we need to write the lattice-setupparameters to hdf5 file
        ensemble = replace(name, "out_corr" => "wall_corr")
        setup = ensemble != ensemble0
        ensemble0 = ensemble
        @show ensemble, setup

        #####################################################
        # Method A: Using a list of types                   #
        #####################################################
        ###################################################################################
        # Method B: Using a regular expression directly  (faster, but it uses more ram)   #
        ###################################################################################
        writehdf5_spectrum(
            file,
            h5file,
            types,
            mixed_rep = false;
            h5group = ensemble,
            setup,
        )


    end
end

main(dir, h5file)
