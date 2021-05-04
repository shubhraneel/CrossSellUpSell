from flask import Flask, render_template, redirect, request
from material_recommender import predict_material
from HLpredictor import predict_HL
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
  materials = predict_material(int(wholesaler_id))
  quantities = [round(predict_HL(int(wholesaler_id), int(material_id)), 2) for material_id in materials]
  return render_template(
    'recommendations.html', 
    wholesaler=wholesaler_id, 
    materials_quantities=zip(materials, quantities)
    )

if __name__ == '__main__':
  app.run(debug=True)
