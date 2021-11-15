# ADVAnCe - Actigraphy Data Visualization and Analysis Challenge

The scripts in this repository aim to provide a clean way of visualizing and comparing client and partners sleep and activity patterns. It is part my entry for the **Actigraphy Data Visualization and Analysis Challenge** that is part of the PoLNet3 workshop.

## Data and Output

The main data used to plot actograms are the 'interval status' classification provided by the ActiWatch. The output from the main script is two PDF files, one containing actograms for clients and the other containing actograms for partners.

Data from the following data set must be extracted in the `data` folder. 

> Angelova, M., Kusmakar, S., Karmakar, C., Zhu, Z., Shelyag, S., Drummond, S., & Ellis, J. (2021). Chronic insomnia and bed partner actigraphy data [Data set]. https://doi.org/10.5061/dryad.b8gtht7bh

In the actograms we plotted only clients that had corresponding bed partners and vice-versa. We plotted 7 days of data for each individual, discarding the first day of recording. 


## Reproducing

Downloaded data must be extracted in the `data` folder.  Client and partner data must be in the paths:

- Clients: `data/Supplementary Material_Final/Data/CLIENT`
- Partners: `data/Supplementary Material_Final/Data/PARTNER`

With the data in place one can open the RStudio project `actigraphy-viz-challenge.Rproj` and run the `actograms.R` script. The script's output will be saved to the `output` folder in PDF format. 

## Contact

Visualization was done by J.T. Silvério with data from Angelova et al. (2021). Contact at jt.silverio[at]usp.br
