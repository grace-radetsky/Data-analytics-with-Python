#!/usr/bin/env python
# coding: utf-8

# > **Tip**: Welcome to the Investigate a Dataset project! You will find tips in quoted sections like this to help organize your approach to your investigation. Before submitting your project, it will be a good idea to go back through your report and remove these sections to make the presentation of your work as tidy as possible. First things first, you might want to double-click this Markdown cell and change the title so that it reflects your dataset and investigation.
# 
# # Project: Investigate FBI Gun Dataset 
# 
# ## Table of Contents
# <ul>
# <li><a href="#intro">Introduction</a></li>
# <li><a href="#wrangling">Data Wrangling</a></li>
# <li><a href="#eda">Exploratory Data Analysis</a></li>
# <li><a href="#conclusions">Conclusions</a></li>
# </ul>

# <a id='intro'></a>
# ## Introduction
# 
# > **Tip**: In this section of the report, provide a brief introduction to the dataset you've selected for analysis. At the end of this section, describe the questions that you plan on exploring over the course of the report. Try to build your report around the analysis of at least one dependent variable and three independent variables.
# >
# > If you haven't yet selected and downloaded your data, make sure you do that first before coming back here. If you're not sure what questions to ask right now, then make sure you familiarize yourself with the variables and the dataset context for ideas of what to explore.
# 

# #### Import Libraries for Data Analysis

# In[1]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
get_ipython().run_line_magic('matplotlib', 'inline')


# <a id='wrangling'></a>
# ## Data Wrangling
# 
# ### General Properties

# In[2]:


# Load the first data set in excel format

gun_data = pd.read_excel('C:\\Users\\Minh Hang\\Downloads\\gun-data.xlsx')

#view the first 10 rows of the data set
gun_data.head()


# In[3]:


#Inquire general information of the number of columns, rows, missing data of the data set

gun_data.info()


# In[3]:


#since the data set has a lot of Null values, the datatype conversion attempt may not be successful
# I will pushed back this step till Null values have been treated


# In[4]:


# percentage of Null account over non null account:

#count of null

null_counts = gun_data.isnull().sum().sort_values(ascending=False)

#Percentage of null values in the data set; gun_data.count() the number of total observation
percent_null = null_counts*100/len(gun_data)

#table 

missing_gun_data = pd.concat([null_counts, percent_null], axis = 1, keys = ['Total Missing', 'Percent Missing'])

print(missing_gun_data)


# From the above the table with missing data above, some variables have too many missing variables to the extent that it is impossible to make an analysis based on them (e.g. rentails_long_gun at 93.39% missing variables). I will set up a threshold to drop variables that have more than 60% missing variables)

# In[5]:


#drop variables that have more than 60% of missing variables
thresh = len(gun_data)*.6

gun_data.dropna(thresh = thresh, axis = 1, inplace = True)

gun_data.head()


# After dropping those variables, there are 12 columns left. All variables for rentals, private, returns been dropped. Accept that the analysis will be limited

# Get a basic summary of the new data frame

# In[6]:


gun_data.info()


# It can be seen that there are still some Null values among most of variables. either drop rows that contain Null values or impute missing values with either means or median

# In[7]:


gun_data.describe()


# Since the the 50 percentile values for all variables above are smaller than mean values, it is inferred that the distributions of all variables above are right-skewed. In such case, imputing with median would be more ideal than imputing with mean. I will go ahead and impute missing data with median

# In[8]:


#Impute missing data with median

gun_data.fillna(gun_data.median(), inplace = True)


# In[9]:


#view the data set info

gun_data.info()


# In[10]:


#convert all variables except for 'month' and 'state' into 'int64' because ...............

gun_data.iloc[:, 2:11] = gun_data.iloc[:, 2:11].apply(lambda x: x.astype(int))


# To merge with the census_data set which contains data for the year 2016, I will keep only the 2016 (explaination of why I choose year 2016 is later <link>

# In[11]:


#reformat data in 'month' column from object types to datetime type

gun_data['month'] = pd.to_datetime(gun_data['month'])

gun_data.dtypes

#Now that the data type of month is datetime64


