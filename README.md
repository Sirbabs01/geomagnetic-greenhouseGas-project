# Does increasing CO₂ change the response of the midlatitude ionosphere to space weather?

Code and data for the study of how increasing carbon dioxide (CO₂) affects the ionosphere above Roquetes, Spain (Ebro Observatory, URSI code EB040), and whether it changes the way the ionosphere responds to geomagnetic storms and to solar activity. The analysis uses daily ionosonde observations of total electron content (TEC), the F2-layer critical frequency (foF2), and the F2-layer peak height (hmF2) from 1988 to 2026.

**Authors:** Oluwasegun Babalola-Jacobs David, H. A. Lawal, [third author]

**Manuscript:** in preparation for an AGU journal. A preliminary version of this work was presented at the International Beacon Satellite Symposium 2025 (Rome, Italy). The analysis in this repository replaces the preliminary one; the changes are listed in the notebook and in the manuscript.

---

## Main findings

- Solar activity is by far the strongest driver of TEC, foF2, and hmF2, followed by the season, then CO₂. Geomagnetic activity (Dst) has a clear effect only on hmF2.
- The ionosphere is lower at higher CO₂ when solar activity, geomagnetic activity, and the season are held fixed. Per 10 ppm, TEC, foF2, and hmF2 decrease by about 0.23 TECU, 0.04 MHz, and 1.7 km once the strength of the solar cycles is taken into account (F10.7).
- Geomagnetic storms raise hmF2 by about 20 km for a −100 nT storm at every CO₂ level. Their effect on TEC and foF2 changes sign with the season (up in winter, down in summer).
- The data do **not** show a confirmed change with CO₂ in the response of the ionosphere to geomagnetic storms or to solar activity. One model suggests a weaker storm response of TEC and foF2 at higher CO₂, but it is not confirmed by the other models, by the size of the storm change measured from the observations, or once the strength of the solar cycles is included.

---

## Repository contents

| File | What it is |
|---|---|
| `build_dataset.py` | Downloads the raw data from NOAA, NASA OMNIWeb, and GIRO DIDBase, cleans it, and merges it into one daily table |
| `data/merged_daily_filled.csv` | The daily dataset used in the paper (output of `build_dataset.py`, 1974 to 2026) |
| `ionosphere_co2_analysis.ipynb` | The full analysis: every figure and table in the paper |
| `requirements.txt` | Python packages needed |

---

## Data sources

| Variable | Source |
|---|---|
| CO₂ (daily mean, ppm) | NOAA Global Monitoring Laboratory, Mauna Loa Observatory (Maunakea from December 2022 to July 2023) |
| Dst (nT) and F10.7 (sfu) | NASA OMNIWeb, OMNI2 hourly data (Dst from the World Data Center for Geomagnetism, Kyoto) |
| foF2, hmF2, TEC | GIRO Digital Ionogram Database (DIDBase), Roquetes / Ebro Observatory, EB040 |

The ionosonde data are used under the GIRO rules of the road. Users of these data should cite Reinisch & Galkin (2011), acknowledge the Ebro Observatory as the data provider, and follow the GIRO data use policy.

### Columns of `data/merged_daily_filled.csv`

| Column | Meaning |
|---|---|
| `date` | Day (UTC) |
| `co2_ppm` | Daily mean CO₂ at Mauna Loa (ppm); gaps of up to 14 days filled by straight-line interpolation |
| `co2_filled` | True where `co2_ppm` was filled and not measured |
| `dst_mean`, `dst_min` | Daily mean and daily minimum of hourly Dst (nT) |
| `dst_hours` | Number of hourly Dst values in the day |
| `f107` | Daily F10.7 solar radio flux (sfu) |
| `foF2`, `hmF2`, `TEC` | Daily means of the hourly ionosonde values (MHz, km, TECU) |
| `foF2_hours`, `hmF2_hours`, `TEC_hours` | Number of hours that went into each daily mean |
| `solar_cycle`, `solar_cycle_phase` | Solar cycle number and the position within the cycle (0 at the start, 1 at the end) |
| `year`, `doy` | Year and day of year |

Ionosonde soundings with an automatic-scaling confidence score below 70 were removed; manually scaled and unscored soundings were kept. A day was kept only if it had at least 18 hourly values.

---

## How to run

### 1. Rebuild the dataset (optional)

The dataset used in the paper is already in `data/`. To download and build it again:

```bash
pip install pandas numpy requests
python build_dataset.py
```

