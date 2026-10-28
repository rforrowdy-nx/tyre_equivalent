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
    st.error(f"Error loading Excel file (Make sure 'Tyre Equalent Formula.xlsx' is uploaded to GitHub): {e}")
    st.stop()

# Initialize Session State values for rows if not already present
for idx in range(len(df)):
    if f"t_{idx}" not in st.session_state:
        st.session_state[f"t_{idx}"] = 0.0
    if f"m_{idx}" not in st.session_state:
        st.session_state[f"m_{idx}"] = 0.0

# Top Control Panel & Summary Display Container
top_container = st.container()

with top_container:
    control_col1, separator, col_t, col_m, col_diff = st.columns([2, 0.5, 2, 2, 3])
    
    with control_col1:
        builder_mode = st.selectbox("Builder Mode", ["2 Builder", "1 Builder"])

    multiplier = 0.5 if builder_mode == "1 Builder" else 1.0
    target_time = 450.0 if builder_mode == "1 Builder" else 480.0
    header_d_label = "1 Builder (D)" if builder_mode == "1 Builder" else "2 Builder (D)"

# Callbacks for 2-way live sync
def update_from_tyre(idx, current_d, target_time):
    t = st.session_state[f"t_{idx}"]
    if t > 0:
        st.session_state[f"m_{idx}"] = round((target_time / current_d) * t, 2)
    else:
        st.session_state[f"m_{idx}"] = 0.0

def update_from_min(idx, current_d, target_time):
    m = st.session_state[f"m_{idx}"]
    if m > 0:
        st.session_state[f"t_{idx}"] = round((m * current_d) / target_time, 2)
    else:
        st.session_state[f"t_{idx}"] = 0.0

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

# Render rows dynamically
for idx, row in df.iterrows():
    gt_code = str(row['GT Code']) if pd.notna(row['GT Code']) else ""
    tyre_size = str(row['Tyre size'])
    d_base = float(row['2 Builder'])
    current_d = d_base * multiplier
    
    rcol1, rcol2, rcol3, rcol4, rcol5 = st.columns([1.5, 4, 2, 2, 2])
    
    rcol1.write(gt_code)
    rcol2.write(tyre_size)
    rcol3.write(f"{current_d:.2f}")
    
    t_key = f"t_{idx}"
    m_key = f"m_{idx}"
    
    # Number inputs with event callbacks
    rcol4.number_input("", min_value=0.0, step=None, key=t_key, label_visibility="collapsed",
                       on_change=update_from_tyre, args=(idx, current_d, target_time))
    rcol5.number_input("", min_value=0.0, step=None, key=m_key, label_visibility="collapsed",
                       on_change=update_from_min, args=(idx, current_d, target_time))
    
    total_tyres += st.session_state[t_key]
    total_mins += st.session_state[m_key]

# Render summary stats dynamically back into the top control panel columns
diff_val = target_time - total_mins
with col_t:
    st.metric("Total Tyres", f"{total_tyres:.2f}")
with col_m:
    st.metric("Total Mins", f"{total_mins:.2f}")
with col_diff:
    st.markdown(f"<p style='font-size:16 font-weight:bold; color:red; padding-top:20px;'>({target_time:.0f} - {total_mins:.2f} = {diff_val:.2f})</p>", unsafe_allow_html=True)
