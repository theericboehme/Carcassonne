import streamlit as st
import numpy as np
from PIL import Image
import pandas as pd
from io import BytesIO
import xlsxwriter
from datetime import date

# site setup
st.set_page_config(layout="wide", page_title='Carcassonne')
st.title("Carcassonne Analytics")
st.write("v1.0")
st.caption("by Eric Waste-of-Time Ventures")

# dictionary of all items
items = {
    "burg": 0,
    "wappen": 0,
    "waren": 0,
    "kathedrale": 0,
    "weg": 0,
    "wirtshaus": 0,
    "kloster": 0,
    "beet": 0
}

dependencies = {
    "wappen": "burg",
    "waren": "burg",
    "kathedrale": "burg", 
    "wirtshaus": "weg"
}

PATH_PICTURES = "Bilder/"

# load all images

images = {}
for picture in items.keys():
    images[picture] = Image.open(PATH_PICTURES + f"{picture}.png")

if 'Round' not in st.session_state:
    st.session_state['Round'] = 1

if 'Setup' not in st.session_state:
    st.session_state['Setup'] = True
# if st.session_state['Round'] > 1:
#     st.session_state['Setup'] = False

if 'alreadyPlayed' not in st.session_state:
    st.session_state['alreadyPlayed'] = []

# game preparations

if 'ongoingGame' not in st.session_state:
    st.session_state['ongoingGame'] = False

with st.expander("Game setup", expanded = st.session_state['Setup']):

    col1, col2, col3 = st.columns(3)
    numberPlayers = col1.number_input("Select the number of players: ", min_value=1, max_value=8, value=2)
    player_list = list(np.arange(1, numberPlayers + 1))

    if 'Players' not in st.session_state:
        st.session_state['Players'] = {}

    if 'Totals' not in st.session_state:
        st.session_state['Total'] = {}

    for number in range(1, numberPlayers + 1):
        st.session_state['Players'][number] = {}
        col1, col2, col3 = st.columns(3)

        # add name
        st.session_state['Players'][number]["name"] = col1.text_input("Enter player name", key = number)

        # add color picker
        color_list = ["#DE2020", "#3CAF19", "#3B4DB5", "#FBEE07", "#FB9D00", "#6D1983", "#FFFFFF", "#000000"]
        st.session_state['Players'][number]["color"] = col2.color_picker("Choose color", value = color_list[number-1])

    if 'RoundStatistics' not in st.session_state:
        st.session_state['RoundStatistics'] = {}

    # initiate the dictionary in the first round
    if st.session_state["Round"] == 1:
        for number in range(1, numberPlayers + 1):
            # add list with each round later
            st.session_state['RoundStatistics'][number] = {}

    def function_number_to_name(number):
        return st.session_state['Players'][number]["name"]

    # determine the starter of the game
    st.session_state['starter'] = st.selectbox("Who starts the game?", options = player_list, format_func=function_number_to_name)

    if 'disableInput' not in st.session_state:
        st.session_state['disableInput'] = False

    def disable_input():
        st.session_state['disableInput'] = False
        st.session_state['Setup'] = False
        st.session_state['ongoingGame'] = True
        return

    if st.button("Start Game", on_click = disable_input):
        st.write("Game has started")

    for number in st.session_state['Players'].keys():
        if number == st.session_state['starter']:
            st.session_state['Players'][number]["starter"] = 1
        else:
            st.session_state['Players'][number]["starter"] = 0

    if 'Next' not in st.session_state:
        st.session_state['Next'] = 'False'

    if 'Round' not in st.session_state:
        st.session_state['Round'] = 1


# each turn ----------------------------------------------------------------------

