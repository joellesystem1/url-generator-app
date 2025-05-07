from flask import Flask, render_template, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_excel', methods=['POST'])
def upload_excel():
    file = request.files['file']
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        df = pd.read_excel(filepath, skiprows=[0])
        revenue_cols = df.columns[1:8]
        rpc_cols = df.columns[8:15]
        clicks_cols = df.columns[15:22]

        def clean_numeric(df, cols):
            data = df[cols].copy().astype(str)
            data = data.replace({
                r'[\$,]': '',
                r'^\s*$': '0',
                'nan': '0',
                '#N/A': '0',
                'None': '0',
                '-': '0'
            }, regex=True)
            return data.apply(pd.to_numeric, errors='coerce').fillna(0)

        revenue_data = clean_numeric(df, revenue_cols)
        rpc_data = clean_numeric(df, rpc_cols)
        clicks_data = clean_numeric(df, clicks_cols)
        queries = df.iloc[:, 0].fillna('').astype(str).str.strip()
        metrics_df = pd.DataFrame({
            'query': queries,
            'avg_revenue': revenue_data.mean(axis=1).round(2),
            'total_revenue': revenue_data.sum(axis=1).round(2),
            'avg_rpc': rpc_data.mean(axis=1).round(2),
            'total_rpc': rpc_data.sum(axis=1).round(2),
            'avg_clicks': clicks_data.mean(axis=1).round(0),
            'total_clicks': clicks_data.sum(axis=1).round(0)
        })
        invalid_queries = ['query', 'total', 'grand total', 'nan', '#n/a', '', ' ']
        metrics_df = metrics_df[~metrics_df['query'].str.lower().isin(invalid_queries)]
        keywords = metrics_df.to_dict(orient='records')
        return jsonify({'keywords': keywords})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
