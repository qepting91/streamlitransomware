import streamlit as st
import pandas as pd
import base64
import plotly.graph_objects as go
from data_process import process_data

def display_options(data):
    data = process_data(data)
    pd.set_option('display.max_colwidth', None)

    st.sidebar.markdown('<p class="font">Ransomware Data Database</p>', unsafe_allow_html=True)
    st.sidebar.subheader("About the App")
    st.sidebar.text("""
        Exploration of the Ransomware Attacks by Group, per Target and Date 
    """)

    st.sidebar.subheader('Statistics')
    if st.sidebar.checkbox('Full Data Set', key='full_data_set'):
        st.subheader('Filter on Entry Number at the Left of the Table for Most Recent Attack')
        all_groups = data['group'].unique().tolist()
        selected_group = st.selectbox('Select a Group', ['All Groups'] + all_groups)

        if selected_group != 'All Groups':
            data = data[data['group'] == selected_group]

        st.write(data[['group', 'title', 'date']].sort_values(by='date', ascending=False))

    if st.sidebar.checkbox('Show attacks over time', help='Toggle to view the number of attacks over time'):
        st.subheader('Attacks Over Time')

        all_groups = data['group'].unique().tolist()
        selected_groups = st.multiselect('Select Groups', all_groups, default=[])
        filtered_data = data[data['group'].isin(selected_groups)].copy()

        if not selected_groups:
            st.write("Select at least one group to display the graph")
        else:
            # Convert 'date' column back to datetime type for resampling
            filtered_data['date'] = pd.to_datetime(filtered_data['date'])

            # Set 'date' as index and resample the data monthly
            filtered_data = filtered_data.set_index('date').groupby('group').resample('M').size().reset_index(name='Number of Attacks')

            # Initialize an empty figure
            fig = go.Figure()

            # Define colors for the groups
            colors = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3', '#FF6692', '#B6E880', '#FF97FF', '#FECB52']

            # Loop over the groups to add a line for each group
            for i, group in enumerate(selected_groups):
                group_data = filtered_data[filtered_data['group'] == group]
                fig.add_trace(go.Scatter(
                    x=group_data['date'].dt.strftime('%b %d, %Y'),  # Format date when plotting
                    y=group_data['Number of Attacks'], 
                    mode='lines+markers+text', 
                    name=group, 
                    text=group_data['date'].dt.day,  # Day of the month
                    textposition='top center',
                    line=dict(color=colors[i % len(colors)]),  # set the color of the line
                    marker=dict(
                        symbol='star',
                        color='black',  # set the color of the marker
                        size=10  # adjust the size of the marker
                    )
                ))
            
            fig.update_layout(
                title='Attacks Over Time by Group',
                title_x=0.5, 
                xaxis_title='Date', 
                yaxis_title='Number of Attacks',
                hovermode='x unified',
                plot_bgcolor='#f8fafc',
                paper_bgcolor='#f8fafc',
                font=dict(color='#222222')
            )

            # Display the figure
            st.plotly_chart(fig, use_container_width=True)
            if st.checkbox('Show description for "Attacks Over Time"'):
                st.markdown("""
                    The chart above depicts the number of ransomware attacks over time for the selected groups. 
                    The x-axis represents time (in months and years), while the y-axis represents the count of attacks. Each line corresponds to a different group.
                    The markers show the number of attacks for each day of the month. The plot allows us to analyze the frequency and trend of attacks over time for each group.
                """)

    if st.sidebar.checkbox('Download CSV file'):
        csv = data.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        linko= f'<a href="data:file/csv;base64,{b64}" download="myfilename.csv">Download CSV File</a>'
        st.markdown(linko, unsafe_allow_html=True)
