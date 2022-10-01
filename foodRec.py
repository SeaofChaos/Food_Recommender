import numpy as np
import pandas as pd
import cv2
import sys
import os

def main():
    #if len(sys.argv) != 2:
    #    sys.exit("Usage: python " + sys.argv[0] + " data_file")
    recipeSheet = pd.read_csv(os.getcwd() + '\\Cleaned_Datasets\\CleanedData_1M.csv')

    recipes = recipeSheet['ingredients']

    return


if __name__ == "__main__":
    main()