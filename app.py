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

# Create a mapping dictionary for fast lookup based on GT Code
df['GT Code_str'] = df['GT Code'].astype(str)
gt_mapping = {}
for _, row in df.iterrows():
    gt = str(row['GT Code']) if pd.notna(row['GT Code']) else "N/A"
    gt_mapping[gt] = {
        'size': str(row['Tyre size']),
        'd_base': float(row['2 Builder'])
    }

gt_list = list(gt_mapping.keys())

# Initialize rows state
if 'rows' not in st.session_state:
    st.session_state.rows = [{'gt': gt_list[0] if gt_list else "", 'tyre': "", 'min': ""}]

# Top Control & Summary Panel
top_container = st.container()

with top_container:
    control_col1, col_add, col_del, col_t, col_m, col_diff = st.columns([2, 1, 1, 2, 2, 3])
    
    with control_col1:
        builder_mode = st.selectbox("Builder Mode", ["2 Builder", "1 Builder"])

    multiplier = 0.5 if builder_mode == "1 Builder" else 1.0
    target_time = 450.0 if builder_mode == "1 Builder" else 480.0
    header_d_label = "1 Builder (D)" if builder_mode == "1 Builder" else "2 Builder (D)"

    with col_add:
        st.write("")
        if st.button("➕ Add Row"):
            st.session_state.rows.append({'gt': gt_list[0] if gt_list else "", 'tyre': "", 'min': ""})
            st.rerun()

    with col_del:
        st.write("")
        if st.button("🗑️ Delete Last") and len(st.session_state.rows) > 1:
            st.session_state.rows.pop()
            st.rerun()

st.markdown("---")

# Table Headers
hcol1, hcol2, hcol3, hcol4, hcol5 = st.columns([2, 4, 2, 2, 2])
hcol1.markdown("**GT Code (Combo)**")
hcol2.markdown("**Tyre Size**")
hcol3.markdown(f"**{header_d_label}**")
hcol4.markdown("**No. of Tyres (E)**")
hcol5.markdown("**Time (Minutes) (F)**")

total_tyres = 0.0
total_mins = 0.0

# Render dynamic rows
for i, row_data in enumerate(st.session_state.rows):
    rcol1, rcol2, rcol3, rcol4, rcol5 = st.columns([2, 4, 2, 2, 2])
    
    # GT Code Combox selection
    selected_gt = rcol1.selectbox("", gt_list, index=gt_list.index(row_data['gt']) if row_data['gt'] in gt_list else 0, key=f"gt_{i}", label_visibility="collapsed")
    st.session_state.rows[i]['gt'] = selected_gt
    
    # Lookup details from dictionary
    details = gt_mapping.get(selected_gt, {'size': '', 'd_base': 0.0})
    current_d = details['d_base'] * multiplier
    
    rcol2.write(details['size'])
    rcol3.write(f"{current_d:.2f}")
    
    # Text input values
    current_tyre_val = row_data['tyre']
    current_min_val = row_data['min']
    
    t_input = rcol4.text_input("", value=current_tyre_val, key=f"t_{i}", label_visibility="collapsed")
    m_input = rcol5.text_input("", value=current_min_val, key=f"m_{i}", label_visibility="collapsed")
    
    # Handle Live 2-way Calculations & State tracking
    if t_input != current_tyre_val:
        st.session_state.rows[i]['tyre'] = t_input
        try:
            if t_input.strip() != "":
                t_num = float(t_input)
                m_num = round((target_time / current_d) * t_num, 2)
                st.session_state.rows[i]['min'] = str(m_num)
            else:
                st.session_state.rows[i]['min'] = ""
        except ValueError:
            pass
        st.rerun()

    elif m_input != current_min_val:
        st.session_state.rows[i]['min'] = m_input
        try:
            if m_input.strip() != "":
                m_num = float(m_input)
                t_num = round((m_num * current_d) / target_time, 2)
                st.session_state.rows[i]['tyre'] = str(t_num)
            else:
                st.session_state.rows[i]['tyre'] = ""
        except ValueError:
            pass
        st.rerun()

    # Accumulate totals
    try:
        if st.session_state.rows[i]['tyre'].strip() != "":
            total_tyres += float(st.session_state.rows[i]['tyre'])
    except ValueError:
        pass
        
    try:
        if st.session_state.rows[i]['min'].strip() != "":
            total_mins += float(st.session_state.rows[i]['min'])
    except ValueError:
        pass

# Render summary stats into top panel columns
diff_val = target_time - total_mins
with col_t:
    st.metric("Total Tyres", f"{total_tyres:.2f}")
with col_m:
    st.metric("Total Mins", f"{total_mins:.2f}")
with col_diff:
    st.markdown(f"<p style='font-weight:bold; color:red; padding-top:20px;'>({target_time:.0f} - {total_mins:.2f} = {diff_val:.2f})</p>", unsafe_allow_html=True)
