# Zambia vs. Regional Peers: Economic Dashboard

**Live Link:** [LINK HERE]

## What is this?
A Streamlit dashboard exploring how Zambia's economy has performed since 2000 compared to a few regional peers: Kenya, Rwanda, Tanzania, and Zimbabwe. 

I didn't just want to compare Zambia to its direct neighbors. I picked a mix of countries in Sub-Saharan Africa that face similar structural challenges (reliance on a few key exports, similar income levels) to see how their growth paths have diverged.

## The Data
Downloaded from the World Bank Open Data portal in October 2026. 
I used three main indicators:
* GDP growth (annual %)
* GDP per capita (current US$)
* Total GDP (current US$)

## How I built it
* **Cleaning:** World Bank data comes in a messy "wide" format (a column for every single year). I used Pandas to filter the data into a clean "long" format. .
* **The App:** Built with Streamlit and Plotly. 
* **Features:** 
  * Sidebar filters to switch between countries, years, and indicators.
  * A "Compare" tab that calculates exactly how much Zambia is over or underperforming the average of the other countries.
  * The text findings at the bottom update automatically based on what is selected.

## 3 Things I found
1. Rwanda is a growth machine. They consistently post the highest growth rates in this group, often over 8%.
2. All five economies crashed in 2020. The COVID-19 dip is clearly visible across all five countries. 
3. Zimbabwe is highly volatile. The -17.6% crash in 2008 is by far the deepest contraction in the dataset.

## Run it locally
If you want to run it on your machine:
```bash
pip install -r requirements.txt
streamlit run app.py
