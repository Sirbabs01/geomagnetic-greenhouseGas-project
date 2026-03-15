# Ionospheric Effects of Geomagnetic Storms under Increasing Greenhouse Gas Concentrations
## Project Overview

This project investigates how geomagnetic storms influence the ionosphere under increasing greenhouse gas concentrations. The ionosphere is a dynamic region of the upper atmosphere that plays a critical role in radio communication, satellite navigation, and space weather processes.

Ionospheric variability is driven primarily by three major factors:

Solar activity

Geomagnetic activity

Atmospheric composition (greenhouse gases)

While solar and geomagnetic drivers are well-established influences on the ionosphere, the long-term effects of rising greenhouse gas concentrations on ionospheric behaviour remain an active area of research.

This project explores how these three drivers interact and evaluates their relative importance in determining ionospheric variability using statistical analysis and machine learning models.

## Objectives

This project aims to achieve the following objectives:

Quantify the relative effects of solar activity, geomagnetic storms, and greenhouse gas concentrations on ionospheric parameters.

Investigate nonlinear relationships between ionospheric parameters and their drivers using machine learning methods.

Examine interaction effects between geomagnetic activity and greenhouse gases to determine whether greenhouse gases modulate how geomagnetic storms affect the ionosphere.

## Data Sources
### Geomagnetic Activity Data

Hourly geomagnetic indices were obtained and averaged daily.

Indices used:

Dst index

Kp index

Ap index

Time range: 1960 – 2024

Source: Kyoto World Data Center
https://wdc.kugi.kyoto-u.ac.jp/dstae/index.html

### Greenhouse Gas Data

Daily CO₂ concentration data were used as a proxy for greenhouse gas levels.

Time range: 1974 – 2024

Source: Mauna Loa Observatory – NOAA Global Monitoring Laboratory
https://gml.noaa.gov/obop/mlo/

### Solar Activity Data

Solar activity was represented using solar cycle phase numbers, which were feature-engineered from geomagnetic indices and their corresponding dates. This allowed the model to capture the periodic nature of solar activity across multiple solar cycles.

### Ionospheric Data

Three ionospheric parameters were analyzed:

Total Electron Content (TEC)

F2-layer critical frequency (foF2)

F2-layer peak height (hmF2)

Time range: 1982 – 2024

Source: GIRO Ionosonde Data (Roquetes, Spain)
https://giro.uml.edu/didbase/scaled.php

## Methodology

The analysis involved several stages:

### Exploratory Data Analysis

Time-series plots were generated for all independent and dependent variables.

Results showed that:

Solar activity

Geomagnetic indices

Ionospheric parameters

all exhibited strong periodic behaviour consistent with solar cycles.

This suggested that solar activity may be a dominant driver of ionospheric variability, influencing both geomagnetic disturbances and ionospheric responses.

In contrast, CO₂ concentrations showed a non-stationary increasing trend, reflecting long-term atmospheric changes.

Scatter plots and correlation coefficient analysis were also performed. These analyses revealed that:

Relationships between geomagnetic indices and ionospheric parameters were highly nonlinear

Most geomagnetic data clustered within low disturbance levels (0 to −50 nT)

This indicated that simple linear models would be insufficient to describe these relationships.

### Machine Learning Modeling

Two machine learning approaches were used:

#### Primary Model

Generalized Additive Models (pyGAM)

pyGAM was used because it can effectively model nonlinear relationships between predictors and response variables.

The model included:

Solar cycle phase

CO₂ concentration

Geomagnetic indices

Partial dependence plots were used to analyse how each variable influenced the ionospheric parameters.

Model performance was evaluated using:

Total variance explained

AIC (Akaike Information Criterion)

GCV (Generalized Cross Validation)

#### Secondary Model (Validation)

A Convolutional Neural Network (CNN) model was trained to independently validate the results obtained from the pyGAM model.

The CNN model was analyzed using SHAP (SHapley Additive Explanations) to determine the relative contribution of each parameter to ionospheric variability.

