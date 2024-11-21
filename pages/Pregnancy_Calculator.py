import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta
import pandas as pd
        
st.set_page_config(
   page_title="Pregnancy Calculator",
   page_icon="🤰",
   layout="wide",
   initial_sidebar_state="expanded",
)
def make_donut(input_response, input_text, input_color):
  chart_color = ['#27AE60', '#781F16']
  source = pd.DataFrame({
      "Topic": ['', input_text],
      "% value": [100-input_response, input_response]
  })
  source_bg = pd.DataFrame({
      "Topic": ['', input_text],
      "% value": [100, 0]
  })
    
  plot = alt.Chart(source).mark_arc(innerRadius=45, cornerRadius=25).encode(
      theta="% value",
      color= alt.Color("Topic:N",
                      scale=alt.Scale(
                          #domain=['A', 'B'],
                          domain=[input_text, ''],
                          # range=['#29b5e8', '#155F7A']),  # 31333F
                          range=chart_color),
                      legend=None),
  ).properties(width=130, height=160)
    
  text = plot.mark_text(align='center', color="#29b5e8", font="Lato", fontSize=20, fontWeight=700, fontStyle="italic").encode(text=alt.value(f'{input_response} %'))
  plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=45, cornerRadius=20).encode(
      theta="% value",
      color= alt.Color("Topic:N",
                      scale=alt.Scale(
                          # domain=['A', 'B'],
                          domain=[input_text, ''],
                          range=chart_color),  # 31333F
                      legend=None),
  ).properties(width=130, height=160)
  return plot_bg + plot + text
@st.cache_data
def load_csv_data():
    df = pd.read_csv(".//additional//detailed_pregnancy_weeks_with_symptoms.csv")
    df = df.astype(str)
    return df
pregnancy_weeks = lambda: load_csv_data()
def get_week_details(df, week_number):
    if week_number < 1 or week_number > 40:
        return "Invalid Week Number. Please provide a Week Number between 1 and 40."
    week_details = df[df["Week Number"] == str(week_number)]
    return week_details.to_dict(orient="records")[0]
def calculate_due_date_by_last_menstrual_period(date_of_last_menstrual_period, pregnancy_duration):
    due_date = date_of_last_menstrual_period + timedelta(days=pregnancy_duration)
    return due_date
def calculate_ivf_last_menstrual_period(date_of_ivf_transfer, pregnancy_duration, embryo_stage):
    if embryo_stage == "Day 3":
        extra_days = 3 + 14
    elif embryo_stage == "Day 5":
        extra_days = 5 + 14
    pregnancy_duration = pregnancy_duration - extra_days
    last_menstral_date = date_of_ivf_transfer - timedelta(days=extra_days)
    due_date = date_of_ivf_transfer + timedelta(days=pregnancy_duration)
    return due_date, last_menstral_date
def calculate_days_preganant(last_menstrual_period_date):
    # Get the current date
    current_date = datetime.now().date()
    # Calculate the difference in days
    difference_in_days = (current_date - last_menstrual_period_date).days 
    return difference_in_days
def calculate_weeks_pregnant(last_menstrual_period_date):  
    # Get the current date
    current_date = datetime.now().date()
    # Calculate the difference in days
    difference_in_days = (current_date - last_menstrual_period_date).days 
    # Convert days to weeks
    difference_in_weeks = difference_in_days / 7
    return round(difference_in_weeks,2)
def calculate_days_left(due_date):
    # Get the current date
    current_date = datetime.now().date()
    # Calculate the difference in days
    difference_in_days = (due_date - current_date).days 
    return difference_in_days
def calculate_weeks_left(due_date):
    # Get the current date
    current_date = datetime.now().date()
    # Calculate the difference in days
    difference_in_days = (due_date - current_date).days 
    # Convert days to weeks
    difference_in_weeks = difference_in_days / 7
    return round(difference_in_weeks,2)
