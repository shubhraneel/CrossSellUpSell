from flask import Flask, render_template, redirect, request
from material_recommender import predict
import json

app = Flask(__name__)

@app.route('/')
def index():
  materials = json.load(open('data/wudi.json'))
  return render_template('index.html', materials=materials)

@app.route('/recommendations', methods=['POST'])
def recommendations():
  return redirect(f"/recommendations/{request.form['wholesaler']}")

@app.route('/recommendations/<wholesaler_id>')
def recommendations_wholesaler(wholesaler_id):
  return str(predict(int(wholesaler_id)))

if __name__ == '__main__':
  app.run(debug=True)
