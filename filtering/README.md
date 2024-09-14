# Filtering signals 

Functions and classes related to filtering your data 

## types of filters 
* moving average 
* Keizer-Bessel
* etc. 

## The FilteredTrace class 
Inherits from `Trace` 
Specifically has attributes only refering to filtered data 
* `filtered_values` :: Typically z-position or fluorescence intensity. However could in principle be any signal you filtered 
* `time` :: The time array is also adjusted after filtering // course-graining 