## Results
### Dominant Drivers of Ionospheric Variability

Model comparisons revealed that:

Solar activity was the strongest driver of ionospheric variability

Greenhouse gas concentrations had a measurable but smaller influence

Geomagnetic indices contributed the least explanatory power

Across several evaluation metrics, solar and greenhouse gas parameters performed 5–10 times better than geomagnetic indices in explaining ionospheric variability.

This result was somewhat unexpected, as geomagnetic storms are traditionally considered important drivers of ionospheric disturbances.

### Interaction Effects

Interaction effects between CO₂ concentration and geomagnetic activity were investigated using tensor spline interactions within the pyGAM model.

The analysis suggested that:

CO₂ levels modulate how the ionosphere responds to geomagnetic storms

At higher CO₂ concentrations, the TEC response to geomagnetic disturbances becomes smoother and less chaotic

At lower CO₂ levels:

TEC responses exhibited larger fluctuations

Storm-time variability was more pronounced.

At higher CO₂ levels:

TEC values shifted toward more positive levels

Variability during geomagnetic disturbances decreased.

This suggests that increasing greenhouse gas concentrations may reduce the sensitivity of the ionosphere to geomagnetic disturbances over long timescales.

#### Reverse Interaction Analysis

The reverse interaction was also tested to determine whether geomagnetic activity modulates greenhouse gas effects.

Results showed that:

Geomagnetic disturbances could temporarily alter the periodic patterns associated with greenhouse gas influence.

However, these effects appear limited due to the short duration of intense geomagnetic storms.

### CNN and SHAP Validation

The CNN model confirmed the major findings of the pyGAM analysis.

SHAP analysis revealed:

Strong contributions from solar activity

Moderate contributions from greenhouse gas concentrations

Weak contributions from geomagnetic indices

Interaction strength between greenhouse gases and geomagnetic activity was found to be weak to moderate, with mutual information scores ranging from 0.05 to 0.15.

However, stronger interaction was observed between solar activity and greenhouse gas concentrations.

## Conclusions

The results of this study suggest that:

Solar activity remains the dominant driver of ionospheric variability.

Greenhouse gas concentrations may play a larger role in ionospheric behaviour than previously assumed.

Geomagnetic storms appear to contribute less to long-term ionospheric variability than expected, although they remain important during short-term disturbances.

Increasing greenhouse gas concentrations may gradually modify the ionosphere's response to geomagnetic storms, potentially reducing storm-time variability over long timescales.

These findings raise interesting questions regarding the future behaviour of the ionosphere under continued atmospheric change. As greenhouse gas concentrations continue to rise, the relative importance of geomagnetic storms in shaping ionospheric variability may evolve.

## Repository Structure
├── Final_Year_Project.ipynb
│   Main notebook containing the pyGAM analysis
│
├── CNN_Part_of_Final_Year_Project.ipynb
│   CNN model implementation and SHAP analysis
│
├── Undergraduate_Project_Report.pdf
│   Original undergraduate thesis document
│
├── Research_Presentation_Slides.pdf
│   The slides used for explaining the project that was presented at the ICTP International Satellite Symposium
│
└── README.md
## Supporting Documents

This repository also includes:

Undergraduate Final Year Project Report

Project Presentation Slides

These documents provide additional explanation of the research and its results.

## Python Libraries Used

numpy

pandas

matplotlib

seaborn

pyGAM

scikit-learn

SHAP

tensorflow

## Project Supervisor

Dr. H. A. Lawal

## Author

Babalola-Jacobs Oluwasegun David
Final Year Undergraduate Project
Department of Physics
Air Force Institute of Technology, Kaduna

## Citation

If you use this project, please cite:

Babalola-Jacobs, O. D. (2025).
Predicting the Effects of Geomagnetic Storms on the Ionosphere under Increasing Greenhouse Gas Concentrations.
Final-Year Undergraduate Project.
Department of Physics, Air Force Institute of Technology, Kaduna.

License

This project is intended for academic and research purposes.

Please cite appropriately if using any part of this work.
