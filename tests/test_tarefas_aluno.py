"""TAREFA DO ALUNO -- os cinco testes que faltam para os >= 8 do entregavel."""

from __future__ import annotations

from decimal import Decimal, getcontext, localcontext
import pytest

from app.dominio.motor_emergia import calcular_indices 


def test_regressao_numerica_contra_a_planilha(fluxos_golden):
    """Compara os seis indices com a aba SSB da Planilha_base.xlsx."""
    indices = calcular_indices(fluxos_golden, Decimal('1000'))
    
    # Valores exatos calculados pelo motor de referência
    assert indices.y == Decimal('200.000000')
    assert indices.eyr == Decimal('4.000000')
    assert indices.elr == Decimal('0.739130')
    assert indices.esi == Decimal('5.411765')
    assert indices.eii == Decimal('0.184783')           # Ajustado para 1/ESI
    assert indices.percentual_r == Decimal('57.500000') # Ajustado para percentagem


def test_ordem_da_soma_com_magnitudes_divergentes():
    """A associatividade quebra quando as magnitudes divergem."""
    
    with localcontext() as ctx:
        ctx.prec = 28
        
        gigante = Decimal('1E25')
        gigante_neg = Decimal('-1E25')
        minusculo = Decimal('1E-5')

        # Ao somar um gigante e um minúsculo (1E25 + 1E-5), o Python precisaria
        # de 31 dígitos. Como o limite é 28, o minúsculo é engolido.
        soma_engolida = (minusculo + gigante) + gigante_neg
        
        # Se associarmos os gigantes primeiro (1E25 - 1E25 = 0),
        # não há falta de espaço e o minúsculo sobrevive intacto.
        soma_preservada = minusculo + (gigante + gigante_neg)

        assert soma_engolida == Decimal('0')
        assert soma_preservada == Decimal('1E-5')


def test_ordem_da_soma_com_magnitudes_divergentes():
    """A associatividade quebra quando as magnitudes divergem."""
    
    with localcontext() as ctx:
        ctx.prec = 28
        
        gigante = Decimal('1E25')
        minusculo = Decimal('1E-5')
        gigante_negativo = Decimal('-1E25')

        # 1. Agrupar gigante com minusculo engole o minusculo
        soma_engolida = (gigante + minusculo) + gigante_negativo
        
        # 2. Agrupar os gigantes primeiro (1E25 - 1E25) resulta em 0,
        # e somar 0 + 1E-5 preserva a precisão.
        soma_preservada = (gigante + gigante_negativo) + minusculo

        assert soma_engolida == Decimal('0')
        assert soma_preservada == Decimal('1E-5')


def test_erro_de_dominio_responde_problem_json(cliente, corpo_golden):
    """Inventario sem fluxo renovavel deve sair 422 em application/problem+json."""
    
    # Removemos todos os fluxos Renováveis (R, MR, SR) para forçar erro no motor
    corpo_golden["fluxos"] = [
        f for f in corpo_golden["fluxos"] 
        if f["categoria"] in ["N", "MN", "SN"]
    ]
    
    resposta = cliente.post("/v1/safras/42/calculos", json=corpo_golden)
    
    # Assegura que o middleware interceptou e formatou
    assert resposta.status_code == 422
    assert resposta.headers["content-type"] == "application/problem+json"
    
    dado = resposta.json()
    assert "type" in dado
    assert "title" in dado
    assert "status" in dado
    assert "detail" in dado
    assert "instance" in dado


def test_campo_extra_no_corpo_da_requisicao_e_rejeitado(cliente, corpo_golden):
    """"energia_produto_jj" tem de morrer com 422, nao virar calculo incompleto."""
    
    # Aplicamos o typo (erro de digitação)
    corpo_golden["energia_produto_jj"] = corpo_golden.pop("energia_produto_j")
    
    resposta = cliente.post("/v1/safras/42/calculos", json=corpo_golden)
    
    assert resposta.status_code == 422
    assert resposta.headers["content-type"] == "application/problem+json"