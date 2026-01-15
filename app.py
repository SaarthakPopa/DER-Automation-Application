import streamlit as st
import json
import re
import io
import pandas as pd
from pandas.errors import EmptyDataError
from functools import reduce

# =========================================================
# APP CONFIG
# =========================================================
st.set_page_config(page_title="LifeSciences DER Automation Tool", layout="wide")
st.title("🧬 LifeSciences DER Automation Tool")

app_choice = st.selectbox(
    "Choose an operation",
    ["DER JSON Creator", "DER ZIP Data Compiler"]
)

st.divider()

# =========================================================
# ---------------- APP 1 : DER JSON CREATOR ----------------
# =========================================================
def clean_sql_query(file):
    content = file.read().decode("utf-8")
    content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)
    content = re.sub(r"--.*?$", "", content, flags=re.MULTILINE)
    return re.sub(r"\s+", " ", content).strip()

def create_final_json(uploaded_files):
    metrics = []
    for idx, uploaded_file in enumerate(uploaded_files, start=1):
        cleaned_query = clean_sql_query(uploaded_file)
        metrics.append({
            "id": idx,
            "metric": f"DER_{uploaded_file.name}",
            "level": "l2",
            "supported_customers": {
                "included": [],
                "excluded": [
                    "kaiser-staging","kpphm-prod","kpphmi-prod",
                    "kpphmi-staging","kpwa-prod","kpwa-staging","jhah-prod"
                ]
            },
            "queries": {
                "snowflake": {"database": "DAP","schema": "L2","query": cleaned_query},
                "postgres": {"database": "postgres","schema": "l2","query": cleaned_query}
            }
        })
    return {"metrics": metrics}

