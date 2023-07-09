import csv
import locale
import os

# Set the locale for currency formatting
locale.setlocale(locale.LC_ALL, '')

try:

    # Create the "outputs" folder if it doesn't exist
    os.makedirs("outputs", exist_ok=True)

    # Get the list of .v2 files in the "savegames" folder
    savegame_files = [file for file in os.listdir("savegames") if file.endswith(".v2")]

    # Process each .v2 file and create output folder
    for savegame_file in savegame_files:
        # Construct the input file path
        input_file = os.path.join("savegames", savegame_file)
        output_folder = os.path.splitext(savegame_file)[0]
        os.makedirs(os.path.join("outputs", output_folder ), exist_ok=True)

        # Read the content of the input file
        with open(input_file, 'r') as file:
            content = file.read()

        # Find all instances of "state_buildings="
        instances = content.split('state_buildings=')

        # Initialize a list to store the extracted details
        factories = []

        # Process each instance if state building
        for idx, instance in enumerate(instances[1:], start=1):
            detail = {}

            # Assign a unique ID
            detail['ID'] = idx

            # Extract the desired details
            detail['State_province_id'] = instance.split('state_province_id=')[1].split('\n')[0].strip()
            detail['Tag'] = detail['State_province_id']
            detail['Building'] = instance.split('building="')[1].split('"\n')[0].strip()
            detail['Level'] = int(instance.split('level=')[1].split('\n')[0].strip())
            detail['Last_spending'] = float(instance.split('last_spending=')[1].split('\n')[0].strip()) / 1000
            detail['Last_income'] = float(instance.split('last_income=')[1].split('\n')[0].strip()) / 1000
            detail['Pops_paychecks'] = float(instance.split('pops_paychecks=')[1].split('\n')[0].strip()) / 1000
            detail['Profit'] = detail['Last_income'] - detail['Last_spending'] - detail['Pops_paychecks']
            detail['Money'] = float(instance.split('money=')[1].split('\n')[0].strip()) / 1000 #added
            detail['Produces'] = float(instance.split('produces=')[1].split('\n')[0].strip()) #added
            detail['Leftover'] = float(instance.split('leftover=')[1].split('\n')[0].strip()) #added
            detail['Injected_money'] = float(instance.split('injected_money=')[1].split('\n')[0].strip()) / 1000 #added
            detail['GDP'] = (detail['Last_income'] - detail['Last_spending']) * 365

            employee_inst = instance.split('count=') # get each instance of "count" in state building instances to calculate employement
            employees_count = 0 # start counter at 0 for each factory

            for count_instance in employee_inst[1:]: #
                count_first_line = count_instance.split('\n')
                try:
                    if count_first_line[4].strip() == "province_pop_id=": #check to make sure line 4 of each count instance equals province pop id to make sure were not counting something other than factories
                        employees_count += float(count_first_line[0].strip('\"'))
                except:
                    pass
            detail['Employees'] = employees_count
            
            if detail['Employees'] != 0:
                detail['Productivity'] = detail['GDP']/detail['Employees']
                detail['AvgWage'] = detail['Pops_paychecks']/detail['Employees']
            else:
                detail['Productivity'] = 0
                detail['AvgWage'] = 0       

            # Append the detail to the list
            factories.append(detail)

        # Sort the factories by largest profit
        factories.sort(key=lambda x: x['Profit'], reverse=True)

        for index, x in enumerate(factories):
            factories[index]['ID'] = index + 1

        # Load the state names from 'listofstates.csv' into a dictionary
        state_names = {}
        with open('listofstates.csv', 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                state_names[row[0]] = row[1]

        # Replace state province IDs with state names
        for detail in factories:
            state_province_id = detail['State_province_id']
            if state_province_id in state_names:
                detail['State_province_id'] = state_names[state_province_id]

        # Load the state names from 'Provinces.csv' into a dictionary
        country_names = {}
        folder_path = os.path.join("outputs", output_folder.strip("\t"), "Provinces.csv")
        with open(folder_path, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                country_names[row[0]] = row[3]

        # Add country tag to factories
        for detail in factories:
            country_id = detail['Tag']
            if country_id in country_names:
                detail['Tag'] = country_names[country_id]

        script_folder = os.path.dirname(os.path.abspath(__file__))
        parent_folder = os.path.dirname(script_folder)
        folder_path = os.path.join(parent_folder, 'history', 'countries')
        Country_name_list = []  # Dictionary to store the file provinces

        for filename in os.listdir(folder_path):
            if filename.endswith(".txt"):
                split_name = filename.split(" - ")
            if len(split_name) == 2:
                country_tag, country_name = split_name[0].strip(), split_name[1].split(".")[0].strip()
                Country_name_list.append({"tag": country_tag, "name": country_name})

        for index, x in enumerate(factories):
            for y in Country_name_list:
                if x['Tag'] == y['tag']:
                    factories[index]["Country"] = str(y['name'])
                    break
                else:
                    factories[index]["Country"] = "none"

        # Construct the output file path
        output_file = os.path.join("outputs", os.path.splitext(savegame_file)[0], "Factory.csv")

        # Write the factories to the CSV file
        with open(output_file, 'w', newline='') as file:
            fieldnames = ['Rank', 'State', 'Tag', 'Country', 'Building', 'Level', 'Employees', 'Produces', 'Leftover', 'Money', 'Revenue', 'Input Costs', 'Pops_paychecks', 'Profit', 'GDP', 'Productivity', 'AvgWage']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

            # Write each row with formatted currency values
            for detail in factories:
                row = {
                    'Rank': detail['ID'],
                    'State': detail['State_province_id'],
                    'Tag': detail['Tag'],
                    'Country': detail['Country'],
                    'Building': detail['Building'],
                    'Level': detail['Level'],
                    'Employees': detail['Employees'],
                    'Produces': detail['Produces'],
                    'Leftover': detail['Leftover'],
                    'Money': locale.currency(detail['Money'], grouping=True),
                    'Revenue': locale.currency(detail['Last_income'], grouping=True),
                    'Input Costs': locale.currency(detail['Last_spending'], grouping=True),
                    'Pops_paychecks': locale.currency(detail['Pops_paychecks'], grouping=True),
                    'Profit': locale.currency(detail['Profit'], grouping=True),
                    'GDP': detail['GDP'],
                    'Productivity': detail['Productivity'],
                    'AvgWage': detail['AvgWage']

                }
                writer.writerow(row)

        print(f"Factories from '{savegame_file}' have been successfully written to '{output_file}'.")

except Exception as e:
    print("Factory.csv was not able to be written")
    print("An error occurred:", str(e))
