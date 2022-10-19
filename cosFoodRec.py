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

import numpy as np
import pandas as pd
import difflib
import cv2
import os
import ast
import time
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

################################
#   To do:
#
#   1. If I have extra time, add in some error checking
#   2. Limit file size 
#       to prevent an enormous cosine matrix. 
#   3. Make input file dynamic and
#       not set to the 15k file every time. 
#   4. COMMENT.
#   5. SORT RECIPE NAMES BEFORE CALCULATING SIMILARITY
################################

def main():
    print("Loading data...", end='', flush=True)
    # import recipe data
    recipeSheet = pd.read_csv(os.getcwd() + '\\Cleaned_Datasets\\CleanedTest15k.csv')

    recipes = recipeSheet['ingredients']

    print("done.\nGetting feature vector...", end='', flush=True)

    #convert recipes into string
    recipes = [ast.literal_eval(recipe) for recipe in recipes]
    for recipe in recipes:
        recipe = recipe.sort()
    recipes = [' '.join(recipe) for recipe in recipes]

    #convert recipes into feature vectors
    vectorizer = TfidfVectorizer()
    featureVector = vectorizer.fit_transform(recipes)

    print("done.\nGetting cosing similarity...", end='', flush=True)

    #get cosine similarity between recipes
    cosSim = cosine_similarity(featureVector)

    print("done.\n", flush=True)

    choice = 0
    while choice not in [1, 2, 3]:
        try:
            choice = int(input("Enter number of choice:\n1. Enter recipe name.\n2. Random recipe.\n3. Quit\n"))
        except:
            print("Invalid choice, please enter a number 1-3")

    if choice == 1:
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
    elif choice == 2:
        recipeName = random.choice(recipeSheet['title'])
        #get the index of selected recipe
        recipeIdx = recipeSheet[recipeSheet['title'] == recipeName]['index'].values[0]
    else:
        return        

    print("\nFinding similar recipes to \"" + recipeName + '\"')

    #get list of this recipe's similarity scores
    recSim = list(enumerate(cosSim[recipeIdx]))

    #sort list so most similar recipes are at front
    sortedSim = sorted(recSim, key=lambda x:x[1], reverse=True)
    
    print("\nRecommended recipes")
    print("----------------------------------------")
    i = 1
    #print out similar values starting from most similar
    while True:
        print((recipeSheet[recipeSheet['index'] == sortedSim[i][0]].values[0])[4])
        #print out 5 recipes
        if i%5 == 0:
            print("----------------------------------------")
            more = input("\nWould you like to see more recipes? (y/n): ").lower()
            if more != 'y':
                break
            print("\n----------------------------------------")
        i+=1

    return


if __name__ == "__main__":
    main()