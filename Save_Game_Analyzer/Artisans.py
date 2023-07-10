import csv
import locale
import os

# Set the locale for currency formatting
locale.setlocale(locale.LC_ALL, '')

# Create the "outputs" folder if it doesn't exist
os.makedirs("outputs", exist_ok=True)

try:
    


    # Get the list of .v2 files in the "savegames" folder
    savegame_files = [file for file in os.listdir("savegames") if file.endswith(".v2")]

    # Process each .v2 file and create output folder
    for savegame_file in savegame_files:
        # Construct the input file path
        input_file = os.path.join("savegames", savegame_file)
        output_folder = os.path.splitext(savegame_file)[0]
        os.makedirs(os.path.join("outputs", output_folder ), exist_ok=True)

        #load provinces.csv in a list with a dictionary
        provinces_csv = []
        folder_path = os.path.join("outputs", output_folder.strip("\t"), "Provinces.csv")
        with open(folder_path, 'r',  encoding='latin-1') as file:
            reader = csv.reader(file)
            for row in reader:
                detail = {}
                detail['ID'] = row[0]
                detail['Provid'] = row[1]
                detail['Name'] = row[2]
                detail['Country'] = row[3]
                detail['State'] = row[5]
                provinces_csv.append(detail)

        #load Goods.csv in a list with a dictionary
        Goods_csv = []
        folder_path = os.path.join("outputs", output_folder.strip("\t"), "Goods.csv")
        with open(folder_path, 'r',  encoding='latin-1') as file:
            reader = csv.reader(file)
            for row in reader:
                detail = {}
                detail['Good'] = row[0]
                detail['Price'] = row[1]
                Goods_csv.append(detail)


        # Read the content of the input file
        with open(input_file, 'r',  encoding='latin-1') as file:
            content = file.read()

        # Find all instances of "state_buildings="
        province_instances = content.split('=\n{\n\tname=')

        artisans = []
        pcounter = 0

        for idx, instance in enumerate(province_instances[1:]):

            try:
                x = instance.split('goods_type="')[1].split('"\n')[0].strip()
                pcounter = pcounter + 1 #creates province id counter     
                artisan_instance = instance.split('production_type="artisan_')

                for A_instance in artisan_instance[1:]:
                    detail = {}
                    artisan_instance_line = A_instance.split('\n')
                    detail['artisan_type'] = artisan_instance_line[0].strip("\"")
                    
                    if detail['artisan_type'] == "winery":
                        detail['artisan_type'] = "wine"
                    if detail['artisan_type'] == "telephone":
                        detail['artisan_type'] = "telephones"
                    if detail['artisan_type'] == "automobile":
                        detail['artisan_type'] = "automobiles"
                    if detail['artisan_type'] == "steamer":
                        detail['artisan_type'] = "steamer_convoy"
                    if detail['artisan_type'] == "clipper":
                        detail['artisan_type'] = "clipper_convoy"
                    if detail['artisan_type'] == "aeroplane":
                        detail['artisan_type'] = "aeroplanes"
                    if detail['artisan_type'] == "barrel":
                        detail['artisan_type'] = "barrels"
                    if detail['artisan_type'] == "fabric_wool":
                        detail['artisan_type'] = "fabric"

                    
                    LS_instance = A_instance.split('last_spending=')
                    PI_instance = A_instance.split('production_income=')

                    for x in LS_instance[1:]:
                        LS_line = x.split('\n')
                        detail['last_spending'] = float(LS_line[0].strip())/1000
                    for y in PI_instance[1:]:
                        PI_line = y.split('\n')
                        detail['production_income'] = float(PI_line[0].strip())/1000
                    
                    detail['AGDP'] = detail['production_income'] - detail['last_spending']
                    
                    if detail['AGDP'] < -1000:
                        detail['AGDP'] = 0

                    
                    detail['ID'] = pcounter 
                    artisans.append(detail)
                
            except:
                pass
        #add country tag to Artisans based on matching province id from provincecsv with id in artisan
        for index, row in enumerate(artisans):
            for x in provinces_csv:
                a = str(row['ID'])
                i = str(x['ID'])
                if a == i:
                    artisans[index]['Country'] = x['Country']
                    artisans[index]['State'] = x['State']
                    artisans[index]['Provid'] = x['Provid']
                    artisans[index]['Name'] = x['Name']

        for index, row in enumerate(artisans):
            for x in Goods_csv[1:]:
                a = str(row['artisan_type'])
                g = str(x['Good'])
                #print(a + " - good - " + g)
                if a == g:
                    artisans[index]['Price'] = float(x['Price'])
                    artisans[index]['Production'] = artisans[index]['production_income']/artisans[index]['Price']
                    break
                else:
                    artisans[index]['Price'] = 1
                    artisans[index]['Production'] = 0


        # Construct the output file path Provinces must be first
        outputs_folder = os.path.splitext(savegame_file)[0].strip("\t")
        output_file = os.path.join("outputs", outputs_folder, "Artisans.csv")

        # Write the details to the CSV file
        with open(output_file, 'w', newline='') as file:
            fieldnames = ['ID', 'Provid', 'Name', 'Country', 'State', 'artisan_type', 'last_spending', 'production_income', 'AGDP', 'Production' ]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

            # Write each row with formatted currency values
            for detail in artisans:
                row = {
                    'ID': detail['ID'],
                    'Provid': detail['Provid'],
                    'Name': detail['Name'],
                    'Country': detail['Country'],
                    'State': detail['State'],
                    'artisan_type': detail['artisan_type'],
                    'last_spending': detail['last_spending'],
                    'production_income': detail['production_income'],
                    'AGDP': detail['AGDP'],
                    'Production': detail['Production']

                }
                writer.writerow(row)

        print(f"Artisans from '{savegame_file}' have been successfully written to '{output_file}'.")

except Exception as e:
    print("Artisans.csv not able to be written")
    print("An error occurred:", str(e))