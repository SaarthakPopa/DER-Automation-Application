import streamlit as st
import json
import re
import pandas as pd
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
 'walgreens-prod': 'Walgreens',
'champion-prod' : 'Champion Health Plan',
'mdxhawaii-prod' : 'MDX Hawaii'
'recuro-prod' : 'Recuro Health'
'mhpartner-prod' : 'Mission Health Partners'
  }

def add_health_system(df):
    df = df.copy()
    df.insert(1, "Health System Name", df["customer"].map(mapping).fillna(""))
    return df

# =========================================================
# -------- CONTACT VALIDITY (FINAL & CORRECT) --------------
# =========================================================
CATEGORY_CONFIG = {
    "Total": "",
    "With Contact" : "_patients_with_contact_number" ,
    "With Email" : "_patients_with_email",
    "Only Contact": "_patients_with_only_contact",
    "Only Email": "_patients_with_only_email",
    "Both Contact and Email": "_patients_with_both_contact_and_email",
    "None Available": "_patients_with_neither_contact_nor_email"
}


def detect_base_metrics(columns):
    return [
        c for c in columns
        if c.startswith("NUM_")
        and not c.endswith("_PATIENTS_WITH_CONTACT_NUMBER")
        and not c.endswith("_PATIENTS_WITH_EMAIL")
        and not c.endswith("_PATIENTS_WITH_ONLY_CONTACT")
        and not c.endswith("_PATIENTS_WITH_ONLY_EMAIL")
        and not c.endswith("_PATIENTS_WITH_BOTH_CONTACT_AND_EMAIL")
        and not c.endswith("_PATIENTS_WITH_NEITHER_CONTACT_NOR_EMAIL")
    ]


def compile_contact_validity(df):
    records = []

    den_cols = [c for c in df.columns if c.startswith("den_")]
    num_cols = [
        c for c in df.columns
        if c.startswith("num_")
        and not c.endswith((
            "_patients_with_contact_number",
            "_patients_with_email",
            "_patients_with_only_contact",
            "_patients_with_only_email",
            "_patients_with_both_contact_and_email",
            "_patients_with_neither_contact_nor_email"
        ))
    ]

    for _, row in df.iterrows():
        for category, suffix in CATEGORY_CONFIG.items():
            out = {
                "customer": row["customer"],
                "Category": category
            }

            # Denominators → only Total
            for den in den_cols:
                out[den] = row[den] if category == "Total" else 0

            # Numerators
            for num in num_cols:
                col = num + suffix if suffix else num
                out[num] = row[col] if col in df.columns else 0

            records.append(out)

    result = pd.DataFrame(records)
    result = add_health_system(result)
    return result



def reorder_contact_validity_columns(df):
    fixed_cols = ["customer", "Health System Name", "Category"]

    den_cols = sorted([c for c in df.columns if c.startswith("den_")])
    num_cols = sorted([c for c in df.columns if c.startswith("num_")])

    ordered_metric_cols = []

    for den in den_cols:
        suffix = den.replace("den_", "")
        matching_num = f"num_{suffix}"

        ordered_metric_cols.append(den)
        if matching_num in num_cols:
            ordered_metric_cols.append(matching_num)

    # Add any remaining num columns (safety)
    remaining_nums = [c for c in num_cols if c not in ordered_metric_cols]
    ordered_metric_cols.extend(remaining_nums)

    return df[fixed_cols + ordered_metric_cols]




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
            dfs = [pd.read_csv(f) for f in uploaded_files]
            df = pd.concat(dfs, ignore_index=True)

            if "customer" not in df.columns:
                st.error("❌ 'customer' column is mandatory")
                st.stop()

            numeric_cols = df.select_dtypes(include="number").columns
            final_df = df.groupby("customer", as_index=False)[numeric_cols].sum()
            final_df = add_health_system(final_df)

            st.dataframe(final_df, use_container_width=True)

        # ============ MORE THAN 2 COLUMNS =================
        elif mode == "Use this for more than 2 columns":
            df = pd.concat([pd.read_csv(f) for f in uploaded_files], ignore_index=True)
            df = add_health_system(df)

            st.dataframe(df, use_container_width=True)

        # ============ CONTACT VALIDITY (FINAL) ============

        elif mode == "Contact Validity Compilation":

                dfs = []
                for file in uploaded_files:
                    temp = pd.read_csv(file)
                    if not temp.empty:
                        dfs.append(temp)

                if not dfs:
                    st.error("❌ No valid CSV files uploaded")
                    st.stop()

                merged_df = dfs[0]
                for d in dfs[1:]:
                    merged_df = merged_df.merge(d, on="customer", how="outer")

                merged_df = merged_df.fillna(0)
            
                final_df = compile_contact_validity(merged_df)
                final_df = reorder_contact_validity_columns(final_df)

            
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





