from flask import Flask, render_template, redirect, request
from material_recommender import predict_material
from HLpredictor import predict_HL
from cross_up import cross_up
import json

app = Flask(__name__)

@app.route('/')
def index():
  wholesalers = json.load(open('data/wudi.json'))
  return render_template('index.html', wholesalers=wholesalers)

@app.route('/recommendations', methods=['POST'])
def recommendations():
  return redirect(f"/recommendations/{request.form['wholesaler']}")

@app.route('/recommendations/<wholesaler_id>')
def recommendations_wholesaler(wholesaler_id):
  materials, preds = predict_material(int(wholesaler_id))
  quantities = [round(predict_HL(int(wholesaler_id), int(material_id)), 2) for material_id in materials]
  all_materials = json.load(open('data/mudi.json'))
  return render_template(
    'recommendations.html', 
    wholesaler=wholesaler_id, 
    materials_quantities=zip(materials, quantities),
    all_materials=all_materials,
    preds=json.dumps(preds),
    material_pred_dict=json.dumps(dict(zip(materials, quantities)))
    )

@app.route('/order', methods=['POST'])
def order_materials():
  data = json.loads(request.data)
  cross_sell_dict, cross_sell_discounts, upsell_quantities, upsell_dis = cross_up(
    {key: float(value) for key, value in data["cart"].items()}, json.loads(data["preds"]), json.loads(data["material_pred_dict"])
    )
  print(f"Cross sell dict: {cross_sell_dict}")
  print(f"Cross sell discounts: {cross_sell_discounts}")
  print(f"Upsell quant: {upsell_quantities}")
  print(f"Upsell disc: {upsell_dis}")

if __name__ == '__main__':
  app.run(debug=True)
