import csv
import locale
import os
import json

# Set the locale for currency formatting
locale.setlocale(locale.LC_ALL, '')

# Create the "outputs" folder if it doesn't exist
os.makedirs("outputs", exist_ok=True)

try:

    # Get the list of .v2 files in the "savegames" folder
    savegame_files = [file for file in os.listdir("savegames") if file.endswith(".v2")]

    # Process each .v2 file
    for savegame_file in savegame_files:
        # Construct the input file path
        input_file = os.path.join("savegames", savegame_file)
        output_folder = os.path.splitext(savegame_file)[0]
        os.makedirs(os.path.join("outputs", output_folder ), exist_ok=True)
        #print(savegame_file[0])

        #load Goods.csv in a list with a dictionary
        Goods_csv = []
        folder_path = os.path.join("outputs", output_folder.strip("\t"), "Goods.csv")
        with open(folder_path, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                detail = {}
                detail['Good'] = row[0]
                detail['Price'] = row[1]
                Goods_csv.append(detail)

        #load listofprovinces.csv in a list with a dictionary
        Provinces_list_csv = []
        with open('listofprovinces.csv', 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                detail = {}
                detail['prov_id'] = row[0]
                detail['prov_name'] = row[1]
                Provinces_list_csv.append(detail)

        # Read the content of the input file
        with open(input_file, 'r') as file:
            content = file.read()

        # Find all instances of "Provinces="
        instances = content.split('=\n{\n\tname=')

        # Initialize a list to store the extracted details and counter to count province ID
        provinces = []
        pcounter = 0

         # Process each instance
        for idx, instance in enumerate(instances[1:], start=1):
            detail = {}
            pops = 0
            last_spending_counter = 0
            production_income_counter = 0

            # Assign a unique ID
            firstline = instance.split('\n')      

            # Make sure each instance that starts with name contains a good type to avoid non provinces instances
            try:
                detail['Goods_type'] = instance.split('goods_type="')[1].split('"\n')[0].strip()
                detail['RGO_Production'] = 0
                pcounter = pcounter + 1 #creates province id counter
                detail['ID'] = pcounter

                try:
                    detail['Name'] = firstline[0].strip('\"') #create province name and state dictionary
                    detail['State'] = 'blank' #create state dictionary as blank to add later
                    detail['Colony'] = False
                    for line in firstline:
                        if "colonial=2" in line:
                            detail['Colony'] = True
                except IndexError:
                    detail['Name'] = 'no name' #add exception if none found create name as no name

                size = instance.split('size=') #create "size" instances within the "name=" instance to add up population

                for size_instance in size[1:]:
                    size_first_line = size_instance.split('\n')
                    try:
                        pops += float(size_first_line[0].strip('\"'))

                    except:
                        pass

                try:
                    detail['Pop'] = pops
                except:
                    detail['Pop'] = 0

                try:
                    detail['Owner'] = instance.split('owner="')[1].split('"\n')[0].strip()     #add owner tag to province list     
                except IndexError:
                    detail['Owner'] = 'none'

                try:
                    detail['Last_income'] = float(instance.split('last_income=')[1].split('\n')[0].strip()) / 1000  #add last income of RGO in province
                    detail['GDP'] = detail['Last_income'] * 365 # add up GDP by multiplying last income by 365
                except IndexError:
                    detail['Last_income'] = 0
                    detail['GDP'] = float(detail['Last_income']) * 365

                artisan_LS = instance.split('last_spending=')
                artisan_PI = instance.split('production_income=')

                for LS_instance in artisan_LS[1:]:
                    LS_first_line = LS_instance.split('\n')
                    try:
                        last_spending_counter += float(LS_first_line[0].strip('\"'))

                    except:
                        pass
                detail['Last_Spending'] = float(format(last_spending_counter/1000,"2f"))

                for PI_instance in artisan_PI[1:]:
                    PI_first_line = PI_instance.split('\n')
                    try:
                        production_income_counter += float(PI_first_line[0].strip('\"'))

                    except:
                        pass
                detail['Production_Income'] = float(format(production_income_counter/1000,"2f"))

                detail['AGDP'] = detail['Production_Income'] - detail['Last_Spending']

                if detail['AGDP'] < -1000:
                    detail['AGDP'] = 0
            
                # Append the detail to the list
                provinces.append(detail)


            except IndexError: 
                pass
        for index, x in enumerate(provinces):
            for y in Goods_csv:
                if y['Good'] == x['Goods_type']:
                    goodproduction = float(format(x['Last_income']/float(y['Price']),"2f"))
                    provinces[index]['RGO_Production'] = goodproduction
            provinces[index]['Provid'] = Provinces_list_csv[index + 1]['prov_id']



        # Load the state names from 'liststates.csv' into a dictionary
        state_names = {}
        with open('listofstates.csv', 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                state_names[row[0]] = row[1]

        # Add state names to Detail[State]
        for detail in provinces:
            state_province_id = str(detail['Provid'])
            if state_province_id in state_names:
                detail['State'] = state_names[state_province_id]


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

        for index, x in enumerate(provinces):
            for y in Country_name_list:
                if x['Owner'] == y['tag']:
                    provinces[index]["Country"] = str(y['name'])
                    break
                else:
                    provinces[index]["Country"] = "none"


        # Construct the output file path Provinces must be first
        outputs_folder = os.path.splitext(savegame_file)[0].strip("\t")
        output_file = os.path.join("outputs", outputs_folder, "Provinces.csv")

        # Write the provinces to the CSV file
        with open(output_file, 'w', newline='') as file:
            fieldnames = ['ID', 'Provid', 'Name', 'Owner', 'Country', 'State','Colony', 'Pop', 'Goods_type', 'RGO_Production', 'Last_income', 'GDP', 'Last_Spending', 'Production_Income', 'AGDP']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

            # Write each row with formatted currency values
            for detail in provinces:
                row = {
                    'ID': detail['ID'],
                    'Provid': detail['Provid'],
                    'Name': detail['Name'],
                    'Owner': detail['Owner'],
                    'Country': detail['Country'],
                    'State': detail['State'],
                    'Colony': detail['Colony'],
                    'Pop': detail['Pop'],
                    'Goods_type': detail['Goods_type'],
                    'RGO_Production': detail['RGO_Production'],
                    'Last_income': detail['Last_income'],
                    'GDP': detail['GDP'],
                    'Last_Spending': detail['Last_Spending'],
                    'Production_Income': detail['Production_Income'],
                    'AGDP': detail['AGDP']
                }
                writer.writerow(row)

        print(f"Provinces from '{savegame_file}' have been successfully written to '{output_file}'.")

except Exception as e:
    print("Provinces.csv was not able to be written")
    print("An error occurred:", str(e))

