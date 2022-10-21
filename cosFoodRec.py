########################################################
#
#   Author:     Ryan Quinn
#   Class:      Artificial Intelligence 1 (Independent Study)
#   Professor:  Dr. Dylan Schwesinger
#   Project:    Independent project
#   Semester:   Fall 2022
#
#   Filename:   cosFoodRec.py
#   Purpose:    Recommends recipes based on cosine similarity
#               between different recipe ingredients.
#
########################################################

import pandas as pd
import difflib
import os
import ast
import random
import argparse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

pd.options.mode.chained_assignment = None

def checkCLA():
    #CLA argument definitions
    parser = argparse.ArgumentParser("Copy recipe data set, clean it, and output in a new file.\n")
    parser.add_argument('--datafile', '-f', type=str, required=True, help="File containing cleaned recipe data.")
    parser.add_argument('--usetitle', '-t', action='store_true', help="Take into consideration the name of a recipe for recommendations.")
    args = parser.parse_args()

    print("Loading data...", end='', flush=True)
    # import recipe data
    recipeSheet = pd.read_csv(os.getcwd() + '\\Cleaned_Datasets\\' + args.datafile)

    if len(recipeSheet) > 50000:
        exit("\nFile size limited to 50,000 rows to prevent high memory usage.")
    
    return recipeSheet, args

def getRecipes(args, recipeSheet):
    recipes = recipeSheet['ingredients']

    print("done.\nGetting feature vector...", end='', flush=True)

    #convert recipe strings into lists
    recipes = [ast.literal_eval(recipe) for recipe in recipes]
    recipes = list(map(sorted, recipes))
    #convert recipe lists into simplified string
    recipes = [' '.join(recipe) for recipe in recipes]
    
    #If titles are used in feature vector, the similarity will be more biased towards
    #similarly named recipes. I have added in a flag to use them as it can be useful
    #for getting similar recipes.

    if args.usetitle:
        titles = recipeSheet['title']
        titles[:] = [' ' + s for s in recipeSheet['title']]
        recipes = recipes + titles

    #convert recipes into feature vectors
    vectorizer = TfidfVectorizer()
    featureVector = vectorizer.fit_transform(recipes)

    print("done.\nGetting cosing similarity...", end='', flush=True)

    if args.usetitle:
        print("\nUsing titles.")
        titles[:] = [s[1:] for s in recipeSheet['title']]
    
    return recipes, featureVector

def getRecipeID(recipeSheet):
    #get valid recipe
    while True:
        recipeName = input("Enter recipe: ")
        if recipeName not in recipeSheet['title'].tolist():
            recipeName = difflib.get_close_matches(recipeName, recipeSheet['title'].tolist(), cutoff=0.5)
            num = 0
            try:
                num = int(input("No direct match found. Enter the corresponding"+
                            " number (1-3) for the following recipes:\n"+
                            "1. "+recipeName[0]+" \n2. "+
                            (recipeName[1] if len(recipeName)>1 else "None")+"\n3. "+
                            (recipeName[2] if len(recipeName)>2 else "None")+"\n"
                            "\nor (4-5) for the following options:\n4. re-enter recipe name\n5. quit.\n"))
            except:
                print("No close recipe names found. Try entering a different recipe name.")
            
            if (len(recipeName) == 1 and (num == 2 or num == 3)) or (len(recipeName) == 2 and num == 3):
                print("Please make a valid recipe selection")
                continue
            
            if (num == 1 or num == 2 or num == 3):
                recipeName = recipeName[num-1]
                break
            elif (num == 4):
                continue
            elif (num == 5):
                return
            else:
                print("Invalid input. Please enter a new recipe.")
        else:
            break
    #get the index of selected recipe
    recipeIdx = recipeSheet[recipeSheet['title'] == recipeName]['index'].values[0]

    return recipeIdx, recipeName

def printRecipes(recipeSheet, sortedSim):
    print("\nRecommended recipes")
    print("----------------------------------------")
    i = 0
    j = 1
    #print out similar values starting from most similar
    while True:
        i += random.randint(1, 3) #add a little bit of randomness to recommended recipes
        try:
            print((recipeSheet[recipeSheet['index'] == sortedSim[i][0]].values[0])[4]) #title
            print((recipeSheet[recipeSheet['index'] == sortedSim[i][0]].values[0])[2]) #link

            ingredients = ast.literal_eval((recipeSheet[recipeSheet['index'] == sortedSim[i][0]].values[0])[1])
            print("Ingredients:", ", ".join(ingredients)) #ingredients
        except:
            #error printing, error in cleaned data, or reached end of sortedSim
            print("Error retrieving recipe information. Please enter a different recipe or select a different dataset.")
            break
        #print out 5 recipes
        if j%5 == 0:
            print("----------------------------------------")
            more = input("\nWould you like to see more recipes? (y/n): ").lower()
            if more != 'y':
                break
            print("\n----------------------------------------")
        j+=1
        print("")
    return

def main():
    #check CLA and open cleaned recipes file
    recipeSheet, args = checkCLA()

    #get recipes from file and a feature vector
    recipes, featureVector = getRecipes(args, recipeSheet)

    #get cosine similarity between recipes
    cosSim = cosine_similarity(featureVector)

    print("done.\n", flush=True)

    #allow user to continue to enter different recipes into program
    while True:
        choice = 0
        while choice not in [1, 2, 3]:
            try:
                choice = int(input("Enter number of choice:\n1. Enter recipe name.\n2. Random recipe.\n3. Quit\n"))
            except:
                print("Invalid choice, please enter a number 1-3")

        if choice == 1:
            recipeIdx, recipeName = getRecipeID(recipeSheet)
        elif choice == 2:
            recipeName = random.choice(recipeSheet['title'])
            #get the index of selected recipe
            recipeIdx = recipeSheet[recipeSheet['title'] == recipeName]['index'].values[0]
        else:
            return        

        print("\nFinding similar recipes to \"" + recipeName + '\"')
        ingredients = ast.literal_eval((recipeSheet[recipeSheet['title'] == recipeName].values[0])[1])
        print("Ingredients: ", ", ".join(ingredients))

        #get list of this recipe's similarity scores
        recSim = list(enumerate(cosSim[recipeIdx]))

        #sort list so most similar recipes are at front
        sortedSim = sorted(recSim, key=lambda x:x[1], reverse=True)
        
        printRecipes(recipeSheet, sortedSim)
    return

if __name__ == "__main__":
    main()