import pandas as pd
import sys
import os
import shutil
import argparse
import re
import numpy as np
import ast
import difflib
import itertools

#remove warnings about copying over dataframe

pd.options.mode.chained_assignment = None

measurements = ["tbsp","tablespoon","tsp","teaspoon","oz","ounce",
                "fl.","oz","fluid ounce","c","cup","qt","quart","pt",
                "pint","gal","gallon","lb","pound","mL","milliliter",
                "g","grams","kg","kilogram","l","liter"]

# Words to avoid when looking at valid ingredient key words
words_to_avoid = ["dry", "plus", "sliced", "more", "other", "sodium", 
                  "garnish", "for", "mild", "large", "small", "medium",
                  "cooked", "in", "square", "chopped", "ground", "whole",
                  "temperature", "extra", ]

# Words to avoid when looking for valid ingredients (normally these
# are words that cannot, alone, be considered an ingredient but are
# important parts of whole ingredients. e.g. white pepper needs 'white'
# but 'white' is not an ingredient in itself)
ingredients_to_avoid = ["green", "white", "black"]

approved_words = ["italian", "loaf"]

# TO DO IF I HAVE EXTRA TIME
# Add in more customization on what kind of recipe file you can input. Make it so 
# any file with an 'ingredients' column can be entered and it is able to handle 
# formats such as: a list of strings, a list of lists, or just a complete list of 
# ingredients.

def copyFile(args):
    # This function checks for valid command line arguments along with whether the 
    # new file name exists and if it can be properly copied.
    fileName = args.newfile
    if not (not fileName.endswith(".csv") or not fileName.endswith(".json")):
        sys.exit("Make sure the file name contains its extension (csv or json).")
    
    if args.overwriteFile:
        #check if file exists in directory
        if fileName in os.listdir(os.getcwd() + '\\Cleaned_Datasets'):
            sys.exit("New file name must not exist to avoid overwriting data.\nDelete \""+
                        fileName+"\", enter a different name, " +
                        "\nor use the -o argument to ignore this check.")
    
    #create new file to put cleaned data into
    try:
        shutil.copyfile(os.getcwd() + '\\Datasets\\' + args.oldfile, 
                        os.getcwd() + '\\Cleaned_Datasets\\' + fileName)
    except shutil.SameFileError:
        sys.exit("File already exists. Enter a different file name.")
    except IsADirectoryError:
        sys.exit("Entered file name is a directory. Make sure you only enter a valid file name.")
    except PermissionError:
        sys.exit("Permission to copy into new file denied. (File is most likely opened in another window.)")
    except:
        sys.exit("There was a problem copying data to new file. Make sure a only a valid file name is entered.")
    
    return fileName

def loadIngredients():
    #print("file: ", file)
    path = os.getcwd() + "\\Datasets\\"
    ingredients = []
    openedFile = False

    if os.path.isfile(path + "simplified-recipes-1M.npz"):
        print("Loading ingredients...", end='')
        # load valid ingredients from simplified-recipes-1M, obtained from https://dominikschmidt.xyz/simplified-recipes-1M/
        with np.load(path+"simplified-recipes-1M.npz") as data:
            ingredients = list(data['ingredients'])
        print("done.")
        openedFile = True

    #recipe dataset obtained from: https://recipenlg.cs.put.poznan.pl/dataset
    if os.path.isfile(path +  "full_dataset.csv"):
        print("Loading ingredients...", end='')
        recipes = pd.read_csv(path+"full_dataset.csv")
        print("done.",)
        print("Loading recipes...")
        raw = recipes['NER'].tolist()
        print("done.")

        print("Formatting ingredients...")

        ingredients_raw = []
        print("  Changing type to list...", end='')
        for row in raw:
            ingredients_raw = ast.literal_eval(row)
        print("done.")
        
        print("  Creating singular list...", end='')
        
        ingredients.extend([j for i in ingredients_raw for j in i])
        print("done.")

        print("Completed.")

        openedFile = True
    
    #recipe dataset obtained from: https://www.kaggle.com/datasets/kaggle/recipe-ingredients-dataset
    if os.path.isfile(path + "Ingredients.json"):
        print("Loading ingredients...", end='')
        sheet = pd.read_json(path+"Ingredients.json")

        ingredients_raw = sheet['ingredients'].tolist()
        print("done.")
        
        print("  Creating singular list...", end='')
        
        ingredients.extend([j for i in ingredients_raw for j in i])
        print("done.")        

        openedFile = True
    
    if not openedFile:
        sys.exit("Invalid recipe dataset. Make sure file name is correct.")

    print("  Making all ingredients lowercase...", end='')
    ingredients = [i.lower() for i in ingredients]
    print("done.")
    print("  Removing duplicates...", end='')
    ingredients = [*set(ingredients)]
    print("done.")

    return ingredients


