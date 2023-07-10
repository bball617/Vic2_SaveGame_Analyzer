import csv
import locale
import os
import re

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

    #x = 0 Uncomment when testing to only try 1 save game file in testing called testing.v2
    #if x == 0: Uncomment when testing to only try 1 save game file in testing called testing.v2
        #input_file = os.path.join("testing", "testing.v2") Uncomment when testing to only try 1 save game file in testing called testing.v2

        # Read the content of the input file
        with open(input_file, 'r', encoding='latin-1') as file:
            content = file.read()

        instances = content.split('price_pool=') #fine price pool in save game file
        pricepool = instances[1].split('}') # get instance with price pool ahead of last curley bracket
        Goods = []

        lines = pricepool[0].split('\n')
        lines = [line.replace('{', '') for line in lines]
        lines = [line.replace('}', '') for line in lines]
        lines = [line.replace('\t', '') for line in lines]
        lines = [line.replace(' ', '') for line in lines]
     
        for line in lines[2:]:
            try:
                detail = {}
                y = line.split('=')
                detail['Good'] = y[0]
                detail['Price'] = y[1]

                Goods.append(detail)
            except:
                pass

        #x = x + 1 Uncomment when testing to only try 1 save game file in testing called testing.v2

        # Construct the output file path Provinces must be first
        outputs_folder = os.path.splitext(savegame_file)[0].strip("\t")
        output_file = os.path.join("outputs", outputs_folder, "Goods.csv")

        # Write the details to the CSV file
        with open(output_file, 'w', newline='') as file:
            fieldnames = ['Good', 'Price']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

            # Write each row with formatted currency values
            for detail in Goods:
                row = {
                    'Good': detail['Good'],
                    'Price': detail['Price'],

                }
                writer.writerow(row)

        print(f"Goods from '{savegame_file}' have been successfully written to '{output_file}'.")

except Exception as e:
    print("Goods.csv was not able to be written")
    print("An error occurred:", str(e))