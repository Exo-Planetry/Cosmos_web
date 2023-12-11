from pymongo import MongoClient


client = MongoClient('mongodb://localhost:27017/')
db = client['ExoplanetData']  
collection = db['Exoplanet'] 


def insert_form_data(pl_orbper, pl_rade, pl_orbeccen, pl_orbincl, pl_tranmid, pl_imppar, pl_trandep, pl_trandur, pl_ratdor, pl_ratror, sy_vmag, sy_kmag):
    # Perform calculations or processing to determine ttv_flag
    # For simplicity, let's assume ttv_flag is calculated as the sum of pl_orbper and pl_rade
    ttv_flag = float(pl_orbper) + float(pl_rade)

    # Store form data and result in MongoDB
    form_data = {
        'pl_orbper': pl_orbper,
        'pl_rade': pl_rade,
        'pl_orbeccen': pl_orbeccen,
        'pl_orbincl' : pl_orbincl,
        'pl_tranmid' : pl_tranmid,
        'pl_imppar' : pl_imppar,
        'pl_trandep' : pl_trandep,
        'pl_trandur' : pl_trandur,
        'pl_ratdor' : pl_ratdor,
        'pl_ratror' : pl_ratror,
        'sy_vmag' : sy_vmag,
        'sy_kmag' : sy_kmag,
        'ttv_flag': ttv_flag
    }
    collection.insert_one(form_data)

    return ttv_flag
