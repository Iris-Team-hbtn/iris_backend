# import os
# import json
import uuid
from flask import request, make_response


# treatment_prices = {
#     "IMPLANTE CAPILAR CON DHI": "3850 USD",
#     "IMPLANTE CAPILAR CON FUE": "2500 USD",
#     "MESOTERAPIA CAPILAR POR SESION": "100 USD",
#     "MESOTERAPIA CAPILAR PACK DE 4 SESIONES": "370 USD",
#     "MESOTERAPIA CAPILAR PACK DE 8 SESIONES": "700 USD"
#     }

# def contar(a: str):
#     """returns result"""
#     result= len(a)
#     return result

# def get_treatment_price(treatment: str):
#     asking = treatment.upper()
#     result = treatment_prices.get(asking, "Unknown")
#     return result

#Creando un identificador unico
def get_or_create_user_id():
    user_id = request.cookies.get('user_id')
    if not user_id:
        user_id = str(uuid.uuid4())
    return user_id