import joblib
import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


df = pd.read_csv("../data/creditcard.csv")
training_df = pd.DataFrame()
training_df["order_amount"] = df.Amount

np.random.seed(42)
is_fraud = df.Class == 1

training_df["orders_last_24h"] = np.where(
    is_fraud,
    np.random.poisson(lam=8, size=len(df)),
    np.random.poisson(lam=1.2, size=len(df)),
)
training_df.orders_last_24h = training_df.orders_last_24h.clip(0, 20)

training_df["address_mismatch"] = np.where(
    is_fraud,
    np.random.choice([0, 1], size=len(df), p=[0.6, 0.4]),
    np.random.choice([0, 1], size=len(df), p=[0.85, 0.15]),
)

training_df["country_mismatch"] = np.where(
    is_fraud,
    np.random.choice([0, 1], size=len(df), p=[0.3, 0.7]),
    np.random.choice([0, 1], size=len(df), p=[0.99, 0.01]),
)

training_df["account_age_min"] = np.where(
    is_fraud,
    np.where(
        np.random.rand(len(df)) < 0.9,
        np.random.randint(1, 1440, size=len(df)),
        np.random.randint(1440, 10000, size=len(df)),
    ),
    np.where(
        np.random.rand(len(df)) < 0.2,
        np.random.randint(1, 1440, size=len(df)),
        np.random.randint(1440, 525600, size=len(df)),
    ),
)

training_df["new_account"] = (training_df.account_age_min < 1440).astype(int)
training_df["high_velocity"] = (training_df.orders_last_24h > 3).astype(int)
training_df["diff_country_new_acc"] = (training_df.country_mismatch * training_df.new_account)
training_df["diff_country_high_vel"] = (training_df.country_mismatch * training_df.high_velocity)

X = training_df
y = df.Class

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)

sm = SMOTE(random_state=42, sampling_strategy=0.1)
X_train_res, y_train_res = sm.fit_resample(X_train_scaled, y_train)

model = RandomForestClassifier(n_estimators=100, n_jobs=-1, random_state=42)
model.fit(X_train_res, y_train_res)

joblib.dump(model, "../app/ml_models/fraud_check_model/fraud_model.joblib")
joblib.dump(scaler, "../app/ml_models/fraud_check_model/scaler.joblib")