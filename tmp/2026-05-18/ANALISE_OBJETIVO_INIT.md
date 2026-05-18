# Análise Crítica do objetivo-init.yaml

**Projeto**: portfolio-generator
**Data**: 2026-05-18
**Analista**: GitHub Copilot (Claude Sonnet 4.5)
**Fase**: Pré-especificação

---

## 🎯 Objetivo desta Análise

Identificar **inconsistências**, **campos vazios** e **ambiguidades** no arquivo `objetivo-init.yaml` atual, fornecendo contexto técnico para facilitar o preenchimento do questionário.

---

## ⚠️ INCONSISTÊNCIA CRÍTICA DETECTADA

### Conflito: Propósito do Projeto

| Fonte | Propósito Declarado |
|-------|---------------------|
| **objetivo-init.yaml → description** | "Escanear pastas em /home/yves_marinho/Documentos/DevOps/ para gerar portfólio profissional em JSON" |
| **.copilot-rules.md → Context** | "Projeto usado para testar e validar scaffolding automático, processo de inicialização, configurações VS Code e MCP" |
| **README.md** | *(não analisado ainda, verificar)* |

### 🔴 Ação Necessária: RESOLVER ANTES DE PROSSEGUIR

**Decisão requerida** (responder na Seção 1 do questionário):

1. **Cenário A**: Este é um projeto **dual purpose**
   - Validação de template (primário)
   - Gerador de portfólio (secundário/experimental)

2. **Cenário B**: Objetivo-init.yaml está **desatualizado**
   - Atualizar description para refletir propósito de validação
   - Criar objetivo-portfolio.yaml separado para feature de portfólio

3. **Cenário C**: Copilot-rules.md está **desatualizado**
   - Projeto evoluiu para ferramenta de portfólio
   - Atualizar regras e documentação

**Impacto desta decisão**:
- Define todo o escopo do spec.md
- Determina features_to_implement
- Influencia infraestrutura necessária
- Afeta pending_tasks e prioridades

---

## 📊 Campos Vazios no YAML

### Criticidade: 🔴 ALTA (bloqueia geração de spec.md)

| Campo | Status | Impacto se não preenchido |
|-------|--------|---------------------------|
| `expected_outcome` | **VAZIO** | Sem critérios de sucesso definidos |
| `infrastructure` | **VAZIO** | Sem definição de ambiente/deploy |
| `features_to_implement` | **VAZIO** | Sem roadmap de funcionalidades |

### Criticidade: 🟡 MÉDIA (reduz qualidade da spec)

| Campo | Status | Impacto se não preenchido |
|-------|--------|---------------------------|
| `specification.docstyle` | Vazio | Documentação inconsistente |
| `rules[0]` | Vazio | Falta regra específica do projeto |
| `pending_tasks` | Lista vazia | Sem próximos passos definidos |

### Criticidade: 🟢 BAIXA (informacional)

| Campo | Status | Observação |
|-------|--------|------------|
| `specification.response` | Menção a Pandas/IA | Precisa detalhamento técnico (ver Seção 2.2) |
| `profile.skill_level` | "intermediate" | Adequado? Verificar Seção 8.2 |

---

## 🔍 Análise por Seção

### 1. Description & Specification

**Pontos positivos**:
- ✅ Estrutura de pastas bem definida e detalhada
- ✅ Regras de organização alinhadas com .copilot-rules.md
- ✅ Workflow SpecKit mencionado

**Pontos de atenção**:
- ⚠️ Descrição menciona "Pandas e IA" mas sem especificação técnica
- ⚠️ "Todas as extensões de código-fonte" é muito vago (quais exatamente?)
- ⚠️ Não define formato/schema do JSON de saída

**Perguntas críticas** (Seção 2 do questionário):
1. Quais bibliotecas de IA serão usadas?
2. Qual o schema do JSON de portfólio?
3. Como será feita a análise semântica de código?

---

### 2. Folder Structure

**Análise**:
- ✅ Estrutura completa e bem documentada
- ✅ Separação clara entre gerado/manual
- ✅ Alinhada com Enterprise Template

**Sugestões**:
- Considerar adicionar `src/portfolio/` se for feature real
- Considerar adicionar `schemas/` para JSON schemas
- Verificar se `tests/` ou `test/` (inconsistência com .copilot-rules)

---

### 3. Infrastructure (VAZIO)

**Informações faltantes críticas**:

1. **Ambiente de execução**:
   - Python version? (3.12+ mencionado em rules, confirmar)
   - Dependências de sistema? (git, tools específicos)
   - Gerenciador de pacotes? (uv está instalado, usar?)

2. **Deploy/Distribuição**:
   - CLI tool instalável?
   - Script standalone?
   - Módulo Python importável?

3. **Dados e persistência**:
   - Onde armazenar cache de análise?
   - SQLite para indexação?
   - Arquivos temporários em tmp/?

4. **Recursos computacionais**:
   - Se usar IA: local ou API externa?
   - Memória necessária para processar?
   - Paralelização (multiprocessing)?

**Recomendação**: Preencher Seção 5 do questionário com atenção especial.

---

### 4. Features to Implement (VAZIO)

**Análise de features mencionadas indiretamente**:

Baseado na description, features implícitas:

1. **Scanner de Diretórios**
   - Recursivo em /home/yves_marinho/Documentos/DevOps/
   - Filtros por extensão (configruável?)
   - Exclusão de .git, node_modules, etc.

2. **Analisador de Arquivos**
   - Parser de Markdown (README, docs)
   - Parser de código (Python, TS, etc.)
   - Extração de metadados (autor, licença, etc.)

