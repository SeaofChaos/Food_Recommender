# Food Recommender
> A simple food recommendation program.

This food recommender is a simple food recommendation program designed
to give you similar recipes to anything you may be craving. Just enter
in a meal and the let the program work its magic. You will be returned
a list of different recipes and their corresponding website where you
can view them at the source.

## Installation
In order to run this program, all you need to do is install the libraries
found in `requirements.txt`.
Python and PIP are required.

Run the following command to install them:

```
pip install -r /path/to/requirements.txt
```

***It's highly recommended (but not necessary) to work inside a virtual 
environment to avoid any possible version conflicts.***

## Usage
### [cleanRecipeData.py](/cleanRecipeData.py)
```
usage: Copy recipe data set, clean it, and output in a new file.
 [-h] --oldfile OLDFILE --column COLUMN --newfile NEWFILE [--overwriteFile] [--removeDup]

options:
  -h, --help            show this help message and exit
  --oldfile OLDFILE, -f OLDFILE
                        File containing uncleaned recipe data.
  --column COLUMN, -c COLUMN
                        Column name with ingredients.
  --newfile NEWFILE, -n NEWFILE
                        New file to copy cleaned data into.
  --overwriteFile, -o   Give warning about overwriting a pre-existing file.
  --removeDup, -d       Remove duplicate recipe names.
```

### [cosFoodRec.py](/cosFoodRec.py)
```
usage: Copy recipe data set, clean it, and output in a new file.
 [-h] --datafile DATAFILE [--usetitle]

options:
  -h, --help            show this help message and exit
  --datafile DATAFILE, -f DATAFILE
                        File containing cleaned recipe data.
  --usetitle, -t        Take into consideration the name of a recipe for recommendations.
```


## Methodology
### Inspiration
The food recommender was built as a continuation of my previous semester's
project from my software engineering class. I was part of a group that 
worked together to create a meal planner web application. This was the
initial inspiration. We had created a fully functioning website, and had 
plans to build a recommendation system, but is was cut out and the project's
direction was focused now on its meal planner. I want to explore topics dealing 
with the collection and cleaning of data, using this data with artificial 
intelligence, and producing results that would've been useful to our previous 
project that we never fully completed. 

### Implementation
One of the most difficult challenges I faced was procuring clean data which I
could use for my specific purpose. While there were a lot of datasets available, 
most had recipes that contained large ingredients (e.g. "8 skinless, boneless 
chicken thighs") and random information dealing with the instructions and such. 
In my case, I only desired the ingredient information for each recipe (e.g. 
"chicken thights"), so I had to first create a program to clean up the congested 
data.

In order to find similar recipes, I decided that a simple yet effective way would 
be to create a cosine similarity between the different recipes using feature
vectors. This method is useful for finding similar items based on keywords. 

#### [cleanRecipeData.py](/cleanRecipeData.py)
I determined that the AI algorithm would be based on the ingredient names alone, 
so I would first need to clean the recipe data. After removing any invalid rows, 
the uncleaned dataset is run through an algorithm that tries to extract only the 
direct ingredient name. To do this, I compared each ingredient name against a dataset
which only contained cleaned ingredients (e.g. 'broccoli', 'chicken breast', 'spam', 
...). If no valid ingredient name was found, it would look at all possible
permutations of the ingredient and determine which is most valid. If no valid
ingredient was found, then it is removed.

Any uncleaned datasets should be placed inside the `Datasets` folder to use. The 
cleaned datasets will be saved to the `Cleaned_Datasets`.

#### [cosFoodRec.py](/cosFoodRec.py)
The AI algorithm I chose was based on content-based filtering. This is an approach
where the discrete characteristics of an item are compared to other items. While 
the algorithm is simple, it is useful for me and the overall purpose of this 
program. In the future it may be useful to combine this along with collaborative
filtering, which will base the recommendations on past user behavior, but that's 
a much more complicated approach than what is needed. In my case, I decided to base 
this comparison on the recipe ingredients and optionally the recipe name. 

Once the program is ran, it will load in all the recipe information and create
similarity vectors for all of them. You have the option to search for recipes or
to get a random one. Once you enter a recipe, you will get similar recipes 5
at a time. You can then either choose to get more recommendations for the
current recipe or to enter in a new one. 

## Conclusion
This project was a lot of fun to implement while working with both data cleaning
and AI. The challenges of using feature vectors and cosine similarity are the main 
takeaways. Figuring out how to create, implement, and get the desired results from 
them was an important part of this project. For my specific use, this method worked 
wonderfully. 

Cleaning the data was also a large challenge in this project. I never had much 
experience dealing with it so I had to learn all about pandas, dataframes, and 
working different file types (like json and csv) all by myself. Another area I had
to focus on was writing efficient code. I learned that when working with tens of
thousands of data entries, I had to be quick when doing computations on each one. 

Overall I'm happy with the way the project turned out. I learned a lot and am now a
lot more comfortable cleaning data and working with AI algorithms. I probably won't 
be spending much more time on it, although I may add in a simple UI to make it more user
friendly. 