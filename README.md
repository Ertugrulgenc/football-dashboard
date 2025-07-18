Interactive Football (Soccer) Game Events Dashboard
This Streamlit application provides an interactive dashboard to visualize and analyze football (soccer) game events and match statistics. It leverages data from game_events.csv and games.csv to offer insights into event distribution, goal trends, and more.

Features
Event Distribution Histogram: Visualize the frequency of selected event types (e.g., Goals, Fouls) across game minutes, including extra time (up to 95 minutes).

Event Frequency Heatmap: A heatmap showing the concentration of all event types across different 5-minute intervals of the game, excluding shootout events.

Average Goals per Matchday: A line chart displaying the average goals scored per matchday for selected top European leagues (France, Great Britain, Turkey, Italy, Netherlands, Spain), allowing multi-selection and filtering for the last 10 years.

Data Sources
The application uses two CSV files: game_events.csv and games.csv. These files are hosted on Google Drive. The application attempts to download them directly.

game_events.csv:

File ID: 11L7_jJ_6rU3D43vsd4IQVqY3_BB_l9-H

Direct Download URL: https://drive.usercontent.google.com/download?id=11L7_jJ_6rU3D43vsd4IQVqY3_BB_l9-H&export=download&confirm=t

games.csv:

File ID: 1Z42XEB60ogr280R3FrhvIvqgWaoP81JO

Direct Download URL: https://drive.google.com/uc?export=download&id=1Z42XEB60ogr280R3FrhvIvqgWaoP81JO&confirm=t

Important Notes for Google Drive Links:

The &confirm=t parameter is added to bypass Google Drive's virus scan warning for large files. If you encounter issues, verify the file IDs and sharing settings.

How to Run
Save the Python code: Save the provided Python code (from the "Interactive Game Events Dashboard" Canvas) as app.py in a directory on your computer.

Save requirements.txt: Save the content of the requirements.txt immersive into a file named requirements.txt in the same directory as app.py.

Create a virtual environment (recommended):

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

Run the Streamlit application:

streamlit run app.py

This will open the dashboard in your web browser.

Development
Feel free to explore the appgithub2.py file to understand the data loading, processing, and visualization logic. 
Enjoy!
