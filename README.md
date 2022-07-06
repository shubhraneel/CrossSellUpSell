# CrossSellUpSell

This project was done for the Cross-Sell/Upsell task of Maverick 2.0, a data science hackathon organized by AB InBev. It is a python Flask app that recommends the products to Cross-Sell or Upsell to wholesalers and with how much quantity. The backend runs a Machine Learning model based on Neural Collaborative Filtering to predict the Upsell/Cross-Sell product and another Machine Learning model based on LSTM time series prediction to predict the quantity of product to sell. The model uses past sales data for training and is constantly updated as new data is available based on the product and quantity chosen by the user.

## Running Instructions

1. Start virtual environment

   ```bash
   python3 -m venv env
   ```

2. Activate environment

   ```bash
   source env/bin/activate
   ```

   Or

   ```bash
   .\env\Scripts\activate
   ```

3. Install requirements

   ```bash
   pip install -r requirements.txt
   ```

4. Start the server

   ```bash
   python3 app.py
   ```

4. Open [localhost:5000](http://localhost:5000) in a browser

## Local Requirements

* Python 3.8
* pip

## Warnings

If the Flask app does not work, run the notebooks in the folder

Disclaimer: Works with Python 3.8. TensorFlow faces version issue 
when if tried in Python 3.9. Follow the steps in GitHub to run the application.

## HEROKU APP

Heroku App link: https://cross-sell-up-sell.herokuapp.com/

The App deployed on Heroku might not work sometimes due to server issues. 
Launching it after sometime is recommended, it something like that happens. 

Do not try to input anything unusual in the application. It might crash. 
For example, do not try to enter an existing user ID where the new user ID 
has to be entered. This application only provides an user interface, 
which is not the main objective of this task.

If for any reason the application doesn’t run, run the .ipynb Notebooks 
present in the Notebook folder of the GitHub repo. All the recommendations 
(both materials and quantity) are printed in the notebooks.
