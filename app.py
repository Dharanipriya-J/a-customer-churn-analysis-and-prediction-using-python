from flask import Flask, request, jsonify, render_template
import pickle
import pandas as pd
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER='uploads'
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

model=pickle.load(open('model.pkl','rb'))

def get_risk(prob):

    if prob>0.7:
        return "HIGH"

    elif prob>=0.4:
        return "MEDIUM"

    else:
        return "LOW"


def get_suggestion(risk):

    if risk=="HIGH":
        return "Provide discount offer"

    elif risk=="MEDIUM":
        return "Customer follow-up"

    else:
        return "Offer loyalty benefits"


@app.route('/')
def home():

    return render_template("index.html")


# MANUAL PREDICTION

@app.route('/api/predict',methods=['POST'])

def predict():

    data=request.json

    gender=1 if data['gender']=="Male" else 0

    pay_map={
    "Credit Card":0,
    "Debit Card":1,
    "UPI":2,
    "Net Banking":3
    }

    payment=pay_map[data['payment_method']]

    features=[[
    gender,
    int(data['tenure']),
    float(data['monthly']),
    float(data['total']),
    payment
    ]]

    pred=model.predict(features)[0]

    prob=model.predict_proba(features)[0][1]

    risk=get_risk(prob)

    suggestion=get_suggestion(risk)

    return jsonify({

    "churn":"YES" if pred==1 else "NO",

    "risk_level":risk,

    "suggestion":suggestion

    })


# CSV UPLOAD

@app.route('/api/upload',methods=['POST'])

def upload():

    if 'file' not in request.files:

        return jsonify({"error":"No file"})

    file=request.files['file']

    if file.filename=='':    

        return jsonify({"error":"Empty file"})

    path=os.path.join(

    app.config['UPLOAD_FOLDER'],

    secure_filename(file.filename)

    )

    file.save(path)

    data=pd.read_csv(path)

    if 'customer_id' not in data.columns:

        data['customer_id']=range(1,len(data)+1)

    data['tenure']=pd.to_numeric(
    data['tenure'],errors='coerce')

    data['monthly']=pd.to_numeric(
    data['monthly'],errors='coerce')

    data['total']=pd.to_numeric(
    data['total'],errors='coerce')

    data['gender_num']=data['gender'].apply(

    lambda x:1 if str(x)=="Male" else 0

    )

    pay_map={

    "Credit Card":0,

    "Debit Card":1,

    "UPI":2,

    "Net Banking":3

    }

    data['payment_num']=data[
    'payment_method'
    ].map(pay_map)

    data['payment_num']=data[
    'payment_num'
    ].fillna(0)

    X=data[[

    'gender_num',

    'tenure',

    'monthly',

    'total',

    'payment_num'

    ]]

    pred=model.predict(X)

    prob=model.predict_proba(X)[:,1]

    data['churn']=[

    "YES" if i==1 else "NO"

    for i in pred

    ]

    data['risk']=[

    get_risk(p)

    for p in prob

    ]

    data['suggestion']=[

    get_suggestion(r)

    for r in data['risk']

    ]

    result=data[[

    'customer_id',

    'tenure',

    'monthly',

    'total',

    'churn',

    'risk',

    'suggestion'

    ]]

    return jsonify({

    "results":

    result.to_dict(

    orient='records'

    )

    })


# ANALYTICS ROUTE (FIXED)

@app.route('/api/analytics')

def analytics():

    df=pd.read_csv("dataset.csv")

    df['churn']=df['churn'].astype(int)

    churn_yes=int(df['churn'].sum())

    churn_no=len(df)-churn_yes

    churned=df[df['churn']==1]['monthly'].mean()

    not_churn=df[df['churn']==0]['monthly'].mean()

    return jsonify({

    "churn_distribution":{

    "yes":churn_yes,

    "no":churn_no

    },

    "monthly_comparison":{

    "churned":float(churned),

    "not_churned":float(not_churn)

    }

    })


if __name__=="__main__":

    app.run(debug=True)