# In[12]:


#filter out years before 2010
gun_data = gun_data[gun_data.month.dt.year == 2016]


# ## Load the second data set

# In[106]:


#load the second data set
census_data = pd.read_csv('C:\\Users\\Minh Hang\\Downloads\\u.s.-census-data.csv')

print('number of rows and columns are:', census_data.shape)

census_data.tail(30)


# Clean up data set, drop unnecessary columns, treat Null

# In[107]:


#Drop 'Fact Note' column since most data is neither NaN or incomprehensible

census_data.drop(census_data.columns[1], axis = 1, inplace=True)

#Drop rows containing NaN values since NaN in index from 64 to 84 across all variables (Note that row 64 doesn't contain Null values however since FIPS Code is 'string' information that is unique to each state and not so useful in our analysis)
census_data.drop(census_data.index[65:85], axis=0, inplace=True)

#view the bottom 30 records of the data frame
census_data.tail()


# #### 'Extract the year or time information and store in a new column called 'Year'

# In[108]:


#Add a new column and assign it to "None" value. We will add later. 1 is the location to insert the column

census_data.insert(1, 'Year', None)


# #### Extracting the 'Year'

# In[109]:


census_data['Year'] = census_data['Fact'].str.extract(r"(\d{4})")
                                            


# In[110]:


census_data.head()


# #### View all elements in the column 'Fact'

# In[111]:


census_data.Fact.tolist()


# #### Reasoning about why choose 2016 and NOT??? 2011 - 2015
# 
# >Asking question here: What factors I think are relevant to total sales of guns/ permits:
# 
# variables have so many different years, and don't follow a particular formats, since 2016 has various variables such as population size, age, and ethnicities => pick 2016 for those variables
# 
# the period from 2011 to 2015 have a few interesting variables such to inform about occupations, educations, incomes (household or income per capita)
# 
# the other time periods have variables that I don't think are relevant such as firm types (men-owned, women-owned, etc), healthcare receipts, accommodation food and sales. So I won't pursue this year.

# #### filter only year 2016

# In[112]:


census_2016 = census_data[census_data.Year == '2016']

fips_info = census_data[census_data.Fact == 'FIPS Code']

census_2016_fips = pd.concat([census_2016, fips_info])


# #### Transpose the DataFrame
# 
# > Transpose to merge with the gun_data using State as the shared index

# In[113]:


census_2016_fips = census_2016_fips.set_index('Fact').T


# Drop row '2016' since all variables now are based in 2016

# In[114]:


census_2016_fips = census_2016_fips.drop(index = 'Year')


# In[115]:


census_2016_fips.head(3)


# #### Cleaning unwanted characters such as . , %

# In[116]:


def clean_bad_char(incoming_string):
    cleaned_string = incoming_string.replace('%', '').replace(',', '').replace('$','').replace('\"', '')
    return(cleaned_string)


# In[117]:


#apply to the dataframe

census_2016_fips = census_2016_fips.applymap(clean_bad_char)


# In[118]:


census_2016_fips.columns.to_list()


# In[119]:


census_2016_fips.tail()


# In[120]:


#Change the 'Popultion estimates', 'Housing Units', and 'Building permits' columns into integer

cols_to_int = ['Population estimates, July 1, 2016,  (V2016)', 'Housing units,  July 1, 2016,  (V2016)', 'Building permits, 2016', 'FIPS Code']

census_2016_fips[cols_to_int] = census_2016_fips[cols_to_int].astype(int)

census_2016_fips.dtypes


# In[121]:


#Change the remaining column into float

cols_to_float = ['Persons under 5 years, percent, July 1, 2016,  (V2016)',
 'Persons under 18 years, percent, July 1, 2016,  (V2016)',
 'Persons 65 years and over, percent,  July 1, 2016,  (V2016)',
 'Female persons, percent,  July 1, 2016,  (V2016)',
 'White alone, percent, July 1, 2016,  (V2016)',
 'Black or African American alone, percent, July 1, 2016,  (V2016)',
 'American Indian and Alaska Native alone, percent, July 1, 2016,  (V2016)',
 'Asian alone, percent, July 1, 2016,  (V2016)',
 'Native Hawaiian and Other Pacific Islander alone, percent, July 1, 2016,  (V2016)',
 'Two or More Races, percent, July 1, 2016,  (V2016)',
 'Hispanic or Latino, percent, July 1, 2016,  (V2016)',
 'White alone, not Hispanic or Latino, percent, July 1, 2016,  (V2016)']


