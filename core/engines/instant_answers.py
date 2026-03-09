import re

CATEGORIES = ["general", "news", "videos", "images", "social", "it"]
WEIGHT = 5.0  # Máxima prioridad absoluta para herramientas locales

def request(query, params):
    # No hace petición externa, procesamos localmente
    params["url"] = "internal://instant" 

def response(resp):
    query = resp.search_params.get("query", "").lower().strip()
    results = []
    
    # 1. Calculadora Matemática Simple
    math_pattern = r'^[\d\s\+\-\*\/\(\)\.\^]+$'
    if re.match(math_pattern, query) and any(op in query for op in "+-*/^"):
        try:
            # Reemplazar ^ con ** para Python
            safe_query = query.replace("^", "**")
            # Evaluar de forma segura (limitado a números y operadores)
            # Solo permitimos caracteres seguros previstos por el regex
            result = eval(safe_query, {"__builtins__": None}, {})
            results.append({
                "title": f"Resultado: {result}",
                "content": f"Cálculo matemático para: {query}",
                "url": "#",
                "template": "infobox.html",
                "source": "calculator"
            })
        except:
            pass

    # 2. Conversor de Unidades (Ej: 10km to miles)
    unit_map = {
        "km": {"to": "miles", "factor": 0.621371},
        "miles": {"to": "km", "factor": 1.60934},
        "kg": {"to": "lb", "factor": 2.20462},
        "lb": {"to": "kg", "factor": 0.453592},
        "c": {"to": "f", "op": lambda x: (x * 9/5) + 32},
        "f": {"to": "c", "op": lambda x: (x - 32) * 5/9}
    }
    
    match = re.search(r'(\d+\.?\d*)\s*(km|miles|kg|lb|c|f)\s*(?:to|a|in)\s*(km|miles|kg|lb|c|f)', query)
    if match:
        val = float(match.group(1))
        from_u = match.group(2)
        to_u = match.group(3)
        
        if from_u in unit_map and unit_map[from_u]["to"] == to_u:
            converted = val * unit_map[from_u]["factor"]
            results.append({
                "title": f"{val}{from_u} = {round(converted, 2)}{to_u}",
                "content": "Conversión de unidades instantánea.",
                "url": "#",
                "template": "infobox.html",
                "source": "unit_converter"
            })
        elif from_u in ["c", "f"] and to_u in ["c", "f"] and from_u != to_u:
            converted = unit_map[from_u]["op"](val)
            results.append({
                "title": f"{val}°{from_u.upper()} = {round(converted, 2)}°{to_u.upper()}",
                "content": "Conversión de temperatura instantánea.",
                "url": "#",
                "template": "infobox.html",
                "source": "unit_converter"
            })

    return results
