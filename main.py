from fastapi import FastAPI, Query
import httpx
import re

app = FastAPI(title="API Ragnarok Divine Pride", version="2.0")

BASE_URL = "https://www.divine-pride.net/api/database/Item"

REGEX_ATRIBUTOS = {
    "for": r"\+(\d+)\s*FOR",
    "int": r"\+(\d+)\s*INT",
    "des": r"\+(\d+)\s*DES",
    "agi": r"\+(\d+)\s*AGI",
    "vit": r"\+(\d+)\s*VIT",
    "sor": r"\+(\d+)\s*SOR",
}

@app.get("/atributos")
async def buscar_por_atributos(
    atributo: str = Query(..., description="Atributo: for, int, des, vit, agi ou sor"),
    tipo: str = Query("item", description="Tipo: item ou card"),
    nome: str = Query("", description="Parte do nome"),
    slots: int = Query(None, description="Número exato de slots"),
    nivel: int = Query(None, description="Nível mínimo")
):
    atributo = atributo.lower()
    if atributo not in REGEX_ATRIBUTOS:
        return {"erro": "Atributo inválido. Use: for, int, des, vit, agi ou sor."}

    params = {"name": nome}
    if tipo == "card":
        params["type"] = "Card"

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(BASE_URL, params=params)
            resp.raise_for_status()
            dados = resp.json()
    except Exception as e:
        return {"erro": str(e)}

    resultado = []
    for item in dados:
        desc = item.get("description", "")
        if re.search(REGEX_ATRIBUTOS[atributo], desc, re.IGNORECASE):
            if slots is not None and item.get("slots") != slots:
                continue
            if nivel is not None and item.get("equipLevel") != nivel:
                continue
            resultado.append({
                "id": item.get("id"),
                "nome": item.get("name"),
                "tipo": item.get("type"),
                "slots": item.get("slots"),
                "nivel": item.get("equipLevel"),
                "descricao": desc
            })
    return {"itens": resultado}