def calculate_last_menstrual_period_by_due_date(due_date, pregnancy_duration):
    last_menstrual_period_date = due_date - timedelta(days=pregnancy_duration)
    return last_menstrual_period_date
def calculate_percentage_of_pregnancy_completed(last_menstrual_period_date, pregnancy_duration):
    days_preganant = calculate_days_preganant(last_menstrual_period_date)
    percentage_of_pregnancy = (days_preganant / pregnancy_duration) * 100
    return round(percentage_of_pregnancy,2)
def create_pregnancy_timeline(last_menstral_date, due_date, pregnancy_duration=280):
    weeks = []
    due_date = datetime.strptime(due_date, "%Y-%m-%d")
    last_menstral_date_str = datetime.strptime(last_menstral_date, "%Y-%m-%d")
    week_number = 0
    while last_menstral_date_str <= due_date:
        weeks.append({
            "Week Number": week_number,
            "Start Date": last_menstral_date_str.strftime("%Y-%m-%d"),
            "End Date": (last_menstral_date_str + timedelta(days=6)).strftime("%Y-%m-%d")
        })
        last_menstral_date_str += timedelta(days=7)
        week_number += 1
    # Create a DataFrame from the list of weeks
    df = pd.DataFrame(weeks)
    # Ensure the 'Week Number' column is of the same type in both dataframes
    df['Week Number'] = df['Week Number'].astype(int)
    pregnancy_weeks_df = pregnancy_weeks()
    pregnancy_weeks_df['Week Number'] = pregnancy_weeks_df['Week Number'].astype(int)
    # Merge with pregnancy_weeks on the "Week Number" column
    df = df.merge(pregnancy_weeks_df[['Week Number', 'Important Milestones']], on="Week Number", how="left")
    # Highlight the current week
    today = datetime.today().strftime("%Y-%m-%d")
    df["Current Week"] = df.apply(lambda row: "You are HERE!!!" if row["Start Date"] <= today <= row["End Date"] else ("✔️" if row["End Date"] < today else ""), axis=1)
    df.at[df.index[-1], "Current Week"] = "💖  👶  💖"
    return df
def highlight_row(row):
    if 'You are HERE!!!' in row.values:
        return ['background-color: green' for _ in row]
    elif '✔️' in row.values:
        return ['background-color: black' for _ in row]
    else:
        return ['' for _ in row]
def get_summary_details_dataframe(due_date, pregnancy_duration, last_menstrual_period_date):
    weeks_pregnant = str(calculate_weeks_pregnant(last_menstrual_period_date))
    data = {"Description": ["Conception Date","Due Date:", "Pregnancy Duration (Days): ", "Days Pregnant: ", "Weeks Pregnant: ", "Weeks until Due Date: ", "Days until Due Date:", "Pregnancy Completed ( % ): "],
            "Values": [last_menstrual_period_date.strftime("%Y-%m-%d"),due_date.strftime("%Y-%m-%d"), str(pregnancy_duration), str(calculate_days_preganant(last_menstrual_period_date)), weeks_pregnant, str(calculate_weeks_left(due_date)),str(calculate_days_left(due_date)),str(calculate_percentage_of_pregnancy_completed(last_menstrual_period_date, pregnancy_duration))]}
    df = pd.DataFrame(data)
    return df, weeks_pregnant
def summary_details_component(due_date, pregnancy_duration, last_menstrual_period_date):
    df, weeks_pregnant = get_summary_details_dataframe(due_date, pregnancy_duration, last_menstrual_period_date)
    data_container = st.container()
    with data_container:
        table, plot = st.columns(2)
        with table:
            st.table(df)
        with plot:
            st.altair_chart(make_donut(calculate_percentage_of_pregnancy_completed(last_menstrual_period_date, pregnancy_duration), 'Pregnancy Precentage Completed', 'red'), use_container_width=True)
