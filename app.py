import streamlit as st
import json
import re
import pandas as pd

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
                "snowflake": {"database": "DAP","schema": "L2","query": clean_sql_query(uploaded_file)},
                "postgres": {"database": "postgres","schema": "l2","query": clean_sql_query(uploaded_file)}
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
 'walgreens-prod': 'Walgreens',
'champion-prod' : 'Champion Health Plan',
'mdxhawaii-prod' : 'MDX Hawaii',
'recuro-prod' : 'Recuro Health',
'mhpartner-prod' : 'Mission Health Partners'
  }

def add_health_system(df):
    df = df.copy()
    df.insert(1, "Health System Name", df["customer"].map(mapping).fillna(""))
    return df

# =========================================================
# -------- CONTACT VALIDITY (OPTIMIZED & SAFE) -------------
# =========================================================
CATEGORY_CONFIG = {
    "Total": "",
    "With Contact": "_patients_with_contact_number",
    "With Email": "_patients_with_email",
    "Only Contact": "_patients_with_only_contact",
    "Only Email": "_patients_with_only_email",
    "Both Contact and Email": "_patients_with_both_contact_and_email",
    "None Available": "_patients_with_neither_contact_nor_email"
}

def compile_contact_validity(df):
    den_cols = [c for c in df.columns if c.startswith("den_")]
    num_base_cols = [
        c for c in df.columns
        if c.startswith("num_") and "_patients_" not in c
    ]

    output_rows = []

    for _, row in df.iterrows():
        for category, suffix in CATEGORY_CONFIG.items():
            record = {
                "customer": row["customer"],
                "Category": category
            }

            for den in den_cols:
                record[den] = row[den] if category == "Total" else 0

            for num in num_base_cols:
                col = num + suffix if suffix else num
                record[num] = row[col] if col in df.columns else 0

            output_rows.append(record)

    result = pd.DataFrame(output_rows)
    return add_health_system(result)

def reorder_contact_validity_columns(df):
    fixed = ["customer", "Health System Name", "Category"]
    den = sorted([c for c in df.columns if c.startswith("den_")])
    num = sorted([c for c in df.columns if c.startswith("num_")])

    ordered = []
    for d in den:
        ordered.append(d)
        n = "num_" + d.replace("den_", "")
        if n in num:
            ordered.append(n)

    remaining = [c for c in num if c not in ordered]
    return df[fixed + ordered + remaining]

# =========================================================
# ---------------- APP 2 : DER ZIP COMPILER ----------------
# =========================================================
if app_choice == "DER ZIP Data Compiler":
    st.header("📦 DER ZIP Data Compiler")

    mode = st.selectbox(
        "Select processing mode",
        ["Aggregated (Customer level)", "Use this for more than 2 columns", "Contact Validity Compilation"]
    )

    uploaded_files = st.file_uploader("Upload CSV files", type=["csv"], accept_multiple_files=True)

    if uploaded_files:

        if mode == "Contact Validity Compilation":

            dfs = []
            for f in uploaded_files:
                temp = pd.read_csv(f)
                if not temp.empty:
                    dfs.append(temp)

            merged = dfs[0]
            for d in dfs[1:]:
                merged = merged.merge(d, on="customer", how="outer")

            merged = merged.fillna(0)

            final_df = reorder_contact_validity_columns(
                compile_contact_validity(merged)
            )

            # 🔥 SAFE PREVIEW (NO CRASH)
            st.subheader("📊 Preview (First 100 Rows)")
            st.caption(f"Total Rows: {len(final_df):,} | Total Columns: {len(final_df.columns)}")
            st.dataframe(final_df.head(100), use_container_width=True)

            st.download_button(
                "⬇️ Download Full CSV",
                final_df.to_csv(index=False),
                "contact_validity_final.csv",
                "text/csv"
            )

# =========================================================
# ---------------- APP 1 UI -------------------------------
# =========================================================
if app_choice == "DER JSON Creator":
    st.header("📌 DER JSON Creator")

    uploaded_files = st.file_uploader("Upload SQL files", type=["sql"], accept_multiple_files=True)

    if uploaded_files:
        final_json = create_final_json(uploaded_files)
        st.json(final_json)
        st.download_button(
            "⬇️ Download JSON",
            json.dumps(final_json, indent=4),
            "DER_JSON_FINAL.json",
            "application/json"
        )
