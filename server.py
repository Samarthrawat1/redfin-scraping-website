from flask import Flask, render_template, jsonify, request, send_file
import time
import csv
import os
from scrape import scrape_redfin_data
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import pandas as pd
import io

app = Flask(__name__)

CSV_FILE = 'redfin_data.csv'

def load_recent_data(limit=10):
    try:
        with open(CSV_FILE, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            return list(reader)[-limit:][::-1]  # Reverse for newest on top
    except FileNotFoundError:
        return []


@app.route('/')
def index():
    initial_data = load_recent_data()
    return render_template('index.html', initial_data=initial_data)


@app.route('/fetch_data', methods=['POST'])
def fetch_data():
    try:
        request_data = request.get_json()
        url = request_data['url']  # Corrected URL retrieval
        data = scrape_redfin_data(url)
        time.sleep(5)

        if data:
            data = {'URL': url, **data}  # More concise way to add URL
            # Check if the CSV file is empty or doesn't exist
            file_is_empty = not os.path.isfile(CSV_FILE) or os.stat(CSV_FILE).st_size == 0

            with open(CSV_FILE, 'a', newline='') as csvfile:
                fieldnames = list(data.keys())  # Get headers from the first data row
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                if file_is_empty:
                    writer.writeheader()
                writer.writerow(data)

            return jsonify({'data': data})
        else:
            return jsonify({'error': 'Failed to fetch data from Redfin'}), 500

    except Exception as e:
        app.logger.error(f"Error fetching data: {e}")  # Log the error
        return jsonify({'error': 'An error occurred while fetching data'}), 500

@app.route('/download_excel')
def download_excel():
    try:
        df = pd.read_csv(CSV_FILE)
        print(df)

        # Create an in-memory Excel file
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Redfin Data', index=False)

        output.seek(0)

        # Send the Excel file to the user
        return send_file(
            output,
            as_attachment=True,
            download_name='redfin_data.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        app.logger.error(f"Error downloading excel: {e}")
        return jsonify({'error': 'An error occurred while downloading Excel'}), 500



if __name__ == '__main__':
    app.run(debug=True)