import pandas as pd
import plotly.express as px
import streamlit as st

# 1. Page Configuration
st.set_page_config(page_title='Zambia GDP Dashboard', page_icon='📈', layout='wide')

# 2. Load Data
@st.cache_data
def load_data():
    return pd.read_csv('data/clean.csv')

df = load_data()
df.columns = df.columns.str.strip()

# 3. Sidebar Filters
with st.sidebar:
    st.header('Filter Data')
    
    # Indicator selector
    indicators = sorted(df['indicator'].unique())
    default_idx = 0
    for i, ind in enumerate(indicators):
        if 'growth' in ind.lower():
            default_idx = i
            break
    selected_indicator = st.selectbox('Select Indicator:', indicators, index=default_idx)
    
    df_ind = df[df['indicator'] == selected_indicator]
    
    # Country multiselect
    all_countries = sorted(df_ind['country'].unique())
    default_countries = [c for c in all_countries if c == 'Zambia']
    if not default_countries:
        default_countries = all_countries[:1]
    for c in all_countries:
        if c not in default_countries and len(default_countries) < 5:
            default_countries.append(c)
            
    countries = st.multiselect('Select Countries:', all_countries, default=default_countries)
    
    # Year slider
    year_min, year_max = int(df_ind['year'].min()), int(df_ind['year'].max())
    years = st.slider('Select Years:', year_min, year_max, (year_min, year_max))
    
    # (Removed the "Built with..." text here)

# 4. Filtering Logic
mask = df_ind['country'].isin(countries) & df_ind['year'].between(years[0], years[1])
view = df_ind[mask].sort_values('year')

if view.empty:
    st.warning('No data for this selection. Please adjust your filters.')
    st.stop()

# 5. Header
st.title(f'📈 {selected_indicator}: Zambia & Regional Peers')
st.markdown(f"### How does Zambia compare to its neighbors ({years[0]}–{years[1]})?")
st.caption('Source: World Bank Open Data. Data downloaded: October 2026.')

# Formatting function
def format_val(val):
    if 'growth' in selected_indicator.lower():
        return f"{val:.1f}%"
    elif 'per capita' in selected_indicator.lower():
        return f"${val:,.0f}"
    else:
        if val > 1_000_000_000:
            return f"${val/1_000_000_000:.1f}B"
        return f"${val:,.0f}"

# Create Tabs
tab1, tab2, tab3 = st.tabs(['📊 Overview', '⚖️ Compare', '📋 Data & Method'])

with tab1:
    st.subheader(f'Latest value in {years[1]}')
    latest = view.groupby('country').tail(1)
    
    cols = st.columns(len(latest))
    for col, (_, row) in zip(cols, latest.iterrows()):
        country_data = view[view['country'] == row['country']]
        prev_value = country_data.iloc[-2]['value'] if len(country_data) > 1 else None
        
        delta_val = row['value'] - prev_value if prev_value is not None else None
        delta_str = format_val(delta_val) if delta_val is not None else None
        
        col.metric(label=row['country'], value=format_val(row['value']), delta=delta_str)

    st.subheader('Trend over time')
    fig1 = px.line(view, x='year', y='value', color='country', markers=True)
    
    # Highlight Zambia
    fig1.update_traces(line=dict(width=2)) 
    fig1.update_traces(line=dict(width=5), selector=dict(name='Zambia')) 
    
    # COVID Shading
    if years[0] <= 2020 <= years[1]:
        fig1.add_vrect(x0=2019.5, x1=2020.5, fillcolor='grey', opacity=0.2,
                       line_width=0, annotation_text='COVID-19', annotation_position='top left')
                       
    fig1.update_layout(yaxis_title=selected_indicator, xaxis_title="Year", hovermode="x unified")
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader('💡 What the data shows (for current selection)')
    best = view.loc[view['value'].idxmax()]
    worst = view.loc[view['value'].idxmin()]
    avg = view.groupby('country')['value'].mean().sort_values(ascending=False)
    
    st.markdown(f"- **Highest single-year value:** {best['country']} in {int(best['year'])} ({format_val(best['value'])})")
    st.markdown(f"- **Lowest single-year value:** {worst['country']} in {int(worst['year'])} ({format_val(worst['value'])})")
    if 'growth' in selected_indicator.lower():
        st.markdown(f"- **Highest average growth:** {avg.index[0]} ({format_val(avg.iloc[0])} per year on average)")
    else:
        st.markdown(f"- **Highest average value:** {avg.index[0]} ({format_val(avg.iloc[0])})")


with tab2:
    st.subheader('Zambia vs. Peer Average')
    pivot = view.pivot(index='year', columns='country', values='value')
    
    if 'Zambia' in pivot.columns and pivot.shape[1] > 1:
        gap = pivot['Zambia'] - pivot.drop(columns='Zambia').mean(axis=1)
        figz = px.bar(gap.reset_index(name='gap'), x='year', y='gap')
        figz.update_traces(marker_color=['#2ca02c' if val > 0 else '#d62728' for val in gap])
        figz.update_layout(yaxis_title='Zambia minus peer average', xaxis_title="Year")
        st.plotly_chart(figz, use_container_width=True)
        st.caption("Green bars mean Zambia is outperforming the average of the other selected countries. Red means underperforming.")
    else:
        st.info("Select Zambia and at least one other country to see this comparison.")

    st.markdown('---')
    
    st.subheader('Average by Decade')
    period = view.copy()
    period['decade'] = (period['year'] // 10 * 10).astype(str) + 's'
    by_decade = period.groupby(['decade', 'country'])['value'].mean().reset_index()
    figd = px.bar(by_decade, x='decade', y='value', color='country', barmode='group')
    st.plotly_chart(figd, use_container_width=True)
    st.caption('Note: The 2020s only include data up to 2025.')


with tab3:
    st.subheader('Methodology & Notes')
    st.markdown("""
    - **Data Source:** World Bank Open Data.
    - **Download Date:** October 2026.
    - **Data cleaning:** The raw World Bank data is in a "wide" format (one column per year). I used Python and Pandas to reshape it into a "long" format, clean the year strings (e.g., turning '2000 [YR2000]' into '2000'), and drop missing values.
    - **Indicators:**
        - *GDP growth (annual %):* The percentage change in GDP from the previous year.
        - *GDP per capita (current US$):* Total GDP divided by the population, in current US dollars (not adjusted for inflation).
        - *GDP (current US$):* The total gross domestic product in current US dollars.
    """)
    
    st.subheader('View and Download Data')
    with st.expander('🔍 Expand to see the underlying data'):
        st.dataframe(view, use_container_width=True)
        st.download_button(
            label='📥 Download as CSV',
            data=view.to_csv(index=False),
            file_name='economic_data.csv',
            mime='text/csv'
        )