# Callback function if it's the next player's turn
def next_player():
    try:
        current_player_index = player_list.index(st.session_state['currentPlayer'])
    except:
        current_player_index = player_list.index(st.session_state['starter'])

    try:
        nextPlayer = player_list[current_player_index + 1]
    except:
        nextPlayer = player_list[0]
    
    st.session_state['previousPlayer'] = player_list[current_player_index]
    st.session_state['currentPlayer'] = nextPlayer
    
    #st.session_state['showStatistics'] = False

    # collect players that have already played (to make statistics available once everyone has played)
    if st.session_state['previousPlayer'] not in st.session_state['alreadyPlayed']:
        st.session_state['alreadyPlayed'].append(st.session_state['previousPlayer'])

    # increment round
    st.session_state['Round'] += 1
    
    return

# Callback function if it is the same player again
def same_player():
    try:
        st.session_state['currentPlayer'] = st.session_state['currentPlayer']
    except:
        st.session_state['currentPlayer'] = st.session_state['starter']

    st.session_state['previousPlayer'] = st.session_state['currentPlayer']
    #st.session_state['showStatistics'] = False

    # collect players that have already played (to make statistics available once everyone has played)
    if st.session_state['previousPlayer'] not in st.session_state['alreadyPlayed']:
        st.session_state['alreadyPlayed'].append(st.session_state['previousPlayer'])

    # increment round
    st.session_state['Round'] += 1

    return

if 'showStatistics' not in st.session_state:
    st.session_state['showStatistics'] = False

def finishGame():
    st.session_state["ongoingGame"] = False
    st.session_state["showStatistics"] = True
    return

with st.expander("Ongoing Game", expanded = st.session_state['ongoingGame']):
    with st.form("CurrentTurn", clear_on_submit = True):

        try:
            currentPlayer = st.session_state['currentPlayer']
        except:
            currentPlayer = st.session_state['starter']

        # change color
        current_color = st.session_state['Players'][currentPlayer]['color']

        html_design1 = f'<div style="height:30px;width:100%;background-color:{current_color}"></div>'
        st.markdown(html_design1, unsafe_allow_html=True)

        st.write("")
        st.write(f"It is **{function_number_to_name(currentPlayer)}'s** turn! (Round {st.session_state['Round']})")

        col1, col2, col3, col4, col5 = st.columns(5)

        # field to select card

        # copy dictionary for items to fill for current round and player
        temp_items = dict(items) 
        
        ## row1

        col1.image(images["burg"])
        temp_items["burg"] = col1.checkbox("Burg", disabled = st.session_state['showStatistics'])

        col2.image(images["wappen"])
        temp_items["wappen"] = col2.checkbox("Burg mit Wappen", disabled = st.session_state['showStatistics'])

        col3.image(images["waren"])
        temp_items["waren"] = col3.checkbox("Burg mit Waren", disabled = st.session_state['showStatistics'])

        col4.image(images["kathedrale"])
        temp_items["kathedrale"] = col4.checkbox("Burg mit Kathedrale", disabled = st.session_state['showStatistics'])

        st.write("")

        ## row2
        col1.image(images["weg"])
        temp_items["weg"] = col1.checkbox("Weg", disabled = st.session_state['showStatistics'])

        col2.image(images["wirtshaus"])
        temp_items["wirtshaus"] = col2.checkbox("Weg mit Wirtshaus", disabled = st.session_state['showStatistics'])

        col3.image(images["kloster"])
        temp_items["kloster"] = col3.checkbox("Kloster", disabled = st.session_state['showStatistics'])

        col4.image(images["beet"])
        temp_items["beet"] = col4.checkbox("Beet", disabled = st.session_state['showStatistics'])

        html_design2 = f'<div style="height:5px;width:100%;background-color:{current_color}"></div>'
        st.markdown(html_design2, unsafe_allow_html=True)
        st.write("")

        col1, col2, col3, col4, col5 = st.columns(5)

        if set(player_list) == set(st.session_state["alreadyPlayed"]):
            PauseGame = col1.form_submit_button("Pause/End Game", on_click = finishGame) 
        else:
            col1.write("Statistics become available after everyone has played at least once")

        PlayAgain = col4.form_submit_button("Play again", on_click = same_player) 
        NextTurn = col5.form_submit_button("Next player", on_click = next_player)

    if PlayAgain:
        st.session_state['Next'] = False
        
    elif NextTurn:
        st.session_state['Next'] = True

    if PlayAgain or NextTurn:

        # make sure that dependencies are considered
        for item in dependencies.keys():
            if temp_items[item] == 1:
                temp_items[dependencies[item]] = True

        # add to totals
        # for item in temp_items.keys():
        #     # add each item to the player's total
        #     # previous player is used because the callback function already changes to the next player
        #     st.session_state['Players'][st.session_state['previousPlayer']]["total"][item] += temp_items[item]

        # add to individual round
        # dict - player - round - {}
        st.session_state['RoundStatistics'][st.session_state['previousPlayer']][st.session_state['Round'] - 1] = temp_items

