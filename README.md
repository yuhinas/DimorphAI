# Deep learning reveals that harsh environments promote the evolution of sexual dimorphism in moths

In this project, we train a Variational Sparse Coding (VSC) model to quantify moth morphology and unveil the "black box" of a complex deep-learning model to explore the evolutionary mechanisms underlying patterns of sexual dimorphism across an ecological gradient.
The repository encompasses code for the preprocessing of raw files, the training of VSC models, and the data for subsequent analysis and visualization.

## ./data/thermal-experiment/
Artificial moths printed on paper for absorption experiments, including model-generated images and their silhouettes for use in control groups.
## ./code/analysis-in-R/
This folder contains scripts for other analyses in R.
- Script `01-select-elevational-related-features.R` can select the elevational-related features in sexually dimorphic or monomorphic species. 
- Script `02-the-relationship-between-sexual-dimorphism-and-elevation.R` can find the relationship between sexual dimorphism and elevation in sexually dimorphic species. The output csv files deposited in `./data/select-elevational-related-features`
- Script `03-the-relationship-between-elevation-and-temperature.R` can find the relationship between elevation and temperature with worldclim2 data.

## ./code/quantify-moth-trait/
This folder contains a series of scripts that can quantify the generated images to describe the visual appearances.
- Script `01-quantify-photo.py` calculates the average brightness, contrast and relative size of the dark patches of forewings of generated images. 
- Script `02-visualization-for-ploting.R` can visualize the results with CSV files including `photo_quantify_sd.csv` and `photo_quantify_sm.csv`. 

## ./code/thermal-experiment/
This folder contains three scripts and four CSV files for processing thermal camera images:
- Script `01-seq.R` can covert SEQ files for thermal camera images into npy files for python
- Script `02-moth_thermal_masking.ipynb`
- Script `03-plot.R` can plot with CSV file, include `thermal_plot_me_with_metadata_cold_FW.csv`, `thermal_plot_me_with_metadata_cold_HW.csv`, `thermal_plot_me_with_metadata_cold_LW.csv` and `thermal_plot_me_with_metadata_cold_RW.csv` for visualization. 
## ./main_vsc.py
This script can train the VSC model. The metadata of training images is deposited in `./model/sp_all.csv`. The example of training images are deposited in `./model/dataset256_demo/`. The trained model is deposited in `./model/model_local_epoch_10000_iter_0.pth`
## ./prepare_data.py
This script can calculate the distance between sexes, the median elevation and the elevational range size of each species. It also merges the data of 512-D extracted features to do subsequent analysis. The series of data are deposited in `./data/prepare-data/`. 
## ./any_code_trend.py
This script can generate images with the VSC model with elevation in both sexes of sexually dimorphic or monomorphic species. The images are deposited in `./model/generated-image-along-elevation/`.
## ./decoding_vsc.py
This script can generate the images from 512-D extracted features. The example images are deposited in `./model/decode_demo/`.
## ./encoding_vsc_repeatN.py
This script can extract 512-D features from images. The results are deposited in `./model/encode/`.
## ./grid_explore_vsc_dimensions.py
This script can visualize each feature dimension of 512-D features. You need to run `./dim_hist_sampling.py` first to get the changes in values of each feature dimension. The results are deposited in `./model/feature_viz/`


