#utils/model_loader.py
import joblib
import pandas as pd
import streamlit as st
from config import ADMET_INFO, EXCLUDE_COLS

@st.cache_resource
def load_models():

    model_activity = joblib.load("models/model_activity.pkl")
    models_admet = {t: joblib.load(f"models/model_{t}.pkl") for t in ADMET_INFO.keys()}
    return model_activity, models_admet

@st.cache_data
def load_data():

    df_train = pd.read_csv("data/merged_data.csv")
    desc_cols = [c for c in df_train.columns if c not in EXCLUDE_COLS]
    return desc_cols