# =========================================================
# ---------------- HEALTH SYSTEM MAPPING -------------------
# =========================================================
mapping = {'advantasure-prod': 'Advantasure (Env 1)',
 'advantasureapollo-prod': 'Advantasure (Env 2)',
 'adventist-prod': 'Adventist Healthcare',
 'alameda-prod': 'Alameda County',
 'alo-prod': 'Alo solutions',
 'arkansashealth-prod': 'Chi St Vincent',
 'ascension-preprod': 'Ascension Health (Env 1)',
 'ascension-prod': 'Ascension Health (Env 2)',
 'atlantichealth-prod': 'Atlantic Health',
 'bannerapollo-prod': 'Banner Health',
 'bhsf-prod': 'Baptist Health South Florida',
 'bsim-prod': 'BSIM Healthcare services',
 'careabout-prod': 'CareAbout Health',
 'ccmcn-prod': 'Colorado Community Managed Care Network',
 'ccnc-prod': 'Community Care of North Carolina',
 'chessapollo-prod': 'CHESS Health Solutions',
 'childrenshealthapollo-prod': 'Children Health Alliance',
 'christianacare-prod': 'Christiana Care Health System',
 'cmhcapollo-prod': 'Central Maine Healthcare',
 'cmicsapollo-prod': 'Childrens Mercy Hospital And Clinics',
 'coa-prod': 'Colorado Access',
 'concare-prod': 'ConcertoCare',
 'connecticutchildrens-prod': "Connecticut Children's Health",
 'cshnational-new-prod': 'CSH National (Env 1)',
 'cshnational-prod': 'CSH National (Env 2)',
 'curana-prod': 'Curana Health',
 'dhmsapollo-prod': 'Dignity Health',
 'dock-cmicsapollo-prod': 'Childrens Mercy Hospital And Clinics (Nexus)',
 'dock-embrightapollo-prod': 'Embright (Nexus)',
 'dock-nemoursapollo-prod': 'Nemours Childrens Health System (Nexus)',
 'dock-risehealth-prod': 'Rise Health (Nexus)',
 'dock-tccn-prod': 'Childrens Healthcare Of Atlanta (Nexus)',
 'embrightapollo-prod': 'Embright',
 'evergreen-prod': 'Evergreen Nephrology',
 'falliance-prod': 'Franciscan Health',
 'flmedicaid-prod': 'Florida Medicaid',
 'franciscan-staging': 'Franciscan Health (staging)',
 'govcloud-prod': 'govcloud-prod',
 'gravitydemo-prod': 'Gravity',
 'impacthealth-prod': 'Impact Primary Care Network/Impact Health',
 'innohumana-prod': 'Longevity Health Plan(LHP) - HUMANA',
 'innolhp-prod': 'Longevity Health Plan(LHP) - Core)',
 'innovaetna-prod': 'Longevity Health Plan(LHP) - Aetna',
 'integration-preprod': 'internal env',
 'integris-prod': 'integris-prod',
 'intjuly-prod': 'internal account',
 'longitudegvt-prod': 'LongitudeRx (Env 1)',
 'longituderx-prod': 'LongitudeRx (Env 2)',
 'mcs-prod': 'Medical Card System',
 'mercyoneapollo-prod': 'MercyOne',
 'mercypit-prod': 'Trinity Health Pittsburgh',
 'mgm-prod': 'Mgm Resorts',
 'mhcn-prod': 'Chi Memorial',
 'nemoursapollo-prod': 'Nemours Childrens Health System',
 'novanthealth-prod':'Novant Health',
 'nwm-prod': 'Northwestern Medicine',
 'orlandoapollo-prod': 'Orlando Health',
 'pedassoc-prod': 'Pediatric Associates',
 'phlc-prod': 'Population Health Learning Center',
 'php-prod': 'P3 Health Partners',
 'pophealthcare-prod': 'Emcara / POP Health / Guidewell Mutual Holding Company',
 'prismah-prod': 'Prisma Health',
 'pswapollo-prod': 'Physicians Of Southwest Washington',
 'risehealth-prod': 'Rise Health',
 'sacramento-prod': 'Sacramento SHIE (Env 1)',
 'sacramentoshie-prod': 'Sacramento SHIE (Env 2)',
 'sentara-prod': 'Sentara Health',
 'smch-prod': 'San Mateo County Health ',
 'stewardapollo-prod': 'Steward Health Care System',
 'strivehealth-prod': 'Strive Health',
 'tccn-prod': 'Childrens Healthcare Of Atlanta',
 'thnapollo-prod': 'Cone Health',
 'trinity-prod': 'Trinity Health National',
 'uninet-prod': 'CHI Health Partners',
 'usrc-prod': 'US RenalCare',
 'walgreens-prod': 'Walgreens'}  # keep full mapping as needed

def add_health_system(df):
    df = df.copy()
    df.insert(1, "Health System Name", df["customer"].map(mapping).fillna(""))
    return df

# =========================================================
# -------- CONTACT VALIDITY (GENERIC / DYNAMIC) ------------
# =========================================================
CATEGORY_SUFFIX_MAP = {
    "": "Total",
    "_PATIENTS_WITH_CONTACT_NUMBER": "with contact number",
    "_WITH_CONTACT_NUMBER": "with contact number",
    "_PATIENTS_WITH_EMAIL": "with email",
    "_PATIENTS_WITH_ONLY_CONTACT": "only contact number",
    "_PATIENTS_WITH_ONLY_EMAIL": "only email",
    "_PATIENTS_WITH_BOTH_CONTACT_AND_EMAIL": "with both email and contact",
    "_PATIENTS_WITH_NEITHER_CONTACT_NOR_EMAIL": "with neither contact nor email"
}

def detect_base_metrics(columns):
    return [
        c for c in columns
        if c.startswith("NUM_") and "_PATIENTS_" not in c and "_WITH_" not in c
    ]

def compile_contact_validity_single_df(df):
    records = []
    base_metrics = detect_base_metrics(df.columns)

    for base_metric in base_metrics:
        for _, row in df.iterrows():
            for suffix, category in CATEGORY_SUFFIX_MAP.items():
                col = base_metric + suffix
                if col in df.columns:
                    records.append({
                        "customer": row["customer"],
                        "Category": category,
                        "Metric": base_metric,
                        "Value": row[col]
                    })

    out = pd.DataFrame(records)
    out = add_health_system(out)

    out = out.pivot_table(
        index=["customer", "Health System Name", "Category"],
        columns="Metric",
        values="Value",
        fill_value=0
    ).reset_index()

    return out

