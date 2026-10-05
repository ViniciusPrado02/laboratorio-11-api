"""PASSO 4 do laboratorio: a rota-armadilha.

Higiene: apague este arquivo ao final da aula, ou mantenha-o num branch de
demonstracao. Codigo que ensina errado nao fica em main.
"""

from __future__ import annotations

import time

from fastapi import APIRouter

router = APIRouter(prefix="/v1/demo", tags=["armadilha"])

import time

@router.get("/travada")
def travada(): # <-- Tiramos a palavra 'async' daqui!
    time.sleep(10)
    return {"status": "ok"}