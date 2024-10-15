from flask import (
   session
)

def clearSessionKeepUser():
    keysToKeep = ['user_id', '_flashes', 'admin']
    deleteKeys = []
    for key in session:
        if key not in keysToKeep:
            deleteKeys.append(key)
    for key in deleteKeys:
        del session[key]


            

        
