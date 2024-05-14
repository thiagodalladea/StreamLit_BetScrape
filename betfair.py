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


def format_betfair(df):
    df = df.dropna(subset="aa_innerText").aa_innerText.apply(
        lambda x: pd.Series(
            [q for q in re.split(r"[\n]", x) if not re.match("SUSPENSO", q)]
        )
    )
    df_teams = df.iloc[:, [6, 7]]
    df_odds = df.iloc[:, [3, 4, 5]]
    df = pd.concat([df_teams, df_odds.reset_index(drop=True)], axis=1)
    df = (
        df[[6, 7, 3, 4, 5]]
        .rename(
            columns={
                6: "betfair_name1",
                7: "betfair_name2",
                3: "betfair_odd1",
                4: "betfair_odd2",
                5: "betfair_odd3",
            }
        )
        .dropna()
        .assign(
            betfair_odd1=lambda q: q.betfair_odd1.str.replace(",", "."),
            betfair_odd2=lambda q: q.betfair_odd2.str.replace(",", "."),
            betfair_odd3=lambda q: q.betfair_odd3.str.replace(",", "."),
        )
        .astype(
            {
                "betfair_odd1": "Float64",
                "betfair_odd2": "Float64",
                "betfair_odd3": "Float64",
            }
        )
    )
    st.write("\nBETFAIR ODDS DATA REQUESTED SUCCESSFULLY!\n")

    return df.sort_values(by=["betfair_name1", "betfair_name2"]).reset_index(drop=True)


st.write("""
    # Betfair
""")

url = st.text_input("Betfair URL")

if not url:
    st.write("No URL was provided")
else:
    try:
        driver = Driver(uc=True)
        driver.get(url)
        df = get_dataframe(driver, query="li.com-coupon-line-new-layout")
        df = format_betfair(df)
        driver.quit()
        st.write(
            df.sort_values(by=["betfair_name1", "betfair_name2"]).reset_index(drop=True)
        )
    except Exception as exception:
        st.write(exception)
        driver.quit()
