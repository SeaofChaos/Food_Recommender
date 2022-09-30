import argparse
import pandas as pd
import os

def main():
    #CLA argument definitions
    parser = argparse.ArgumentParser("Copy recipe data set, clean it, and output in a new file.\n")
    parser.add_argument('--oldfile', '-f', type=str, required=True, help="File containing 1M raw dataset.")
    parser.add_argument('--newfile', '-n', type=str, required=True, help="New file to copy formatted dataset into.")
    parser.add_argument('--overwriteFile', '-o', action='store_false', help="Give warning about overwriting a pre-existing file.")
    args = parser.parse_args()

    if (args.oldfile).endswith() != ".json":
        sys.exit("File must be .json")

    #read CLA for uncleaned data file and new data file name
    oldFile = os.getcwd() + "\\Datasets\\" + args.oldfile

    print("Loading recipes into program.")
    sheet = pd.read_json(oldFile)
    print("Finished")

    row = 0
    ingredients = []
    lenIng = len(sheet['ingredients'])
    print("Formatting recipes...")
    for recipe in sheet['ingredients']:
        ing = []
        for ingredient in recipe:
            ing.append(ingredient['text'])
        
        sheet['ingredients'][row] = [*ing]
        #sheet['ingredients'][row] = rIng
        #print("sheet['ingredients'][row]: ", sheet['ingredients'][row])
        
        row += 1
        print("\r", end='')
        print("Current row: ", row, "out of ", lenIng, end='')
    print(" done.")
    #print(sheet.info)
    sheet.to_csv(os.getcwd() + '\\Datasets\\out.csv')
    sys.exit("Successfully copied data to: \\Datasets\\out.csv\nPlease run this program again with this formatted file.")

if __name__ == "__main__":
    main()