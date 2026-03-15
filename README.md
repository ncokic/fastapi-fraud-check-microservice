## FastAPI Fraud Check Microservice

A machine learning microservice built to detect fraudulent transactions. Created to work in conjuction with my flask e-commerce API project found [here.](https://github.com/ncokic/flask-ecommerce-api) <br>
The model was trained using the Kaggle Credit Card Fraud Detection dataset which is not included in the repo due to file size limits. You can download the raw CSV file [here.](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud)

### Current Status
- [X] Model Training (Random Forest)
- [X] Architecture (FastAPI + Lifespan model loading)
- [ ] Flask Integration (Pending)

### Installation Instructions

```bash
git clone https://github.com/ncokic/fastapi-fraud-check-microservice.git
cd fastapi-fraud-check-microservice
python -m pip install -r requirements.txt
fastapi dev app/main.py
```
Docs are redirected to the home page where you can test the Fraud Detection endpoint.

