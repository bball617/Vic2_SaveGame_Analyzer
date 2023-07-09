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

        # Open and parse the production_types.txt to add goods and factory into dictionary
        with open(production_types, mode="r") as file:
            content = file.read()
            building_to_good = {}
            lines = content.split('\n')
            for index, line in enumerate(lines):
                if "input_goods =" in line:
                    line_count = index
                    factory_name = "blank"
                    while " = {" not in factory_name:
                        line_count -= 1
                        factory_name = lines[line_count]
                        if "template" in factory_name:
                            continue
                        else:
                            factory_name = factory_name.strip('{= ')
                            factory_name = factory_name.strip("")
                            building_to_good[factory_name] = "blank"
                            break

                if "output_goods =" in line:
                    line_count_output = index
                    z = lines[line_count_output]
                    good = z.split(' = ')[1].strip()
                    building_to_good[factory_name] = good

        #load provinces.csv in a list with a dictionary
        provinces_csv = []
        folder_path = os.path.join("outputs", output_folder.strip("\t"), "Provinces.csv")
        with open(folder_path, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                detail = {}
                detail['ID'] = row[1]
                detail['Tag'] = row[3]
                detail['Country_Name'] = row[4]
                detail['Colony'] = row[6]
                detail['Population'] = row[7]
                detail['Good'] = row[8]
                detail['RGOProduction'] = row[9]
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
                detail['Tag'] = row[2]
                detail['Building'] = row[4]
                detail['Production'] = row[7]
                detail['FGDP'] = row[14]
                factory_csv.append(detail)

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

        #load Artisans.csv in a list with a dictionary
        Artisans_csv = []
        folder_path = os.path.join("outputs", output_folder.strip("\t"), "Artisans.csv")
        with open(folder_path, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                detail = {}
                detail['Tag'] = row[3]
                detail['Artisan_Type'] = row[5]
                detail['Production'] = row[9]
                Artisans_csv.append(detail)


        # Get each unique country from provinces_csv
        unique_Countries = set()
        for row in provinces_csv:
            x = row['Tag']
            if x == 'Owner':
                continue
            unique_Countries.add(x)

        # Create a dictionary in a list to store unique countries and detasils
        country = []
        for x in unique_Countries:
            detail = {}
            detail['ID'] = x
            detail['Population'] = 0
            detail['FGDP'] = 0
            detail['PGDP'] = 0
            detail['GDP'] = 0
            detail['GDPperCapita'] = 0

            country.append(detail)

        # Calculate Factory GDP for each country and add to Country List
        for index, x in enumerate(country):  # Skip the first row
            FGDP = 0
            # Check if the country in column 3 of provinces.csv is in the Countries set
            for y in factory_csv[1:]:
                if y['Tag'] == x['ID'] :
                    z = float(y['FGDP'])
                    FGDP += z
                country[index]['FGDP'] = float(format(FGDP, ".3f"))

        # Calculate Province GDP for each country and add to Country List
        for index, x in enumerate(country):
            PGDP = 0
            AGDP = 0
            for y in provinces_csv[1:]:
                if y['Tag'] == x['ID'] :
                    z = float(y['PGDP'])
                    zz = float(y['AGDP'])
                    PGDP += z
                    AGDP += zz
                country[index]['PGDP'] = float(format(PGDP, ".0f"))
                country[index]['AGDP'] = float(format(AGDP, ".0f"))

        # Calculate population for each country and add to Country List
        for index, x in enumerate(country):
            pop = 0
            for y in provinces_csv[1:]:
                if y['Tag'] == x['ID'] and y['Colony'] == "False":
                    z = float(y['Population'])
                    pop += z
                country[index]['Population'] = pop

        # Calculate Colony population for each country and add to Country List
        for index, x in enumerate(country):
            pop = 0
            for y in provinces_csv[1:]:
                if y['Tag'] == x['ID'] and y['Colony'] == "True":
                    z = float(y['Population'])
                    pop += z
                country[index]['Colony_Population'] = pop

        # Calculate total GDP by adding province and Factory GDP and GDP per Capita by dividinging by population
        for index, x in enumerate(country):
            country[index]['Total_Population'] = country[index]['Colony_Population'] + country[index]['Population']
            country[index]['GDP'] = x['FGDP'] + x['PGDP'] + x['AGDP']
            if country[index]['Population'] == 0:
                country[index]['GDPperCapita'] = 0
            else:
                country[index]['GDPperCapita'] = float(format(country[index]['GDP']/x['Population'], ".3f"))

        #Calculate goods production by country from Provinces.csv
        for index, row in enumerate(country):
            province_goods = []
            for x in provinces_csv[1:]:
                if x['Tag'] == row['ID']:
                    detail = {}
                    detail['ID'] = x['Tag']
                    detail['Good'] = x['Good']
                    detail['RGOProduction'] = float(x['RGOProduction'])
                    province_goods.append(detail)

            for y in Goods_csv[1:]:
                goods_counter = 0
                for z in province_goods:
                    if y['Good'] == z['Good']:
                        goods_counter += z['RGOProduction']
                country[index][y['Good']] = format(goods_counter,".1f")


        # Calculate the production of each good from factories and add to Country List
        for index, x in enumerate(country):
            goods_production = {}
            for y in factory_csv[1:]:
                if y['Tag'] == x['ID']:
                    building = y['Building']
                    production = float(y['Production'])
                    good = building_to_good.get(building)
                    if good:
                        goods_production[good] = goods_production.get(good, 0) + production

            for good in goods_production:
                x[good] = format(goods_production[good], ".1f")

        # Add the total production of each good in the country
        for index, x in enumerate(country):
            for good in building_to_good.values():
                total_production = sum(float(y[good]) if y.get(good) else 0 for y in country if y['ID'] == x['ID'])
                x[good] = format(total_production, ".1f")


        # Calculate the total artisan quantity of each good and update the goods' total in each country
        for index, x in enumerate(country):
            artisan_production = {}
            for y in Artisans_csv[1:]:
                if y['Tag'] == x['ID']:
                    artisan_type = y['Artisan_Type']
                    production = float(y['Production'])
                    good = re.sub(r'_(\d+)', '', artisan_type)  # Remove the number from the artisan type
                    artisan_production[good] = artisan_production.get(good, 0) + production

            for good in artisan_production:
                x[good] = format(float(x[good]) + artisan_production[good], ".1f")

        for index, x in enumerate(country):
            for y in provinces_csv[1:]:
                if x['ID'] == y['Tag']:
                    country[index]['Name'] = y['Country_Name']

        # Sort and ranks the details by largest profit
        country.sort(key=lambda x: x['GDP'], reverse=True)

        for index, x in enumerate(country):
            country[index]['Rank'] = index + 1

            # Construct the output file path
        #outputs_folder = os.path.splitext(savegame_file)[0].strip("\t") uncomment line when done
        output_file = os.path.join("outputs", output_folder, savegame_file + ".csv")

        #Write the details to the CSV file
        with open(output_file, 'w', newline='') as file:
            fieldnames = ['Rank', 'ID', 'Name', 'Population', 'Colony_Population', 'Total_Population', 'FGDP', 'PGDP', 'AGDP', 'GDP', 'GDPperCapita', 'ammunition', 'small_arms', 'artillery', 'canned_food', 'barrels', 'aeroplanes', 'cotton', 'dye', 'wool', 'silk', 'coal', 'sulphur', 'iron', 'timber', 'tropical_wood', 'rubber', 'oil', 'precious_metal', 'precious_goods', 'steel', 'cement', 'machine_parts', 'glass', 'fuel', 'fertilizer', 'explosives', 'clipper_convoy', 'steamer_convoy', 'electric_gear', 'fabric', 'lumber', 'paper', 'cattle', 'fish', 'fruit', 'grain', 'tobacco', 'tea', 'coffee', 'opium', 'automobiles', 'telephones', 'wine', 'liquor', 'regular_clothes', 'luxury_clothes', 'furniture', 'luxury_furniture', 'radio']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

            # Write each row with formatted currency values
            for detail in country:
                row = {
                    'Rank': detail['Rank'],
                    'ID': detail['ID'],
                    'Name': detail['Name'],
                    'Population': detail['Population'],
                    'Colony_Population': detail['Colony_Population'],
                    'Total_Population': detail['Total_Population'],
                    'FGDP': locale.currency(detail['FGDP'], grouping=True),
                    'PGDP': locale.currency(detail['PGDP'], grouping=True),
                    'AGDP': locale.currency(detail['AGDP'], grouping=True),
                    'GDP': locale.currency(detail['GDP'], grouping=True),
                    'GDPperCapita': locale.currency(detail['GDPperCapita'], grouping=True),
                    'ammunition': detail['ammunition'],
                    'small_arms': detail['small_arms'],
                    'artillery': detail['artillery'],
                    'canned_food': detail['canned_food'],
                    'barrels': detail['barrels'],
                    'aeroplanes': detail['aeroplanes'],
                    'cotton': detail['cotton'],
                    'dye': detail['dye'],
                    'wool': detail['wool'],
                    'silk': detail['silk'],
                    'coal': detail['coal'],
                    'sulphur': detail['sulphur'],
                    'iron': detail['iron'],
                    'timber': detail['timber'],
                    'tropical_wood': detail['tropical_wood'],
                    'rubber': detail['rubber'],
                    'oil': detail['oil'],
                    'precious_metal': detail['precious_metal'],
                    'precious_goods': detail['precious_goods'],
                    'steel': detail['steel'],
                    'cement': detail['cement'],
                    'machine_parts': detail['machine_parts'],
                    'glass': detail['glass'],
                    'fuel': detail['fuel'],
                    'fertilizer': detail['fertilizer'],
                    'explosives': detail['explosives'],
                    'clipper_convoy': detail['clipper_convoy'],
                    'steamer_convoy': detail['steamer_convoy'],
                    'electric_gear': detail['electric_gear'],
                    'fabric': detail['fabric'],
                    'lumber': detail['lumber'],
                    'paper': detail['paper'],
                    'cattle': detail['cattle'],
                    'fish': detail['fish'],
                    'fruit': detail['fruit'],
                    'grain': detail['grain'],
                    'tobacco': detail['tobacco'],
                    'tea': detail['tea'],
                    'coffee': detail['coffee'],
                    'opium': detail['opium'],
                    'automobiles': detail['automobiles'],
                    'telephones': detail['telephones'],
                    'wine': detail['wine'],
                    'liquor': detail['liquor'],
                    'regular_clothes': detail['regular_clothes'],
                    'luxury_clothes': detail['luxury_clothes'],
                    'furniture': detail['furniture'],
                    'luxury_furniture': detail['luxury_furniture'],
                    'radio': detail['radio']
                }
                writer.writerow(row)

        print(f"Countries from '{savegame_file}' have been successfully written to '{output_file}'.")
    input("Press Enter to exit.")

except Exception as e:
    print(f"'{savegame_file}'.csv was not able to be written")
    print("An error occurred:", str(e))