def get_current_week_details(weeks_pregnant):
    weeks_pregnant_int = round(float(weeks_pregnant))
    if weeks_pregnant_int == 0:
        weeks_pregnant_int = 1
    return get_week_details(pregnancy_weeks(), weeks_pregnant_int)
def app():
    st.title("Pregnancy Calculator")
    st.markdown("*I created this page to help you calculate the due date of your baby. It's a simple tool that you can use to calculate the due date based on the Last Menstrual Period, Conception Date, IVF Transfer Date, or Due Date.*") 
    st.markdown("*The aquiracy of the due date calculation is based on the average pregnancy duration of 280 days. The pregnancy duration can vary from 266 to 294 days.*")
    st.markdown("*Please validate the due date with your healthcare provider, as this tool is for informational purposes only.*")
    pregnancy_duration = 280
    radiobutton_calculate_by_options = ["Last Menstrual Period (Start Date)", "Conception Date", "IVF Transfer Date", "Due Date"]
    radiobutton_calculate_by = st.radio("Calculation Option:", radiobutton_calculate_by_options)
    if radiobutton_calculate_by == "Last Menstrual Period (Start Date)":    
        last_menstral_date = st.date_input("Date of Last Menstrual Period")
        due_date = calculate_due_date_by_last_menstrual_period(last_menstral_date, pregnancy_duration)
        if last_menstral_date > datetime.now().date():
            st.error("The date of the last menstrual period cannot be in the future.")
            return
        elif datetime.now().date() > due_date:
            st.error("The due date cannot be in the past.")
            return
    elif radiobutton_calculate_by == "Conception Date":
        date_of_conception = st.date_input("Date of Conception")
        due_date = date_of_conception + timedelta(days=266)
        last_menstral_date = date_of_conception - timedelta(days=14)
        if last_menstral_date > datetime.now().date():
            st.error("The date of the last menstrual period cannot be in the future.")
            return
        elif datetime.now().date() > due_date:
            st.error("The due date cannot be in the past.")
            return
    elif radiobutton_calculate_by == "IVF Transfer Date":
        date_of_ivf_transfer = st.date_input("Date of IVF Transfer")
        radiobutton_embryo_stage_options = ["Day 3", "Day 5"]
        radiobutton_embryo = st.radio("Embryo Stage days:", radiobutton_embryo_stage_options)
        due_date, last_menstral_date = calculate_ivf_last_menstrual_period(date_of_ivf_transfer, pregnancy_duration, radiobutton_embryo)
        if last_menstral_date > datetime.now().date():
            st.error("The date of the last menstrual period cannot be in the future.")
            return
        elif datetime.now().date() > due_date:
            st.error("The due date cannot be in the past.")
            return
    elif radiobutton_calculate_by == "Due Date":
        date_of_due_date = st.date_input("Date of Due Date")
        due_date = date_of_due_date
        last_menstral_date =calculate_last_menstrual_period_by_due_date(due_date, pregnancy_duration)
    if due_date and pregnancy_duration and last_menstral_date:
        st.header("Pregnancy Summary")
        df, weeks_pregnant = get_summary_details_dataframe(due_date, pregnancy_duration, last_menstral_date)
        data_container = st.container()
        with data_container:
            table, plot = st.columns(2)
            with table:
                st.dataframe(df, hide_index=True,use_container_width=True)
            with plot:
                st.altair_chart(make_donut(calculate_percentage_of_pregnancy_completed(last_menstral_date, pregnancy_duration), 'Pregnancy Precentage Completed', 'red'), use_container_width=True)
        week_dates= create_pregnancy_timeline(last_menstral_date.strftime("%Y-%m-%d"), due_date.strftime("%Y-%m-%d"))
        st.header("Your Journey")
        st.dataframe(week_dates.style.apply(highlight_row, axis=1), hide_index=True, height=1475, use_container_width=True)
        st.header("Current Week Details")
        current_week_details = get_current_week_details(weeks_pregnant)
        st.dataframe(current_week_details, use_container_width=True)
app()