def cleanIngredients(sheet, ingredients, recipe_Col):
    #loop through each row
    for index, row in sheet.iterrows():
        print("\r", end='')
        print("Current row: ", index, "out of ", len(sheet[recipe_Col]), end='')
        #loop over each column
        for col in sheet.columns:
            if col == recipe_Col:
                #print("sheet[col][index]: ", sheet[col][index][0])
                #print("type(sheet[col][index]): ", type(sheet[col][index][0]))
                #make all ingredients lowercase
                sheet[col][index] = sheet[col][index].lower()
                
                #convert list in a string type to list
                recipeIngredients = ast.literal_eval(sheet[col][index])

                #loop through each list ingredient and extract useful/valid information
                for i in range(len(recipeIngredients)):
                    #get rid of non alpha-numeric characters
                    recipeIngredients[i] = re.sub("([\(\[]).*?([\)\]])", "\g<1>\g<2>", recipeIngredients[i])
                    recipeIngredients[i] = re.sub(r'\W+', ' ', recipeIngredients[i])
                    #print("recipeIngredients[i]: ", recipeIngredients[i])
                    #keeps track of ingredients in recipe that exist in imported ingredients list
                    goodIngredients = []
                    
                    words = recipeIngredients[i].split(' ')
                    #loop over each ingredient
                    for word in words:
                        #print("Checking word: ", word)
                        if len(word) < 3:
                            continue
                        if word in words_to_avoid or word in goodIngredients:
                            continue
                        if word in ingredients or word in approved_words:
                            #add it to goodIngredients if not in words_to_avoid or word in approved_words
                            goodIngredients.append(word)
                            #print("Added word to goodIngredients: ", word)
                    
                    #print("goodIngredients: ", goodIngredients)

                    #if there is at least one valid word, it is a valid ingredient so add it to
                    #the current recipe ingredients list
                    if len(goodIngredients) != 0:
                        recipeIngredients[i] = ' '.join(goodIngredients)
                    else:
                        # Commented code is for attempting to fill ingredients not found in the
                        # imported ingredients list. e.g. 1/2 g kimchi might not be found as
                        # a valid ingredient, but this code would attempt to clean all common
                        # words/numbers that are not part of the ingredient name. I found it 
                        # not as effective as I would want so I am commenting it out and instead
                        # just deleting ingredients that are not found.
                            #print("words: ", words)
                            #
                            #words = [word for word in words if not word.isnumeric()]
                            #print("removing ingredient: ", words)
                            #for word in measurements:
                            #    if word in words:
                            #        print("found word in words: ", word)
                            #        words.remove(word)
                            #recipeIngredients[i] = ' '.join(words)

                        #if there is no valid word, remove ingredient altogether
                        recipeIngredients[i] = None
                        continue
                    
                    #try to find the closest matching ingredient name to word
                    #closestI = difflib.get_close_matches(recipeIngredients[i], ingredients, cutoff=0.9)
                    #print("closestI: ", closestI)

                    #if there is a close match, add that ingredient to recipe
                    #if closestI:
                        #print("adding ingredient " + closestI[0])
                        #recipeIngredients[i] = closestI[0]
                        
                    #if there is not a good match, split into individual words and test every permutation
                    #until a valid ingredient is found
                    if recipeIngredients[i] not in ingredients:
                        subIng = recipeIngredients[i].split(' ')

                        #print("Ingredient not in ingredients. Checking permutations")
                        #print("recipeIngredients[i]: ", recipeIngredients[i])
                        
                        #get all possible permutations into a list
                        allComb = list()
                        tempComb = list()
                        for j in range(len(subIng)):
                            if j>4:
                                break
                            tempComb.append(itertools.permutations(subIng, j+1))
                        for j in range(len(tempComb)):
                            for perm in tempComb[j]:
                                allComb.append(list(perm))
                        #print("allComb: ", allComb)

                        #print("Checking all permutations...")

                        #for each permutation in reverse order (starting at biggest words)
                        for perm in reversed(allComb):
                            #print("perm: ", perm)

                            #if no valid permutations, don't add any ingredient
                            if not perm:
                                recipeIngredients.remove(recipeIngredients[i])
                                i-=1
                                continue
                            
                            perm = ' '.join(perm)

                            #print("Checking for substring as ingredient: ", perm)
                            #closestI = difflib.get_close_matches(perm, ingredients, cutoff=1)
                            #print("closestI: ", closestI)
                            if perm in ingredients_to_avoid:
                                continue
                            #if permutation is a valid ingredient, add it to ingredient list
                            if perm in ingredients:
                                recipeIngredients[i] = perm
                                break
                lengthRI=len(recipeIngredients)
                j=0
                #remove any None values in recipe ingredients
                while j < lengthRI:
                    if recipeIngredients[j] == None or recipeIngredients.count(recipeIngredients[j]) > 1:
                        recipeIngredients.remove(recipeIngredients[j])
                        j-=1
                        lengthRI-=1
                    j+=1

                #print(sheet['Title'][index])
                #print("FINAL recipeIngredients: ", recipeIngredients)

                #add cleaned ingredients over previous ones
                sheet[col][index] = recipeIngredients
    return sheet