# create data frames

if st.session_state['showStatistics'] == True:

    for player in st.session_state['RoundStatistics'].keys():
        st.session_state['Total'][player] = dict(pd.DataFrame(st.session_state['RoundStatistics'][player]).sum(axis = 1))

    #st.write(st.session_state['Total'])

    # create tabs: Total + One for each player
    #ntabs = len(player_list) + 1
    player_names = []
    for player in player_list:
        player_names.append(str(function_number_to_name(player)))

    list_tabs = ["Overall"] + player_names
    tabs = st.tabs(list_tabs)

    # create statistics overview + individual

    with tabs[0]:

        # overall
        # individual items
        list_items = list(items.keys())

        # raw df
        df_results = pd.DataFrame(index = list_items, columns = list_tabs)

        # add player results to table
        for player in player_list:
            df_results[function_number_to_name(player)] = pd.DataFrame.from_dict(st.session_state['Total'][player], orient = "index") \
                .rename(columns = {0:function_number_to_name(player)}).fillna(0).astype(int)

        # create sum column
        df_results["Overall"] = df_results.sum(axis = 1).astype(int)

        # index in title format
        df_results.index = [x.title() for x in df_results.index]

        overall_table_format = st.radio("Format", options = ["1", "%"], index = 1, horizontal=True)

        if overall_table_format == "1":
            st.dataframe(df_results)

        elif overall_table_format == "%":

            # table with percentages
            df_results_percentage = df_results[:]

            for column in player_names:
                df_results_percentage[column] = (df_results_percentage[column] / df_results_percentage["Overall"] * 100) \
                .fillna(0) \
                .astype(int) \
                .astype(str) \
                + "%"


            st.dataframe(df_results_percentage)

    # for each player, show round statistics in individual tab
    for player_number in player_list:
        with tabs[player_number]:
            df_temp_rounds = pd.DataFrame(st.session_state['RoundStatistics'][player_number])
            df_temp_rounds.index = [x.title() for x in df_temp_rounds.index]
            st.write(df_temp_rounds)

    col1, col2, col3, col4, col5 = st.columns(5)

    # end or resume game
    def resume_game():
        st.session_state['showStatistics'] = False
        st.session_state['ongoingGame'] = True
        return

    col5.button("Resume Game", on_click = resume_game)
    
    if col5.button("End Game", on_click= finishGame):

        def to_excel(df):
            output = BytesIO()
            writer = pd.ExcelWriter(output, engine='xlsxwriter')
            df.to_excel(writer, index=False, sheet_name='Results')
            #workbook = writer.book
            #worksheet = writer.sheets['Sheet1']
            #format1 = workbook.add_format({'num_format': '0.00'}) 
            #worksheet.set_column('A:A', None, format1)  
            writer.save()
            processed_data = output.getvalue()
            
            return processed_data

        df_xlsx = to_excel(df_results)
        st.download_button(label='Download Results',
                                        data=df_xlsx ,
                                        file_name= f'{date.today()}_CarcassonneResults.xlsx')


    # button to clear everything and restart
    def confirmed_reset():
        for key in st.session_state.keys():
            del st.session_state[key]

        return

    if col1.button("Reset"):
        col1.warning("This will delete all data!\nPlease confirm below.")
        col1.button("Confirm Reset", on_click = confirmed_reset)
