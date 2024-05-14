import streamlit as st
import re
import pandas as pd
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from a_selenium2df import get_df


def get_dataframe(driver, query="*"):
    df = pd.DataFrame()
    while df.empty:
        df = get_df(
            driver,
            By,
            WebDriverWait,
            expected_conditions,
            queryselector=query,
            with_methods=True,
        )

    return df.reset_index(drop=True)


def format_betano(df):
    df = (
        df.dropna(subset="aa_innerText")
        .aa_innerText.apply(
            lambda x: pd.Series(
                [
                    q
                    for q in re.split(r"[\n]", x)
                    if not re.match(r"\b\d{2}/\d{2}\b", q)
                    if not re.match(r"\d{2}:\d{2}\b", q)
                    if not re.match(r".*Primeiro jogo.*", q)
                    if not re.match("AO VIVO", q)
                    if not re.match("SO", q)
                    if not re.match(r"^\d+$", q)
                ]
            )
        )[[0, 1, 2, 4, 5]]
        .rename(
            columns={
                0: "betano_name1",
                1: "betano_name2",
                2: "betano_odd1",
                4: "betano_odd2",
                5: "betano_odd3",
            }
        )
        .dropna()
        .assign(
            betano_odd1=lambda q: q.betano_odd1.str.replace(",", "."),
            betano_odd2=lambda q: q.betano_odd2.str.replace(",", "."),
            betano_odd3=lambda q: q.betano_odd3.str.replace(",", "."),
        )
        .astype(
            {
                "betano_odd1": "Float64",
                "betano_odd2": "Float64",
                "betano_odd3": "Float64",
            }
        )
    )
    st.write("\nBETANO DATA REQUESTED SUCCESSFULLY!\n")

    return df.sort_values(by=["betano_name1", "betano_name2"]).reset_index(drop=True)


st.write("""
    # Betano
""")

url = st.text_input("Betano URL")

if not url:
    st.write("No URL was provided")
else:
    try:
        driver = Driver(uc=True)
        driver.get(url)
        df = get_dataframe(driver, query="div.vue-recycle-scroller__item-view")
        df = format_betano(df)
        driver.quit()
        st.write(
            df.sort_values(by=["betano_name1", "betano_name2"]).reset_index(drop=True)
        )
    except Exception as exception:
        st.write(exception)
        driver.quit()
