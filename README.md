# Job Search Toolkit

Ferramentas simples e gratuitas (sem dependência de API paga) pra ajudar
na busca de vaga de tecnologia. Primeiro módulo: comparador de currículo
com descrição de vaga.

## Por que esse projeto existe

Grande parte das candidaturas nunca chega a ser lida por um humano —
sistemas de triagem automática (ATS) filtram currículos por
correspondência de palavras-chave com a descrição da vaga. Esse toolkit
ajuda a identificar, de forma objetiva, quais termos de uma vaga
específica não aparecem no seu currículo.

**Importante:** a ferramenta não reescreve seu currículo pra "enganar"
o ATS. Ela só aponta lacunas reais — cabe a você decidir se cada termo
faltando é algo que você genuinamente sabe fazer e vale adicionar.

## Como usar

Requer apenas Python 3.10+ (nenhuma biblioteca externa).

```bash
python3 resume_matcher.py --curriculo curriculo.txt --vaga vaga.txt
```

Ou no modo interativo (cola o texto direto no terminal):

```bash
python3 resume_matcher.py
```

## Saída

O script mostra:
- Uma nota de aderência (% de termos-chave da vaga presentes no currículo)
- Quais termos já aparecem no currículo
- Quais termos da vaga estão faltando, ordenados por relevância

## Roadmap

- [ ] Suporte a leitura direta de PDF (currículo em .pdf)
- [ ] Modo em lote: comparar um currículo com várias vagas de uma vez
- [ ] Sugestão automática de onde encaixar cada termo faltando

## Contribuindo

Esse projeto nasceu de uma necessidade pessoal durante uma busca de
emprego real. Se ele te ajudou, sinta-se à vontade pra abrir uma issue,
sugerir melhoria ou mandar um PR.

## Licença

MIT — use, copie, modifique e compartilhe à vontade.
