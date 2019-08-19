# Home Oslo Home
Everyone needs a place to call 'home, sweet home', however finding the right home at the right price seems to be a complicated process. Normally one would go about and view as many properties as possible in order to get an intuition of the property market. However each viewing takes at least 1.5 hours (including transport). This poses a challenge - one can complete no ore than 2 viewings per day on weekdays and probably 4 in weekends. Considering 100 viewings enough to build a certain intuition of the property market, one would need at least 5 full weeks of dedicated property hunting. And that is just in order to be able to decide which price is right...

Not doing real estate evaluation professionally then comes with the challenge that one may need to look for months before one finds a good property at a reasonable price. The purpose of this project is threefold:

* To help the author dispell their insecurities about purchasing a property;
* To understand the trends that drive property prices in Oslo;
* To build a model that predicts the asking price of properties in Oslo;

## Abstract
For this project we explore a set of 2000 real estate ads and investigate the trends in prices. We enrich the data using additional data on:

* The post codes in Oslo;
* Statistics from the National Health Institute;
* Places of interest in Oslo, available on Google Maps;

Finally, we attempt to build a simple model based on all datasets. We validate the model and compare the results to a benchmark of the median home prices by settlement or municipality (where available).

## News And Updates
We are delighted to announce that this project has servec its purpose and the author has found a place to call 'home, Oslo home.'

## Software Prerequisites
To install the necessary libraries, use the `requirements.txt` file.

## Running The Notebooks
The project has two main notebooks

* `eda.ipynb`- contains the Exploratory Data Analysis;
* `training_pipeline.ipynb` - contains the training scripts;

In addition, there are several supporting notebooks:

* `extract_gmaps_places_attributes.ipynb` - contains scripts for extracting places of interest in Oslo using the Google Maps API.
* `irs_data.ipynb` - contains scripts for extracting tax and income statistics from the Norwegian IRS.