import pandas as pd
import yaml
import os
import argparse
import pprint


base_path = '.'
def compare_csv_to_yaml(device,field,area):
    fname = os.path.join(base_path,f'{area}.yaml')
    if os.path.isfile(fname):
        with open(fname, "r") as f:
            data = yaml.safe_load(f)
    pprint.pprint(data)

def parse_df_by_columns(df, *args):
    a = list(args)
    #print(a)
    filtered_df = df[a]
    return filtered_df

def parse_df_column_by_row_elements(df, column_name, values_to_keep):
    fdf = df[df[column_name].isin(values_to_keep)]
    return fdf
 
def main():
    df = pd.read_csv('lcls_elements.csv')

    parser = argparse.ArgumentParser(description="Script for checking device information matches between csv and yaml")
    parser.add_argument('--area', '-a', default= None, help= 'Accelerator area that you want to run the comparison for, if flag is not passed all areas will be compared')
    parser.add_argument('--device_type', '-d', choices=['magnet','lblm','screen','wire'], default= 'magnet')
    parser.add_argument('--field', '-f', default= None, help= 'Metadata that you want compared')

    args = parser.parse_args()
    area = args.area
    if args.device_type == 'magnet':
        device_types = ["SOLE", "QUAD", "XCOR", "YCOR", "BEND"]
    elif args.device_type == 'lblm':
        device_types = ["PROF"]
    elif args.device_type == 'screen':
        device_types = ["WIRE"]
    elif args.device_type == 'wire':
        device_types = ["LBLM"]

    metadata_field = args.field
    fdf = parse_df_column_by_row_elements(df,'Keyword',device_types)

    if area is None:
    #    #print('Checking df for unique areas and creating a list to loop over')
        areas_col = parse_df_by_columns(fdf,'Area')
        areas = set(areas_col['Area'].to_list())
        for area in areas:
            compare_csv_to_yaml(args.device_type,metadata_field,area)

    else:
        compare_csv_to_yaml(args.device_type,metadata_field,area)


if __name__ == "__main__":
    main()


#df = pd.read_csv('lcls-tools/lcls_tools/common/devices/yaml/lcls_elements.csv')

#print(df["Effective Length (m)"].head(10))