from flask import Flask, render_template, redirect, request, url_for
from material_recommender import predict_material
from HLpredictor import predict_HL
from cross_up import cross_up
from model_feedback import model_feedback
import json

app = Flask(__name__)

@app.route('/')
def index():
  wholesalers = json.load(open('data/wudi.json'))
  return render_template('index.html', wholesalers=wholesalers)

@app.route('/recommendations', methods=['POST'])
def recommendations():
  return redirect(url_for("recommendations_wholesaler", wholesaler_id=request.form['wholesaler']))

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
  model_feedback(int(data["wholesaler"]), [int(x) for x in data["cart"].keys()])
  return redirect(url_for('crossup', 
      wholesaler_id=data["wholesaler"],
      cross_sell_dict=cross_sell_dict, 
      cross_sell_discounts=str(cross_sell_discounts),
      upsell_quantities=upsell_quantities,
      upsell_discount=upsell_dis
      ))

@app.route("/crossup/<wholesaler_id>")
def crossup(wholesaler_id):
  return render_template(
    'cross_up.html', 
    wholesaler = wholesaler_id,
    cross_sell_quantities = eval(request.args["cross_sell_dict"]).items(),
    cross_sell_discounts = eval(request.args["cross_sell_discounts"]),
    upsell_quantities = eval(request.args["upsell_quantities"]).items(),
    upsell_discount = float(request.args["upsell_discount"])
    )

@app.route("/order_2", methods=["POST"])
def order_2():
  data = json.loads(request.data)
  model_feedback(int(data["wholesaler"]), [int(x) for x in data["cart"].keys()])
  return redirect(url_for('index'))

if __name__ == '__main__':
  app.run(debug=True)