census_2016[cols_to_float] = census_2016[cols_to_float].astype(float)

#since there is a character 'Z' in the dataframe

census_2016.dtypes

get_ipython().run_line_magic('xmode', 'plain')


# In[122]:



#since there is a character 'Z' in the dataframe, the following code will force invalid values such as Z to NaN

census_2016_fips[cols_to_float] = census_2016_fips[cols_to_float].apply(pd.to_numeric, errors='coerce')


# In[123]:


census_2016_fips.info()


# In[124]:


#Notice that there are 4 NaN values in the 'Native Hawaiian and Other Pacific Islander' variable.

census_2016_fips['Native Hawaiian and Other Pacific Islander alone, percent, July 1, 2016,  (V2016)'].fillna(census_2016_fips['Native Hawaiian and Other Pacific Islander alone, percent, July 1, 2016,  (V2016)'].median(), inplace = True)


# ### Merging two dataset

# In[125]:


#Since the census_2016 has only July's data, to merge, set 'state'

gun_july = gun_data[gun_data.month == '2016-07-01']

gun_july.set_index('state', inplace = True)


# In[126]:


merged_july = pd.merge(gun_july, census_2016_fips, left_index = True, right_index = True, how = 'outer')

merged_july.info()


# In[127]:


merged_july.head()


# There are some NaN values probably because the gun_july data set has some states that the census_2016 doesn't have. Let's find out what are the states

# In[128]:


#return a list of rows that have at least 1 missing value:

merged_july[merged_july.isna().any(axis=1)]


# In[129]:


#those are not states in the US. I would like to drop them. 

merged_july = merged_july.dropna(axis = 0)


# In[130]:


#impute missing values:

merged_july.head()


# #Notice the missing values due to gun_data have each state has data for 12 months while the census_2016 only have data recorded as of\
# #July 1, 2016. Keep this to analyze the correlation between the gun data with demographic while keeping the 12-month data for each state to analyze the time series
# 

# <a id='eda'></a>
# ## Exploratory Data Analysis
# 
# > **Tip**: Now that you've trimmed and cleaned your data, you're ready to move on to exploration. Compute statistics and create visualizations with the goal of addressing the research questions that you posed in the Introduction section. It is recommended that you be systematic with your approach. Look at one variable at a time, and then follow it up by looking at relationships between variables.
# 
# 
# We have 2 data sets to work with:
# 
# **gun_data**\
# **merged_july**
# 
# ### Research Question 1 - What states have the highest data?
# 
# - State have highest overall gun purchase?
# - Highest growth and lowest growth from Jan to Dec in 2016
# - Overall trend of gun purchase by month?

# In[353]:


#State have the highest overall gun


# In[ ]:


# Use this, and more code cells, to explore your data. Don't forget to add
#   Markdown cells to document your observations and findings.


# ### Research Question 2  (Replace this header name!)
# - Which variables corelate with high gun purchase per capital per state?
# 

# In[ ]:





# In[342]:


# Continue to explore the data to address your additional research
#   questions. Add more headers as needed if you have more questions to
#   investigate.

#which variable corelate with high gun per capital per state?


# <a id='conclusions'></a>
# ## Conclusions
# 
# > **Tip**: Finally, summarize your findings and the results that have been performed. Make sure that you are clear with regards to the limitations of your exploration. If you haven't done any statistical tests, do not imply any statistical conclusions. And make sure you avoid implying causation from correlation!
# 
# > **Tip**: Once you are satisfied with your work, you should save a copy of the report in HTML or PDF form via the **File** > **Download as** submenu. Before exporting your report, check over it to make sure that the flow of the report is complete. You should probably remove all of the "Tip" quotes like this one so that the presentation is as tidy as possible. Congratulations!

# In[ ]:




