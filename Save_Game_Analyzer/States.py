import csv
import locale
import os
import re

# Set the locale for currency formatting
locale.setlocale(locale.LC_ALL, 'en_US.UTF8')

try:


    # Create the "outputs" folder if it doesn't exist
    os.makedirs("outputs", exist_ok=True)

    # Get the list of .v2 files in the "savegames" folder
    savegame_files = [file for file in os.listdir("savegames") if file.endswith(".v2")] 

    # Process each .v2 file
    for savegame_file in savegame_files:
    # Construct the input and output file path and make sure folder is created
        input_file = os.path.join("savegames", savegame_file)
        output_folder = os.path.splitext(savegame_file)[0]
        script_folder = os.path.dirname(os.path.abspath(__file__))
        parent_folder = os.path.dirname(script_folder)
        common_folder = os.path.join(parent_folder, 'common')
        production_types = os.path.join(common_folder, 'production_types.txt')
        os.makedirs(os.path.join("outputs", output_folder ), exist_ok=True)

        #load provinces.csv in a list with a dictionary
        provinces_csv = []
        folder_path = os.path.join("outputs", output_folder.strip("\t"), "Provinces.csv")
        with open(folder_path, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                detail = {}
                detail['State'] = row[5]
                detail['Tag'] = row[3]
                detail['Country'] = row[4]
                detail['Population'] = row[7]
                detail['RGO_Income'] = row[10]
                detail['PGDP'] = row[11]
                detail['AGDP'] = row[14]
                provinces_csv.append(detail)

        #load factories.csv in a list with a dictionary
        factory_csv = []
        folder_path = os.path.join("outputs", output_folder.strip("\t"), "Factory.csv")
        with open(folder_path, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                detail = {}
                detail['State'] = row[1]
                detail['Tag'] = row[2]
                detail['Employees'] = row[6]
                detail['Revenue'] = row[10]
                detail['Profit'] = row[13]
                detail['FGDP'] = row[14]
                factory_csv.append(detail)

        States = []
        for x in provinces_csv[1:]:
            state_name = x['State']
            country_name = x['Tag']
            detail = {'Name': state_name, 'Tag': country_name}
            
            # Check if a similar entry already exists in States
            if detail not in States:
                States.append(detail)

        for index, x in enumerate(States):
            pop = 0
            r_income = 0
            pgdp = 0
            agdp = 0


            for y in provinces_csv[1:]:
                if x['Name'] == y['State'] and x['Tag'] == y['Tag']:
                    pop += float(y['Population'])
                    r_income += float(y['RGO_Income'])
                    pgdp += float(y['PGDP'])
                    agdp += float(y['AGDP'])
                    States[index]['Country'] = y['Country']

            States[index]['Population'] = pop
            States[index]['RGO_Income'] = float(format(r_income,"2f"))
            States[index]['PGDP'] = float(format(pgdp,"2f"))
            States[index]['AGDP'] = float(format(agdp,"2f"))


        for index, x in enumerate(States):
            emp = 0
            f_income = 0
            f_profit = 0
            fgdp = 0

            for z in factory_csv[1:]:
                if x['Name'] == z['State'] and x['Tag'] == z['Tag']:
                    emp += float(z['Employees'])
                    f_income += float(z['Revenue'].strip("$()").replace(",",""))
                    f_profit += float(z['Profit'].strip("$()").replace(",",""))
                    fgdp += float(z['FGDP'])

            States[index]['Employees'] = emp
            States[index]['Revenue'] = float(format(f_income,"2f"))
            States[index]['Profit'] = float(format(f_profit,"2f"))
            States[index]['FGDP'] = float(format(fgdp,"2f"))

        for index, x in enumerate(States):
            fgdp = float(x['FGDP'])
            pgdp = float(x['PGDP'])
            agdp = float(x['AGDP'])
            States[index]['GDP'] = fgdp + pgdp + agdp
            pops = float(x['Population'])

            if pops != 0:
                gdp = float(x['GDP'])           
                States[index]['GDP_PerCapita'] = gdp/pops
            else:
                States[index]['GDP_PerCapita'] = 0

        # Sorts and Ranks the details by largest profit
        States.sort(key=lambda x: x['GDP'], reverse=True)

        for index, x in enumerate(States):
            States[index]['Rank'] = index + 1


        # Construct the output file path
        output_file = os.path.join("outputs", os.path.splitext(savegame_file)[0], "States.csv")

        # Write the States to the CSV file
        with open(output_file, 'w', newline='') as file:
            fieldnames = ['Rank', 'Name', 'Country', 'Population', 'GDP', 'GDP_PerCapita', 'RGO_Income', 'PGDP', 'AGDP', 'FGDP', 'Employees', 'Revenue', 'Profit']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

            # Write each row with formatted currency values
            for detail in States:
                row = {
                    'Rank': detail['Rank'],
                    'Name': detail['Name'],
                    'Country': detail['Country'],
                    'Population': detail['Population'],
                    'GDP': locale.currency(detail['GDP'], grouping=True),
                    'GDP_PerCapita': locale.currency(detail['GDP_PerCapita'], grouping=True),
                    'RGO_Income': locale.currency(detail['RGO_Income'], grouping=True),
                    'PGDP': locale.currency(detail['PGDP'], grouping=True),
                    'AGDP': locale.currency(detail['AGDP'], grouping=True),
                    'FGDP': locale.currency(detail['FGDP'], grouping=True),
                    'Employees': detail['Employees'],
                    'Revenue': locale.currency(detail['Revenue'], grouping=True),
                    'Profit': locale.currency(detail['Profit'], grouping=True)

                }
                writer.writerow(row)






        print(f"States from '{savegame_file}' have been successfully written to '{output_file}'.")


except Exception as e:
    print("States.csv was not able to be written")
    print("An error occurred:", str(e))
