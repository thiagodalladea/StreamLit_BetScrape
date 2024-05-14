import streamlit as st
import re
import pandas as pd
import numpy as np
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from a_selenium2df import get_df
from st_pages import Page, show_pages


show_pages(
    [
        Page("bet365.py", "Bet365"),
        Page("betfair.py", "Betfair"),
        Page("sportingbet.py", "Sporting Bet"),
        Page("betano.py", "Betano"),
    ]
)


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


def format_bet365_teams(df):
    df = (
        df.dropna(subset="aa_innerText")
        .aa_innerText.apply(
            lambda x: pd.Series(
                [q for q in re.split(r"[\n]", x) if not re.match(r"\d{2}:\d{2}\b", q)]
            )
        )[[0, 1]]
        .rename(
            columns={
                0: "bet365_name1",
                1: "bet365_name2",
            }
        )
        .dropna()
    )
    st.write("\nBET 365 TEAMS DATA REQUESTED SUCCESSFULLY!\n")

    return df.reset_index(drop=True)


def format_bet365_odds(df):
    df = df.dropna(subset="aa_innerText")
    df = df[["aa_innerText"]]
    df_parts_odds = np.array_split(df, 3)
    df_part_1 = df_parts_odds[0]
    df_part_2 = df_parts_odds[1]
    df_part_3 = df_parts_odds[2]
    df_part_1 = df_part_1.rename(columns={"aa_innerText": "bet365_odd1"})
    df_part_2 = df_part_2.rename(columns={"aa_innerText": "bet365_odd2"})
    df_part_3 = df_part_3.rename(columns={"aa_innerText": "bet365_odd3"})
    df_odds = pd.concat([df_part_1, df_part_2.reset_index(drop=True)], axis=1)
    df_odds = pd.concat([df_odds, df_part_3.reset_index(drop=True)], axis=1)
    st.write("\nBET365 ODDS DATA REQUESTED SUCCESSFULLY!\n")

    return df_odds.reset_index(drop=True)


st.write("""
    # Bet365
""")

url = st.text_input("Bet365 URL")

if not url:
    st.write("No URL was provided")
else:
    try:
        query = [
            "div.rcl-ParticipantFixtureDetails_TeamNames",
            "span.sgl-ParticipantOddsOnly80_Odds",
        ]
        driver = Driver(uc=True)
        driver.get(url)
        dfs = []
        for part_query in query:
            df = pd.DataFrame()
            while df.empty:
                df = get_df(
                    driver,
                    By,
                    WebDriverWait,
                    expected_conditions,
                    queryselector=part_query,
                    with_methods=True,
                )
            dfs.append(df)
        df_teams = format_bet365_teams(dfs[0])
        df_odds = format_bet365_odds(dfs[1])
        df = pd.concat([df_teams, df_odds.reset_index(drop=True)], axis=1)
        df = df.sort_values(by=["bet365_name1", "bet365_name2"])
        st.write(
            df.sort_values(by=["bet365_name1", "bet365_name2"]).reset_index(drop=True)
        )
    except Exception as exception:
        st.write(exception)
        driver.quit()
