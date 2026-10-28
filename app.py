import streamlit as st
import pandas as pd

st.set_page_config(page_title="Tyre Equivalent Production Calculator", layout="wide")

st.title("Tyre Production & Time Calculator")

# Load data from Excel
@st.cache_data
def load_data():
    file_name = "Tyre Equalent Formula.xlsx"
    df = pd.read_excel(file_name, sheet_name=0)
    return df.dropna(subset=['Tyre size', '2 Builder']).reset_index(drop=True)

try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading Excel file: {e}")
    st.stop()

# Top Control & Summary Panel
control_col1, control_col2, control_col3, control_col4 = st.columns([2, 2, 2, 4])
with control_col1:
    builder_mode = st.selectbox("Builder Mode", ["2 Builder", "1 Builder"])

multiplier = 0.5 if builder_mode == "1 Builder" else 1.0
target_time = 450.0 if builder_mode == "1 Builder" else 480.0
header_d_label = "1 Builder (D)" if builder_mode == "1 Builder" else "2 Builder (D)"

st.markdown("---")

# Table Headers
hcol1, hcol2, hcol3, hcol4, hcol5 = st.columns([1.5, 4, 2, 2, 2])
hcol1.markdown("**GT Code**")
hcol2.markdown("**Tyre Size**")
hcol3.markdown(f"**{header_d_label}**")
hcol4.markdown("**No. of Tyres (E)**")
hcol5.markdown("**Time (Minutes) (F)**")

total_tyres = 0.0
total_mins = 0.0

# Render rows dynamically using number inputs for instant live updates
for idx, row in df.iterrows():
    gt_code = str(row['GT Code']) if pd.notna(row['GT Code']) else ""
    tyre_size = str(row['Tyre size'])
    d_base = float(row['2 Builder'])
    current_d = d_base * multiplier
    
    rcol1, rcol2, rcol3, rcol4, rcol5 = st.columns([1.5, 4, 2, 2, 2])
    
    rcol1.write(gt_code)
    rcol2.write(tyre_size)
    rcol3.write(f"{current_d:.2f}")
    
    t_key = f"tyre_{idx}"
    m_key = f"min_{idx}"
    
    # Using number_input with step=None to look clean and update instantly
    tyre_val = rcol4.number_input("", min_value=0.0, value=0.0, step=None, key=t_key, label_visibility="collapsed")
    min_val = rcol5.number_input("", min_value=0.0, value=0.0, step=None, key=m_key, label_visibility="collapsed")
    
    # Calculation logic
    if tyre_val > 0:
        t = float(tyre_val)
        total_tyres += t
        m = round((target_time / current_d) * t, 2)
        total_mins += m
    elif min_val > 0:
        m = float(min_val)
        total_mins += m
        t = round((m * current_d) / target_time, 2)
        total_tyres += t

# Live Summary Panel at Top / Bottom
st.markdown("---")
diff_val = target_time - total_mins
summary_cols = st.columns(3)
summary_cols[0].metric("Total Tyres Made", f"{total_tyres:.2f}")
summary_cols[1].metric("Total Minutes", f"{total_mins.2f}")
summary_cols[2].markdown(f"### Target Diff: <span style='color:red'>({target_time:.0f} - {total_mins:.2f} = {diff_val:.2f})</span>", unsafe_allow_html=True)
