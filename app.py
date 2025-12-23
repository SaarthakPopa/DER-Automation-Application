import streamlit as st
import json
import re
import io
import zipfile
import pandas as pd

# =========================================================
# APP CONFIG
# =========================================================
st.set_page_config(
    page_title="LifeSciences DER Automation Tool",
    layout="wide"
)

st.title("🧬 LifeSciences DER Automation Tool")

st.markdown(
    """
    Select the automation you want to run:
    - **DER JSON Creator** → Generate metric JSONs from SQL files  
    - **DER ZIP Data Compiler** → Aggregate DER CSVs from a ZIP file
    """
)

app_choice = st.selectbox(
    "Choose an operation",
    [
        "DER JSON Creator",
        "DER ZIP Data Compiler"
    ]
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

        metric_block = {
            "id": idx,
            "metric": f"DER_{275 + idx - 1}",
            "level": "l2",
            "supported_customers": {
                "included": [],
                "excluded": [
                    "kaiser-staging",
                    "kpphm-prod",
                    "kpphmi-prod",
                    "kpphmi-staging",
                    "kpwa-prod",
                    "kpwa-staging",
                    "jhah-prod"
                ]
            },
            "queries": {
                "snowflake": {
                    "database": "DAP",
                    "schema": "L2",
                    "query": cleaned_query
                },
                "postgres": {
                    "database": "postgres",
                    "schema": "l2",
                    "query": cleaned_query
                }
            }
        }

        metrics.append(metric_block)

    return {"metrics": metrics}


# =========================================================
# ---------------- APP 2 : ZIP COMPILER --------------------
# =========================================================
mapping = {
    'advantasure-prod': 'Advantasure (Env 1)',
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
    'mercypit-prod': 'Pittsburgh Mercy',
    'mgm-prod': 'Mgm Resorts',
    'mhcn-prod': 'Chi Memorial',
    'nemoursapollo-prod': 'Nemours Childrens Health System',
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
    'smch-prod': 'San Mateo County Health',
    'stewardapollo-prod': 'Steward Health Care System',
    'strivehealth-prod': 'Strive Health',
    'tccn-prod': 'Childrens Healthcare Of Atlanta',
    'thnapollo-prod': 'Cone Health',
    'trinity-prod': 'Trinity Health National',
    'uninet-prod': 'CHI Health Partners',
    'usrc-prod': 'US RenalCare',
    'walgreens-prod': 'Walgreens'
}


def process_zip(uploaded_zip):
    dfs = []

    with zipfile.ZipFile(uploaded_zip) as z:
        for file in z.namelist():
            if file.lower().endswith(".csv"):
                with z.open(file) as f:
                    dfs.append(pd.read_csv(f))

    combined_df = pd.concat(dfs, ignore_index=True)
    metric_cols = combined_df.columns.drop("customer")

    final_df = (
        combined_df
        .groupby("customer", as_index=False)[metric_cols]
        .sum()
    )

    final_df.insert(
        1,
        "Health System Name",
        final_df["customer"].map(mapping).fillna("")
    )

    return final_df


# =========================================================
# -------------------- UI SWITCH --------------------------
# =========================================================
if app_choice == "DER JSON Creator":
    st.header("📌 DER JSON Creator")

    uploaded_files = st.file_uploader(
        "Upload one or multiple `.sql` files",
        type=["sql"],
        accept_multiple_files=True
    )

    if uploaded_files:
        final_json = create_final_json(uploaded_files)

        json_bytes = io.BytesIO()
        json_bytes.write(json.dumps(final_json, indent=4).encode("utf-8"))
        json_bytes.seek(0)

        st.subheader("🔍 JSON Preview")
        st.json(final_json)

        st.download_button(
            label="⬇️ Download JSON",
            data=json_bytes,
            file_name="DER_JSON_FINAL.json",
            mime="application/json"
        )

elif app_choice == "DER ZIP Data Compiler":
    st.header("📦 DER ZIP → Final Aggregated Table")

    uploaded_zip = st.file_uploader(
        "Upload ZIP file containing DER CSVs",
        type=["zip"]
    )

    if uploaded_zip:
        try:
            with st.spinner("Processing ZIP file..."):
                final_df = process_zip(uploaded_zip)

            st.success("Processing complete ✅")

            st.subheader("📊 Preview Result")
            st.dataframe(final_df, use_container_width=True)

            csv_bytes = final_df.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="⬇️ Download Final CSV",
                data=csv_bytes,
                file_name="final.csv",
                mime="text/csv"
            )

        except Exception as e:
            st.error("❌ Error processing ZIP file")
            st.exception(e)