# =========================================================
# ---------------- APP 2 : DER ZIP COMPILER ----------------
# =========================================================
if app_choice == "DER ZIP Data Compiler":
    st.header("📦 DER ZIP Data Compiler")

    mode = st.selectbox(
        "Select processing mode",
        [
            "Aggregated (Customer level)",
            "Use this for more than 2 columns",
            "Contact Validity Compilation"
        ]
    )

    uploaded_files = st.file_uploader(
        "Upload CSV files",
        type=["csv"],
        accept_multiple_files=True
    )

    if uploaded_files:

        # ================= AGGREGATED =================
        if mode == "Aggregated (Customer level)":
            df = pd.concat([pd.read_csv(f) for f in uploaded_files], ignore_index=True)

            if "customer" not in df.columns:
                st.error("❌ 'customer' column is mandatory")
                st.stop()

            numeric_cols = df.select_dtypes(include="number").columns
            final_df = df.groupby("customer", as_index=False)[numeric_cols].sum()
            final_df = add_health_system(final_df)

        # ============ MORE THAN 2 COLUMNS (PIVOT) ============
        elif mode == "Use this for more than 2 columns":
            df = pd.concat([pd.read_csv(f) for f in uploaded_files], ignore_index=True)
            df = add_health_system(df)

            st.markdown("### 📊 Base Output")
            st.dataframe(df, use_container_width=True)

            all_cols = df.columns.tolist()
            numeric_cols = df.select_dtypes(include="number").columns.tolist()

            rows = st.multiselect("Rows", all_cols)
            columns = st.multiselect("Columns", all_cols)
            values = st.multiselect("Values (numeric only)", numeric_cols)
            agg_func = st.selectbox("Aggregation Function", ["sum", "mean", "count", "min", "max"])

            if rows and values:
                final_df = pd.pivot_table(
                    df,
                    index=rows,
                    columns=columns if columns else None,
                    values=values,
                    aggfunc=agg_func,
                    fill_value=0
                ).reset_index()
            else:
                st.stop()

        # ============ CONTACT VALIDITY =================
        else:
            compiled_dfs = []

            for file in uploaded_files:
                try:
                    df = pd.read_csv(file)

                    if df.empty:
                        st.warning(f"⚠️ Skipped empty file: {file.name}")
                        continue

                    if "customer" not in df.columns:
                        st.warning(f"⚠️ 'customer' missing in {file.name}, skipped")
                        continue

                    compiled_dfs.append(compile_contact_validity_single_df(df))

                except EmptyDataError:
                    st.warning(f"⚠️ Skipped empty file: {file.name}")

            if not compiled_dfs:
                st.error("❌ No valid files to process")
                st.stop()

            final_df = reduce(
                lambda l, r: pd.merge(
                    l, r,
                    on=["customer", "Health System Name", "Category"],
                    how="outer"
                ),
                compiled_dfs
            ).fillna(0)

        st.subheader("📊 Final Output")
        st.dataframe(final_df, use_container_width=True)

        st.download_button(
            "⬇️ Download Final CSV",
            final_df.to_csv(index=False),
            "final.csv",
            "text/csv"
        )

# =========================================================
# ---------------- APP 1 UI -------------------------------
# =========================================================
if app_choice == "DER JSON Creator":
    st.header("📌 DER JSON Creator")

    uploaded_files = st.file_uploader(
        "Upload SQL files",
        type=["sql"],
        accept_multiple_files=True
    )

    if uploaded_files:
        final_json = create_final_json(uploaded_files)
        st.json(final_json)

        st.download_button(
            "⬇️ Download JSON",
            json.dumps(final_json, indent=4),
            "DER_JSON_FINAL.json",
            "application/json"
        )

