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
ingredients_to_avoid = ["green", "white"]

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
        sys.exit("Permission to copy into new file denied.")
    except:
        sys.exit("There was a problem copying data to new file. Make sure a only a valid file name is entered.")
    
    return fileName

def loadIngredients(file):
    print("file: ", file)
    path = os.getcwd() + "\\Datasets\\"
    ingredients = []
    if file == 'simplified-recipes-1M.npz':
        # load valid ingredients from simplified-recipes-1M, obtained from https://dominikschmidt.xyz/simplified-recipes-1M/
        with np.load(path+file) as data:
            ingredients = data['ingredients']

    elif file == "full_dataset.csv":
        print("Loading ingredients...")
        #recipe dataset obtained from: https://recipenlg.cs.put.poznan.pl/dataset
        recipes = pd.read_csv(path+file)
        print("Completed.")
        print("Loading recipes...")
        raw_ingredients = recipes['NER'].tolist()
        print("Completed.")

        print("Formatting ingredients...")

        print("  Changing type to list...", end='')
        for row in raw_ingredients:
            ingredients.append(ast.literal_eval(row))
        print("done.")
        
        print("  Creating singular list...", end='')
        
        ingredients = [j for i in ingredients for j in i]
        print("done.")
        print("  Making all ingredients lowercase...", end='')
        ingredients = [i.lower() for i in ingredients]
        print("done.")
        print("  Removing duplicates...", end='')
        ingredients = [*set(ingredients)]
        print("done.")

        print("Completed.")
    
    #recipe dataset obtained from: https://www.kaggle.com/datasets/kaggle/recipe-ingredients-dataset
    elif file == "Ingredients.json":
        sheet = pd.read_json(path+file)

        ingredients = sheet['ingredients'].tolist()
        
        print("  Creating singular list...", end='')
        
        ingredients = [j for i in ingredients for j in i]
        print("done.")
        print("  Making all ingredients lowercase...", end='')
        ingredients = [i.lower() for i in ingredients]
        print("done.")
        print("  Removing duplicates...", end='')
        ingredients = [*set(ingredients)]
        print("done.")
    
    return ingredients
    


def cleanIngredients(sheet, ingredients):
    #loop through each row
    for index, row in sheet.iterrows():
        print("current row: ", index)
        #loop over each column
        for col in sheet.columns:
            if col == "Cleaned_Ingredients":
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

                    #if there is at least one valid word, then it is a valid ingredient and add it to
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
                            if j>2:
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
                            
                            perm = ' '.join(perm)

                            #print("Checking for substring as ingredient: ", perm)
                            #closestI = difflib.get_close_matches(perm, ingredients, cutoff=1)
                            #print("closestI: ", closestI)

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

                print(sheet['Title'][index])
                print("FINAL recipeIngredients: ", recipeIngredients)

                #add cleaned ingredients over previous ones
                sheet[col][index] = recipeIngredients
    return sheet


def main():
    #CLA argument definitions
    parser = argparse.ArgumentParser("Copy recipe data set, clean it, and output in a new file.\n")
    parser.add_argument('--oldfile', '-f', type=str, help="File containing uncleaned recipe data.")
    parser.add_argument('--newfile', '-n', type=str, help="New file to copy cleaned data into.")
    parser.add_argument('--ingdata', '-i', type=str, help="File containing ingredient list.")
    parser.add_argument('--overwriteFile', '-o', action='store_false', help="Give warning about overwriting a pre-existing file.")
    args = parser.parse_args()

    #read CLA for uncleaned data file and new data file name
    oldFile = os.getcwd() + "\\Datasets\\" + args.oldfile
    newFile = os.getcwd() + "\\Cleaned_Datasets\\" + copyFile(args)

    #get a copy of the sheet from the old file
    sheet = pd.read_csv(newFile)

    ingredients = loadIngredients(args.ingdata)

    #replace any empty cells with NaN
    sheet = sheet.replace('', np.nan)

    #drop all recipes with NaN value for Title or Ingredients
    sheet = sheet.dropna(axis="rows", subset=['Title', 'Cleaned_Ingredients', 'Ingredients'])
    
    print("Cleaning ingredients...")
    #clean recipes into useful format (only ingredient names)
    sheet = cleanIngredients(sheet, ingredients)
    print("Completed.")

    print(sheet.head())
    print(sheet.info())
    print(sheet.describe())

    print("Copying to file " + args.newfile + "...")
    #copy sheet into a new file
    sheet.to_csv(newFile, index=False)
    print("Completed.")
    return

if __name__ == "__main__":
    main()