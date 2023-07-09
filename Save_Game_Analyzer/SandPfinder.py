import re
import csv
import os

try:

    script_folder = os.path.dirname(os.path.abspath(__file__))
    parent_folder = os.path.dirname(script_folder)
    map_folder = os.path.join(parent_folder, 'map')
    provinces_folder = os.path.join(parent_folder, 'history' , 'provinces')
    input_file = os.path.join(map_folder, 'region.txt')
    output_file = "listofstates.csv"

    # Define the regular expression pattern for extracting the numbers and state name
    pattern = r"= {\s*(.*?)\s*} #(.*)"

    # Initialize the CSV writer
    csv_file = open(output_file, mode="w", newline="")
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["Number", "State"])


    province_list = []

    for folder_name in os.listdir(provinces_folder):
        folder_path = os.path.join(provinces_folder, folder_name)
        if os.path.isdir(folder_path):
            for file_name in os.listdir(folder_path):
                if file_name.endswith('.txt'):
                    try:
                        if ' - ' in file_name:
                            province_id, province_name = file_name.split(' - ')
                        else:
                            province_id, province_name = file_name.split(None, 1)  # Split on first whitespace
                        province_id = int(province_id.strip())
                        province_name = province_name.strip('.txt')
                        province_dict = {'prov_id': province_id, 'prov_name': province_name}
                        province_list.append(province_dict)
                    except ValueError:
                        print(f"Ignoring file with unexpected name format: {file_name}")

    province_list_sorted = sorted(province_list, key=lambda x: x['prov_id'])

    csv_file = 'listofprovinces.csv'
    fieldnames = ['prov_id', 'prov_name']

    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(province_list_sorted)

    print(f"Province list has been saved to {csv_file}")

    # Open and parse the input file
    with open(input_file, mode="r") as file:
        for line in file:
            match = re.search(pattern, line)
            if match:
                numbers = match.group(1).split()
                state = match.group(2).strip()
                for number in numbers:
                    csv_writer.writerow([number, state])


    print(f"States list has been saved to {output_file}")

except Exception as e:
    print("States and provinces list csvs was not able to be written")
    print("An error occurred:", str(e))