This creates the folder `ionosphere_data/` with the raw downloads, `merged_daily.csv`, and a `summary.txt` of what was downloaded. The download takes a while because the GIRO server is queried year by year with a pause between requests. If the connection drops, run the script again; files already downloaded are reused.

### 2. Run the analysis

**On your own computer**

```bash
pip install -r requirements.txt
jupyter notebook ionosphere_co2_analysis.ipynb
```

Then run all cells from the top.

**On Google Colab**

1. Open `ionosphere_co2_analysis.ipynb` in Colab.
2. Upload `data/merged_daily_filled.csv` (folder icon on the left).
3. Choose **Runtime → Run all**.

The notebook finds the data file whether it is next to the notebook, in `data/`, or in `ionosphere_data/` (from `build_dataset.py`). A full run takes about one hour, mostly for the bootstrap refits and SHAP. Every figure is saved as PNG and PDF in `figures/`, and every table as CSV in `tables/`. All settings (which Dst to use, the storm levels, the number of bootstrap refits, whether to run the CNN) are in the **Settings** cell near the top. Random seeds are fixed, so the results are repeatable; the CNN may differ slightly between machines.

---

## What the notebook does

The notebook follows the order of the original analysis:

1. **Exploratory analysis**: time series, scatter plots with Pearson, Spearman, and Kendall correlations, and violin plots, each at three levels (whole record, per solar cycle, per year), with Augmented Dickey–Fuller stationarity tests.
2. **Generalized additive models (pyGAM)** for TEC, foF2, and hmF2, with solar cycle phase, daily minimum Dst, CO₂, and the day of year as predictors. The smoothness is chosen by year-blocked cross-validation, and the models are scored on years they were not trained on.
3. **Variable assessment and SHAP** for every model: the contribution of each driver, SHAP summary and dependence plots, and mutual information.
4. **Delayed response and storm days only**: previous day's Dst, and models fitted to storm days.
5. **Interaction between CO₂ and geomagnetic storms**: a tensor-product interaction model, the interaction surface, and Case 1 (CO₂ as the modifier) and Case 2 (Dst as the modifier) curves at percentile levels, with the width of each curve.
6. **The modulation as a number**: a linear-in-CO₂ interaction model gives the change in the storm response per 10 ppm, with 95% intervals from a year-block bootstrap; repeated on 16 combinations of solar cycle phase and season.
7. **Size of the storm change from the observations**, regardless of whether a storm raises or lowers the ionosphere, and the share of storms that raise or lower it, in four CO₂ groups.
8. **Response to solar activity**: the same tests for solar cycle phase and F10.7, from the models and from the observations.
9. **Convolutional neural network** as an independent model, with SHAP.
10. **Check models**: with F10.7, for 2004 to 2026 only, without the season term, and with the daily mean Dst.
11. **Future projection** to 450, 475, and 500 ppm at fixed solar conditions (scenarios, not forecasts).
12. **Summary** of all the numbers used in the paper.

### Main changes from the preliminary analysis (2025)

- The dataset was rebuilt in Python and extended to 2026, with a quality filter on the ionosonde data and short CO₂ gaps filled.
- Solar cycle 25 no longer ends in January 2023, so the years from 2023 onward are included.
- A day-of-year (season) term was added to every model.
- The smoothness of the models is chosen, and the models are tested, by holding out whole years instead of by GCV and a random split.
- The modulation by CO₂ is given as a number with an uncertainty, and is also measured directly from the observations.
- The tests were extended to solar activity, and check models with F10.7 were added.

---

## Requirements

Python 3.10 or later and the packages in `requirements.txt` (tested with pyGAM 0.12.0, SHAP 0.54.1, TensorFlow 2.21.0, scikit-learn 1.9.1, pandas 3.0.5, NumPy 2.5.3, SciPy 1.16.3, Matplotlib 3.11.2, statsmodels 0.15.0).

---

## References for the data

- Reinisch, B. W., & Galkin, I. A. (2011). Global Ionospheric Radio Observatory (GIRO). *Earth, Planets and Space*, 63(4), 377–381. https://doi.org/10.5047/eps.2011.03.001
- NOAA Global Monitoring Laboratory. Mauna Loa CO₂ daily mean data. https://gml.noaa.gov/ccgg/trends/
- NASA Space Physics Data Facility. OMNIWeb, OMNI2 hourly data. https://omniweb.gsfc.nasa.gov/

## How to cite

If you use this code or dataset, please cite the paper once it is published. Until then, cite this repository.

## Licence

[Choose a licence before making the repository public, for example MIT for the code.]
