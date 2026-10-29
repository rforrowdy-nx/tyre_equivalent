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

# Create GT Code mapping and sort alphabetically
df['GT Code_str'] = df['GT Code'].astype(str)
gt_mapping = {}
for _, row in df.iterrows():
    gt = str(row['GT Code']) if pd.notna(row['GT Code']) else "N/A"
    gt_mapping[gt] = {
        'size': str(row['Tyre size']),
        'd_base': float(row['2 Builder'])
    }

# Sort the GT codes in alphabetical/ascending order
gt_list = sorted(list(gt_mapping.keys()))

# Row management state
if 'row_count' not in st.session_state:
    st.session_state.row_count = 1

# Top Control & Summary Panel
top_container = st.container()

with top_container:
    control_col1, col_add, col_del, col_t, col_m, col_diff = st.columns([2, 1, 1, 2, 2, 3])
    
    with control_col1:
        builder_mode = st.selectbox("Builder Mode", ["2 Builder", "1 Builder"], key="builder_mode")

    multiplier = 0.5 if builder_mode == "1 Builder" else 1.0
    target_time = 450.0 if builder_mode == "1 Builder" else 480.0
    header_d_label = "1 Builder (D)" if builder_mode == "1 Builder" else "2 Builder (D)"

    with col_add:
        st.write("")
        if st.button("➕ Add Row"):
            st.session_state.row_count += 1
            st.rerun()

    with col_del:
        st.write("")
        if st.button("🗑️ Delete Row") and st.session_state.row_count > 1:
            st.session_state.row_count -= 1
            st.rerun()

st.markdown("---")

# Table Headers
hcol1, hcol2, hcol3, hcol4, hcol5 = st.columns([2, 4, 2, 2, 2])
hcol1.markdown("**GT Code (Combo)**")
hcol2.markdown("**Tyre Size**")
hcol3.markdown(f"**{header_d_label}**")
hcol4.markdown("**No. of Tyres (E)**")
hcol5.markdown("**Time (Minutes) (F)**")

# Callbacks for 2-way live sync
def tyre_changed(i, current_d, target_time):
    val_key = f"t_{i}"
    min_key = f"m_{i}"
    try:
        val = float(st.session_state[val_key])
        if val > 0:
            st.session_state[min_key] = round((target_time / current_d) * val, 2)
        else:
            st.session_state[min_key] = 0.0
    except (ValueError, TypeError):
        st.session_state[min_key] = 0.0

def min_changed(i, current_d, target_time):
    val_key = f"m_{i}"
    tyre_key = f"t_{i}"
    try:
        val = float(st.session_state[val_key])
        if val > 0:
            st.session_state[tyre_key] = round((val * current_d) / target_time, 2)
        else:
            st.session_state[tyre_key] = 0.0
    except (ValueError, TypeError):
        st.session_state[tyre_key] = 0.0

total_tyres = 0.0
total_mins = 0.0

# Render dynamic rows based on row_count
for i in range(st.session_state.row_count):
    if f"t_{i}" not in st.session_state:
        st.session_state[f"t_{i}"] = 0.0
    if f"m_{i}" not in st.session_state:
        st.session_state[f"m_{i}"] = 0.0
    if f"gt_{i}" not in st.session_state:
        st.session_state[f"gt_{i}"] = gt_list[0] if gt_list else ""

    rcol1, rcol2, rcol3, rcol4, rcol5 = st.columns([2, 4, 2, 2, 2])
    
    selected_gt = rcol1.selectbox("", gt_list, key=f"gt_{i}", label_visibility="collapsed")
    
    details = gt_mapping.get(selected_gt, {'size': '', 'd_base': 0.0})
    current_d = details['d_base'] * multiplier
    
    rcol2.write(details['size'])
    rcol3.write(f"{current_d:.2f}")
    
    # Number inputs with instant 2-way callbacks
    rcol4.number_input("", min_value=0.0, step=None, key=f"t_{i}", label_visibility="collapsed",
                       on_change=tyre_changed, args=(i, current_d, target_time))
    rcol5.number_input("", min_value=0.0, step=None, key=f"m_{i}", label_visibility="collapsed",
                       on_change=min_changed, args=(i, current_d, target_time))
    
    total_tyres += float(st.session_state[f"t_{i}"])
    total_mins += float(st.session_state[f"m_{i}"])

# Render summary stats into top panel columns
diff_val = target_time - total_mins
with col_t:
    st.metric("Total Tyres", f"{total_tyres:.2f}")
with col_m:
    st.metric("Total Mins", f"{total_mins:.2f}")
with col_diff:
    st.markdown(f"<p style='font-weight:bold; color:red; padding-top:20px;'>({target_time:.0f} - {total_mins:.2f} = {diff_val:.2f})</p>", unsafe_allow_html=True)
