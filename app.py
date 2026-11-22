import pandas as pd
import streamlit as st

st.set_page_config(page_title="Tyre Equivalent Production Calculator", layout="wide")

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
    }
    .row-card {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.12);
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Tyre Production & Time Calculator")


@st.cache_data
def load_data():
    file_name = "Tyre Equalent Formula.xlsx"
    df = pd.read_excel(file_name, sheet_name=0)
    return df.dropna(subset=["Tyre size", "2 Builder"]).reset_index(drop=True)


try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading Excel file ('Tyre Equalent Formula.xlsx'): {e}")
    st.stop()

if "row_count" not in st.session_state:
    st.session_state.row_count = 1

# Builder Mode & Row Controls
col_mode, col_add, col_del, col_reload = st.columns([2, 1, 1, 1.2])

with col_mode:
    builder_mode = st.selectbox("Builder Mode", ["2 Builder", "1 Builder"], key="builder_mode")

multiplier = 0.5 if builder_mode == "1 Builder" else 1.0
target_time = 450.0 if builder_mode == "1 Builder" else 480.0
header_d_label = "1 Builder (D)" if builder_mode == "1 Builder" else "2 Builder (D)"

with col_add:
    st.write("")
    if st.button("➕ Add Row", use_container_width=True):
        st.session_state.row_count += 1
        st.rerun()

with col_del:
    st.write("")
    if st.button("🗑️ Delete Row", use_container_width=True) and st.session_state.row_count > 1:
        st.session_state.row_count -= 1
        st.rerun()

with col_reload:
    st.write("")
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Build GT mapping & master list
gt_mapping = {}
master_records = []

for _, row in df.iterrows():
    gt = str(row.iloc[0]).strip() if len(row) > 0 and pd.notna(row.iloc[0]) else "N/A"
    size = str(row.iloc[1]).strip() if len(row) > 1 and pd.notna(row.iloc[1]) else ""
    construction = str(row.iloc[2]).strip() if len(row) > 2 and pd.notna(row.iloc[2]) else ""
    d_base = float(row["2 Builder"]) if "2 Builder" in df.columns and pd.notna(row["2 Builder"]) else 0.0
    current_d = d_base * multiplier

    display_label = f"{gt} — {size} ({construction})" if construction else f"{gt} — {size}"
    gt_mapping[display_label] = {
        "gt": gt,
        "size": size,
        "construction": construction,
        "d_base": d_base,
        "current_d": current_d,
    }
    master_records.append(
        {
            "GT Code": gt,
            "Tyre Size": size,
            "Construction": construction,
            header_d_label: round(current_d, 2),
        }
    )

gt_list = sorted(list(gt_mapping.keys()), key=lambda s: s.lower())
master_df = pd.DataFrame(master_records).sort_values(by="GT Code", key=lambda col: col.astype(str).str.lower())

st.markdown("---")


def tyre_changed(i, current_d, target_time):
    val_key = f"t_{i}"
    min_key = f"m_{i}"
    try:
        val = float(st.session_state[val_key])
        if val > 0 and current_d > 0:
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
        if val > 0 and current_d > 0:
            st.session_state[tyre_key] = round((val * current_d) / target_time, 2)
        else:
            st.session_state[tyre_key] = 0.0
    except (ValueError, TypeError):
        st.session_state[tyre_key] = 0.0


def combo_changed(i, current_d, target_time):
    t_key = f"t_{i}"
    min_key = f"m_{i}"
    try:
        val = float(st.session_state[t_key])
        if val > 0 and current_d > 0:
            st.session_state[min_key] = round((target_time / current_d) * val, 2)
    except (ValueError, TypeError):
        pass


# Main Layout: Left = Calculation Cards, Right = Full Tyre Reference List
left_col, right_col = st.columns([1.35, 1])

total_tyres = 0.0
total_mins = 0.0
active_mins_list = []

with left_col:
    st.subheader("🧮 Production Entries")
    for i in range(st.session_state.row_count):
        if f"t_{i}" not in st.session_state:
            st.session_state[f"t_{i}"] = 0.0
        if f"m_{i}" not in st.session_state:
            st.session_state[f"m_{i}"] = 0.0
        if f"gt_{i}" not in st.session_state or st.session_state[f"gt_{i}"] not in gt_mapping:
            st.session_state[f"gt_{i}"] = gt_list[0] if gt_list else ""

        prev_gt = st.session_state.get(f"gt_{i}", gt_list[0] if gt_list else "")
        curr_d_temp = gt_mapping.get(prev_gt, {"current_d": 0.0})["current_d"]

        st.markdown("<div class='row-card'>", unsafe_allow_html=True)
        selected_label = st.selectbox(
            f"GT / Tyre Size (Construction) — Item {i + 1}",
            gt_list,
            key=f"gt_{i}",
            on_change=combo_changed,
            args=(i, curr_d_temp, target_time),
        )

        details = gt_mapping.get(selected_label, {"gt": "", "size": "", "construction": "", "current_d": 0.0})
        current_d = details["current_d"]

        st.markdown(f"**{header_d_label}:** `{current_d:.2f}`")

        ic1, ic2 = st.columns(2)
        with ic1:
            st.number_input(
                "No. of Tyres (E)",
                min_value=0.0,
                step=1.0,
                key=f"t_{i}",
                on_change=tyre_changed,
                args=(i, current_d, target_time),
            )
        with ic2:
            st.number_input(
                "Time Mins (F)",
                min_value=0.0,
                step=1.0,
                key=f"m_{i}",
                on_change=min_changed,
                args=(i, current_d, target_time),
            )
        st.markdown("</div>", unsafe_allow_html=True)

        try:
            t_val = float(st.session_state[f"t_{i}"])
            m_val = float(st.session_state[f"m_{i}"])
            if t_val > 0 and m_val > 0:
                total_tyres += t_val
                total_mins += m_val
                active_mins_list.append(f"{m_val:.2f}")
        except (ValueError, TypeError):
            pass

with right_col:
    st.subheader("📋 All Tyre Details")
    search_query = st.text_input("Search GT Code, Size, or Construction", placeholder="Type to filter...")
    filtered_df = master_df
    if search_query.strip():
        q = search_query.strip().lower()
        mask = master_df.apply(lambda r: q in " ".join(r.astype(str)).lower(), axis=1)
        filtered_df = master_df[mask]

    st.dataframe(filtered_df, use_container_width=True, hide_index=True, height=420)

# Summary Section at the Bottom
st.markdown("---")
diff_val = target_time - total_mins
st.subheader("📊 Summary Panel")

s_col1, s_col2 = st.columns(2)
s_col1.metric("Total Tyres", f"{total_tyres:.2f}")
s_col2.metric("Total Mins", f"{total_mins:.2f}")

if active_mins_list:
    mins_breakdown = " + ".join(active_mins_list)
    formula_display = f"({target_time:.0f} - [{mins_breakdown}] = {total_mins:.2f} = {diff_val:.2f})"
else:
    formula_display = f"({target_time:.0f} - 0.00 = {target_time:.2f})"

st.markdown(
    f"<h4 style='text-align: center; color: #ef4444;'>Target Diff: {formula_display}</h4>",
    unsafe_allow_html=True,
)
