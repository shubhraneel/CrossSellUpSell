from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/recommendations/<wholesaler_id>')
def recommendations(wholesaler_id):
  return wholesaler_id

if __name__ == '__main__':
  app.run(debug=True)
