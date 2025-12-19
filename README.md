# Ionospheric Effects of Geromagnetic Storms under Increasing Greenhouse Gas Concentrations
## Project Description
This project aims to predict the effects of geomagnetic storms on the ionosphere as greenhouse gas concentrations rises.
The ionosphere is primarily influenced by three broad parameters:
1. Solar activity
2. Geomagnetic Activity
3. Greenhouse gas concentrations
While these parameters are largely independent, increasing greenhousegas concentrations may modulate how geomagnetic storms and solar activity impact the ionosphere. This project investigates the interactions and the relative importance of each factor.
# Objectives
The project seeks to achueve the following objectives:
1. Quantify the relative effects of geomagnetic storms, solar activity, and greenhouse gases on       the ionosphere, confirmming previous research and ranking their impacts from most to least         significant.
2. Investigate interactions between grenhouse gases and geomagnetic storms or solar activity in       influencing ionospheric variability.
3. Determine modulatory effects, specifically whether greenhouse gases significally alter the         impact of geomagnetic storms or solar activity on ionospheric parameters.
# Data Sources
## Geomagnetic Storm Data
Hourly DST, KP, and Ap indices were obtained from 1960 till 2024, with the analysis done with the daily average of the data. Data source: Kyoto World Data Center - https://wdc.kugi.kyoto-u.ac.jp/dstae/index.html
## Greenhouse gas Data
Daily CO2 concentration data were used to represent greenhouse gas levels from 1974 till 2024. Data source: Mauna Lao Observatory, NOAA GML - https://gml.noaa.gov/obop/mlo/
## Solar Activity Data
Solar activity data was represented using solar cycle phase numbers, feature-engineered from the geomagnetic indices and coresponding dates.
## Ionospheric Data
Three ionospheric parameter data was employed in this project to give an overall view of changes in the ionosphere. 
1. Total Electron Content Data - TEC data
2. F2-layer Critical Frequency - foF2 data
3. F2-layer Peak Height Data - hmF2 data
This data was downloaded from 1982 till 2024.
Data source for all three: GIRO Ionosode Data from Roquetes Spain - https://giro.uml.edu/didbase/scaled.php 
# Methodology
The machine learning models pyGAM (Primary model) and CNN (Secondary and confirmatory model) were trained on the geomagnetic, solar activity and greenhouse gas data to predict the target data the ionospheric parameters TEC, foF2 and hmF2. This was done in-line with the objectives stated earlier.
# Python libraries used
numpy
pandas
matplotlib
seaborn
pyGAM
scikit-learn
SHAP
tensorflow
CNN
# Repository Structure
--- Final year project (8).ipynb (This file contains the pyGAM analysis and majority of the project)
--- CNN_Part_of_Final_Year_project.ipynb (This contains the CNN part of the final year project)
--- README
# Note:
Data files are included in this repository due to size limitations. Users are expected to download the datasets direclty from the the original sources listed above, and combine them using excel.

# Project Supervisor
Dr. H.A. Lawal

# Author
Babalola-Jacobs Oluwasegun David
Final Year Undergraduate Project

# License
This project is intended for academic and research purposes.
Please cite appropriately if using any part of this work.

if you use this project, please cite it as:
Babalola-Jacobs, O.D. (2025). Predicting the Effects of Geomagnetic Storms on the Ionosphere under Increasing Greenhouse Gas Concentrations.
Final-Year Undergraduate Project.
Department of Physics, Air Force Institute of Technology, Kaduna.