3. **Análise com IA** (mencionado mas não especificado)
   - Geração de resumos?
   - Classificação de projetos?
   - Extração de tecnologias usadas?

4. **Gerador de JSON**
   - Schema definido?
   - Validação de saída?
   - Pretty-print ou compacto?

5. **Features de CLI** (não mencionadas)
   - Progress indicator?
   - Modo verbose/quiet?
   - Seleção de projetos específicos?

**Recomendação**: Listar e priorizar na Seção 6 do questionário.

---

### 5. Expected Outcome (VAZIO)

**Sugestões de critérios mensuráveis**:

**Se for projeto de portfólio**:
- [ ] JSON gerado para X projetos em menos de Y minutos
- [ ] Acurácia de Z% na detecção de tecnologias
- [ ] Schema JSON validado e documentado
- [ ] Documentação de uso completa

**Se for projeto de validação de template**:
- [ ] Scaffold upgrade sem erros em N projetos
- [ ] 100% das configurações MCP validadas
- [ ] Scripts de inicialização funcionais
- [ ] Documentação de processo completa

**Recomendação**: Definir 3-5 critérios objetivos na Seção 4 do questionário.

---

### 6. Pending Tasks (VAZIO)

**Tarefas implícitas necessárias**:

**Setup (semana 1)**:
- [ ] Definir schema JSON final
- [ ] Configurar ambiente de desenvolvimento
- [ ] Instalar dependências (pandas, etc.)
- [ ] Criar estrutura src/

**Desenvolvimento (semanas 2-3)**:
- [ ] Implementar scanner de diretórios
- [ ] Implementar parsers (MD, code)
- [ ] Integrar análise com IA (se aplicável)
- [ ] Implementar gerador de JSON

**Qualidade (semana 4)**:
- [ ] Escrever testes unitários
- [ ] Documentar código
- [ ] Validar com projetos reais
- [ ] Revisar e refatorar

**Recomendação**: Priorizar na Seção 7 do questionário.

---

## 🎓 Orientações Técnicas

### Para "Análise com Pandas e IA"

**Opção 1: Análise Local (Mais Simples)**
```python
import pandas as pd
from pathlib import Path

# Coletar metadados de arquivos
data = []
for file in Path("/caminho").rglob("*.py"):
    data.append({
        "path": str(file),
        "size": file.stat().st_size,
        "lines": len(file.read_text().splitlines()),
        # ... mais metadados
    })

df = pd.DataFrame(data)
# Análise descritiva com pandas
```

**Opção 2: Análise com LLM (Mais Complexo)**
```python
import openai  # ou anthropic
# Para cada arquivo relevante:
# 1. Ler conteúdo
# 2. Enviar para LLM com prompt específico
# 3. Extrair informações estruturadas
# 4. Agregar em JSON final
```

**Opção 3: Análise Híbrida (Recomendado)**
- Metadados básicos: pandas/pathlib
- Análise de código: AST (Python) / tree-sitter
- Resumos/descrições: LLM apenas para READMEs

---

### Para Schema JSON de Portfólio

**Sugestão de estrutura**:
```json
{
  "version": "1.0",
  "generated_at": "2026-05-18T...",
  "scan_path": "/home/yves_marinho/Documentos/DevOps/",
  "projects": [
    {
      "name": "portfolio-generator",
      "path": "Projetos/portfolio-generator",
      "type": "validation-project",
      "languages": ["Python", "Shell"],
      "description": "...",
      "technologies": ["VS Code", "MCP", "GitHub Actions"],
      "metrics": {
        "files": 252,
        "lines_of_code": 18000,
        "last_commit": "2026-05-18"
      }
    }
  ]
}
```

---

## ✅ Checklist de Validação Pré-Spec

Antes de gerar spec.md, garantir:

- [ ] **Propósito do projeto está claro** (portfólio vs validação)
- [ ] **Expected outcome está definido** (critérios mensuráveis)
- [ ] **Infrastructure está especificada** (ambiente, deploy)
- [ ] **Features estão priorizadas** (MVP vs nice-to-have)
- [ ] **Pending tasks têm sequência lógica** (setup → dev → QA)
- [ ] **Docstyle está escolhido** (se houver código)
- [ ] **Regras específicas estão listadas** (se houver)
- [ ] **Questionário foi preenchido completamente**

---

## 🚀 Recomendação de Workflow

### Fase 1: Clarificação (AGORA)
1. ✅ Questionário gerado
2. ⏳ **Preencher questionário** (próximo passo)
3. ⏳ Revisar respostas
4. ⏳ Resolver inconsistência de propósito

### Fase 2: Especificação (DEPOIS)
5. Atualizar objetivo-init.yaml
6. Executar SpecKit (gerar spec.md)
7. Revisar spec.md
8. Gerar plan.md e tasks.md

### Fase 3: Implementação (MUITO DEPOIS)
9. Começar tasks em ordem
10. Iteração e feedback
11. Documentação contínua

---

## 📌 Decisões Urgentes

| # | Decisão | Impacto | Prazo |
|---|---------|---------|-------|
| 1 | Propósito: Portfólio vs Validação | Define escopo completo | IMEDIATO |
| 2 | Usar IA ou apenas análise estática? | Define infraestrutura | ALTA |
| 3 | Schema JSON de saída | Define features | ALTA |
| 4 | Distribuição (CLI/módulo/script) | Define estrutura de código | MÉDIA |

---

*Documento complementar ao QUESTIONARIO_OBJETIVO_INIT.md*
*Versão: 1.0 | Data: 2026-05-18*
