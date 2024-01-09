import mysql.connector
import pandas as pd
import streamlit as st
import altair as alt
from streamlit_option_menu import option_menu

# Funktion zum Verbinden mit der Datenbank und Laden der Daten
def load_data():
    # Verbindung zu Datenbank herstellen
    dataBase = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="Barcelona.00",
        database="watertemperature"
    )

    # SQL-Abfrage ausführen und Ergebnisse in Pandas DataFrame laden
    query = "SELECT * FROM OCEAN2"
    df = pd.read_sql(query, dataBase)

    # Überprüfe, ob die Spalte 'Temperatur' vorhanden ist
    if 'Temperatur' in df.columns:
        # Versuche, die 'Temperatur'-Spalte in numerische Werte zu konvertieren
        try:
            df['Temperatur'] = pd.to_numeric(df['Temperatur'], errors='raise')
        except pd.errors.ParserError:
            st.warning("Fehler beim Konvertieren der 'Temperatur'-Spalte in numerische Werte.")
    else:
        st.warning("Die Spalte 'Temperatur' ist in der Datenbank nicht vorhanden.")

    # Wenn 'Zeit' vorhanden ist, versuchen Sie, es in ein Datetime-Objekt zu konvertieren
    if 'Zeit' in df.columns:
        try:
            df['Zeit'] = pd.to_datetime(df['Zeit'])
        except pd.errors.ParserError:
            st.warning("Fehler beim Konvertieren der 'Zeit'-Spalte in Datetime-Objekte.")

    # Verbindung schließen
    dataBase.close()

    return df

# Funktion zum Erstellen des Temperaturverlaufsdiagramms für jeden Ort
def create_temperature_chart_per_location(df):
    # Erstelle ein Altair-Chart für jeden Ort
    charts = []
    for ort in df['Ort'].unique():
        chart = alt.Chart(df[df['Ort'] == ort]).mark_line().encode(
            x='Datum',
            y='Temperatur',
            tooltip=['Datum', 'Temperatur']
        ).properties(
            title=f'Temperaturverlauf für {ort}'
        )
        charts.append(chart)
    return charts

# Funktion zum Erstellen des Temperaturverlaufsdiagramms
def create_temperature_chart(df):
    # Gruppiere Daten nach Ortschaft und berechne den Durchschnitt der Temperatur
    grouped_df = df.groupby('Ort')['Temperatur'].mean().reset_index()

    # Erstelle ein Altair-Chart
    chart = alt.Chart(grouped_df).mark_bar().encode(
        x='Ort',
        y='Temperatur',
        tooltip=['Ort', 'Temperatur']
    ).properties(
        title='Durchschnittliche Temperatur pro Ort'
    )

    return chart

# Navigationsbar
selected = option_menu(
    menu_title="Watertemperature",
    options=["Tabellenübersicht", "Maps", "Temperaturverlauf", "Durchschnittstemp"],
    icons=["1-circle", "2-circle", "3-circle", "4-circle"],
    menu_icon="book",
    default_index=0,
    orientation="horizontal",
)

# Hauptfunktion
def main():
    # Titel der App
    st.title("Ocean")

    if selected == "Tabellenübersicht":
        # Lade Daten beim Start der App
        df = load_data()
        st.write('Werte:')
        st.dataframe(df)

    elif selected == "Maps":
        # Lade Daten beim Wechsel zur Maps-Ansicht
        df = load_data()

        # Überprüfe, ob die erforderlichen Spalten in der Datenbank vorhanden sind
        if 'Breitengrad' in df.columns and 'Laengengrad' in df.columns:
            st.write('Standorte:')
            # Konvertiere 'Breitengrad' and 'Laengengrad' als nummerisch
            coordinates = pd.DataFrame({
                'lat': -pd.to_numeric(df['Breitengrad'], errors='coerce'),
                'lon': -pd.to_numeric(df['Laengengrad'], errors='coerce'),
            })
            st.map(coordinates)
        else:
            st.warning("Die Spalten 'Breitengrad' und 'Laengengrad' sind in der Datenbank nicht vorhanden.")

    elif selected == "Temperaturverlauf":
        # Lade Daten beim Wechsel zur Temperaturverlauf-Ansicht
        df = load_data()
        
        # Überprüfe, ob die erforderlichen Spalten in der Datenbank vorhanden sind
        if 'Ort' in df.columns and 'Temperatur' in df.columns and 'Datum' in df.columns:
            st.write("Temperaturverlauf:")
            temperature_charts = create_temperature_chart_per_location(df)
            for chart in temperature_charts:
                st.altair_chart(chart, use_container_width=True)
        else:
            st.warning("Die Spalten 'Ort', 'Temperatur' oder 'Datum' sind in der Datenbank nicht vorhanden.")

    elif selected == "Durchschnittstemp":
        # Lade Daten beim Wechsel zur Temperaturverlauf-Ansicht
        df = load_data()
        
        # Überprüfe, ob die erforderlichen Spalten in der Datenbank vorhanden sind
        if 'Ort' in df.columns and 'Temperatur' in df.columns:
            st.write("Temperaturverlauf:")
            temperature_chart = create_temperature_chart(df)
            st.altair_chart(temperature_chart, use_container_width=True)
        else:
            st.warning("Die Spalten 'Ort' und 'Temperatur' sind in der Datenbank nicht vorhanden.")

if __name__ == "__main__":
    main()