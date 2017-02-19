import pickle
import os
DIR="/tmp/.cache/"

def store_object(k,v):
    if not os.path.exists(DIR):
        os.makedirs(DIR)
    path = DIR + "-".join(k)
    #print("CACHE TO:"+path)
    f = open(path, 'wb') 
    pickle.dump(v, f)
    f.close()

def fetch_object(k):
    path = DIR + "-".join(k)
    #print("FETCHING FROM:"+path)
    if os.path.exists(path):
        f = open(path, 'rb') 
        v = pickle.load(f)
        f.close()
        return v
    else:
        return None
    
