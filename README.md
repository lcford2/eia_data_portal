# EIA API Data Portal

This is a small project I started to help automate the process of pulling data from the EIA. 
The EIA provides a ton of useful information for energy systems modeling and other uses, and its web interface is actually really nice and intuitive. However, when you need a lot of data it can be cumbersome to navigate through their website to get all of the information you want. This project simply provides a easy method to do that. It is not perfect, but I use it all the time and you might find that it helps you too.

The hallmarks of this project are:
- Use of EIA's Data Access API
  - Requiring each user to have their own API key.
- Date parsing functionality that tries to convert the datetime strings provided by EIA to datetime objects
  - With the ability for users to add their own parsing formats easily
- Coercing raw data into pandas DataFrames and storing them as CSV files
- Storing meta data about the retrieved data series in `series_records.json` for reference

The first step after you clone this repository is to [request a API key from EIA](https://www.eia.gov/opendata/register.php). After you have your API key, create a file in this directory called `api_key.txt` that contains your API key in the first line and nothing else. 

After that, you can browse the `series_records.json` file for a data series you may be interested in or you can look through [EIA's data catalog](https://www.eia.gov/opendata/qb.php) for a more comprehensive list of possible data series. Once you have a series id you want to download (e.g. `EBA.CAL-ALL.NG.SUN.HL`, which is the Net Generation (NG) from Solar (SUN) at an hourly resolution in local time (HL) for all of California (CAL-ALL)) you can download it by running the `get_eia_data.py` script in the `src` directory (e.g. `$ python get_eia_data.py EBA.CAL-ALL.NG.SUN.HL`). Note: you must first be in the `src` directory for the script to execute properly.

Similarly, you can run the `get_regional_gen.py` script from the `src` directory (e.g `$ python get_regional_gen.py`) to pull generation information from various regions across the US, split up by generation type.

Both scripts are setup to store the CSV output files in the `output` directory.

## Python Help
This project is built using Python 3.8 and a few Python libraries. It's external dependencies are:
- numpy
- pandas
- dateutil

Other libraries used are included as part of the Python standard library. 

The easiest way to get started if you do not already use Python is [Miniconda](https://docs.conda.io/en/latest/miniconda.html). Miniconda is a minimal installer that includes Python, the `conda` package manager, and a few dependencies. 
You can also use [Anaconda](https://www.anaconda.com/products/individual), which is similar to Miniconda, but it automatically installes a large number of commonly used libraries that take up a lot of disk space on your computer. I find Miniconda to be less bloated. 

Once you have installed one of these (either Miniconda or Anaconda) and followed the instructions for setting up your command line environment to recognize `conda` commands, you can simply create a `conda` environment with all the correct dependencies for this project by running the command `$ conda env create -f environment.yml` from within the project directory.