def main():
    #CLA argument definitions
    parser = argparse.ArgumentParser("Copy recipe data set, clean it, and output in a new file.\n")
    parser.add_argument('--oldfile', '-f', type=str, required=True, help="File containing uncleaned recipe data.")
    parser.add_argument('--column', '-c', type=str, required=True, help="Row name with recipes.")
    parser.add_argument('--newfile', '-n', type=str, required=True, help="New file to copy cleaned data into.")
    parser.add_argument('--overwriteFile', '-o', action='store_false', help="Give warning about overwriting a pre-existing file.")
    args = parser.parse_args()

    #read CLA for uncleaned data file and new data file name
    oldFile = os.getcwd() + "\\Datasets\\" + args.oldfile
    newFile = os.getcwd() + "\\Cleaned_Datasets\\" + copyFile(args)

    #get a copy of the sheet from the old file
    if oldFile.endswith(".csv"):
        sheet = pd.read_csv(oldFile)
    if oldFile.endswith(".json"):
        print("Loading recipes into program.")
        sheet = pd.read_json(oldFile)
        print("Finished")
        # I NEED TO FIGURE OUT HOW TO CONVERT THE 1M DATASET INTO
        # A SINGLE LIST
        row = 0
        ingredients = []
        print("Formatting recipes...")
        for recipe in sheet['ingredients']:
            rIng = []
            for ingredient in recipe:
                rIng.append(ingredient['text'])
            #print("sheet['ingredients'][row]: ", sheet['ingredients'][row])
            #print("TTYYYPPPEEEEEE (sheet['ingredients'][row]): ", type(sheet['ingredients'][row]))
            sheet['ingredients'][row] = rIng
            #print("sheet['ingredients'][row]: ", sheet['ingredients'][row])
            #print("TTYYYPPPEEEEEE (sheet['ingredients'][row]): ", type(sheet['ingredients'][row]))
            row += 1
            print("\r", end='')
            print("Current row: ", row, "out of ", len(sheet['ingredients']), end='')
        print("done.")
    print(sheet.info)


    ingredients = loadIngredients()

    #replace any empty cells with NaN
    sheet = sheet.replace('', np.nan)

    #drop all recipes with NaN value for Title or Ingredients
    sheet = sheet.dropna(subset=[args.column])
    
    print("Cleaning recipes...")
    #clean recipes into useful format (only ingredient names)
    sheet = cleanIngredients(sheet, ingredients, args.column)
    print("Completed.")

    #print(sheet.head())
    #print(sheet.info())
    #print(sheet.describe())

    print("Copying to file " + args.newfile + "...")
    #copy sheet into a new file
    sheet.to_csv(newFile, index=False)
    print("Completed.")
    return

if __name__ == "__main__":
    main()