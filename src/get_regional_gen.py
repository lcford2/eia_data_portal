from get_eia_data import *
import sys
import pathlib

# Script to get various data from EIA. 
# This should be relatively successful
# Generation types
gen_types = {"Wind":"WND", "Solar":"SUN", "Nuclear":"NUC",
             "Hydro":"WAT", "Coal":"COL", "NatGas":"NG",
             "Oil":"OIL", "Other":"OTH"}

# US Regions
regions = {
    "California": "CAL",
    "Carolinas": "CAR",
    "Central": "CENT",
    "Florida": "FLA",
    "Mid - Atlantic": "MIDA",
    "Midwest": "MIDW",
    "New England": "NE",
    "New York": "NY",
    "Northwest": "NW",
    "Southeast": "SE",
    "Southwest": "SW",
    "Tennessee": "TEN",
    "Texas": "TEX"
}

# EBA is Electric Balancing Authority
# First format slot is for region, 
# NG is net generation
# Second format slot is for generation type
# HL is hourly
base_id = "EBA.{}-ALL.NG.{}.HL"
with open('./api_key.txt', 'r') as key_file:
    api_key = key_file.read().strip("\n\r")

# where to store the data
output_path = pathlib.Path("../output/regional_generation")
# some basic file system checks
if output_path.exists():
    # if the path exists but it is not a directory
    if not output_path.is_dir():
        print(f"Output path '{output_path.as_posix()}' is not a directory.")
        sys.exit()
else:
    # create the directory if it does not exists
    output_path.mkdir()

# Loop over regions and gen types
# Call the API portal to get data
# setup the portal once, then pass a new series id every time
datagetter = EIAgov(api_key, None)
for region, key in regions.items():
    # dataframe for region
    regional_df = pd.DataFrame()
    for gentype, genkey in gen_types.items():
        print(region, gentype)
        series_id = base_id.format(key, genkey)
        data = datagetter.get_formatted_data(series_id)
        # this is why I return an empty dataframe in get_eia_data.EIAgov.format_data
        # if it cannot find the series requested
        if not data.empty:
            data = data.rename(columns={"Data":gentype})
            data = data.set_index("Date")
            data = data.drop("Units", axis=1)
            # this way we continously update regional df with new generator data
            if regional_df.empty:
                regional_df = data
            else:
                regional_df = regional_df.join(data)

    regional_df = regional_df.reset_index()
    # write the dataframe to a csv file
    regional_df.to_csv(output_path / f"{key}_gen.csv")
