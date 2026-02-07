# Análise do uso de Modelos de Linguagem de Grande Escala na Geração de Códigos para Simulação de Redes utilizando o Mininet‑WiFi

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Resumo do Artigo:** O trabalho investiga a capacidade de modelos de linguagem de grande escala (LGEs) de gerar scripts em Python para um emulador de redes cabeadas e sem fio, o Mininet‑WiFi. O estudo realiza uma análise dos fatores que influenciam a eficácia desses modelos na produção de códigos funcionais em três níveis de complexidade de simulação. Para cada nível, são aplicados prompts simples e detalhados, a fim de analisar como as instruções influenciam o desempenho dos códigos gerados. Além disso, o estudo compara o melhor modelo online e um modelo local open‑weight na reprodução de um exemplo oficial do Mininet‑WiFi, avaliando sua capacidade de gerar scripts funcionais semelhantes.

Este repositório contém o conjunto de dados e scripts necessários para replicar a avaliação de Modelos de Linguagem de Grande Escala (LGEs) na geração de cenários de rede para o Mininet-WiFi. O artefato inclui os prompts utilizados, os códigos Python gerados pelos modelos (GPT-5, Gemini 3, Claude 4.5 e DeepSeek-V3), logs de erros e os scripts de validação funcional e estatística.

# Estrutura do readme.md

Este README.md está organizado da seguinte forma:

- [Artefatos incluídos](#selos-considerados)
- [Selos Considerados](#selos-considerados)
- [Informações básicas](#informações-básicas)
- [Dependências](#dependências)
- [Preocupações com segurança](#preocupações-com-segurança)
- [Instalação](#instalação)
- [Teste mínimo](#teste-mínimo)
- [#Experimentos e Avaliação](#experimentos-e-avaliação)
- [LICENSE](#license)

## Artefatos incluídos
O repositório contém:

- `scripts/`
  - `prompts/` – arquivos de texto com os prompts simples e específicos usados para cada cenário (básico, intermediário, avançado).
  - `generated/` – scripts Python gerados pelos modelos para cada combinação cenário × prompt × modelo (organizados em subpastas).
  - `examples/` – cópia de referência do `handover.py` do repositório oficial do Mininet‑WiFi e script(s) gerados pelos modelos para esse cenário.
- `analysis/`
  - `data/` – resultados em CSV (por exemplo, uma linha por script com colunas: `modelo`, `cenario`, `tipo_prompt`, `correcao_funcional`, `necessidade_ajuste`, `tipo_erro`).
  - `notebooks/` ou `analysis.py` – código para gerar Tabelas 2, 3 e Figura 2 (análise fatorial e ANOVA).
- `ollama/`
  - arquivos de configuração e exemplos de prompts usados com o `gpt‑oss‑20B`.
- `README.md` – este arquivo.
- `LICENSE` – licença do projeto.

---

# Selos Considerados
Os selos considerados são:
- **Artefatos Disponíveis (SeloD)**
- **Artefatos Funcionais (SeloF)**
- **Artefatos Sustentáveis (SeloS)**
- **Experimentos Reprodutíveis (SeloR)**

---

# Informações básicas

Esta seção apresenta as informações fundamentais de todos os componentes necessários para a execução e replicação dos experimentos.

## Ambiente de execução recomendado

Os experimentos foram executados e validados em um ambiente Linux com as seguintes especificações:
* **Sistema operacional**: Ubuntu 22.04 LTS (ou equivalente).
* **Hardware mínimo recomendado**:
    * **CPU**: 4 cores.
    * **RAM**: 8 GB.
    * **Disco**: 20 GB de espaço livre (para scripts, logs e instalação do Mininet‑WiFi).
* **Software e Versões**:
    * **Python**: Versão 3.10 ou superior.
    * **Mininet‑WiFi**: Versão 2.6 (obtida via repositório oficial).
* **Ferramentas adicionais**:
    * `git` para clonagem dos repositórios.
    * `pip`/`virtualenv` para gerenciamento de bibliotecas Python.
    * **Ollama**: Necessário para a execução do modelo local `gpt‑oss‑20B`.
 
# Dependências
Esta seção descreve as ferramentas, plataformas e modelos utilizados para a execução e replicação dos experimentos.

## Reprodução da Fase 1 (Geração com modelos online)
A tabela abaixo detalha as plataformas e versões utilizadas na primeira fase do experimento:

| Desenvolvedor | Modelo / Plataforma | Site Oficial | Versões Avaliadas |
| :--- | :--- | :--- | :--- |
| **OpenAI** | ChatGPT | [chatgpt.com](https://chatgpt.com) | GPT 5.1 Thinking e GPT 5.2 Thinking |
| **Google** | Gemini | [gemini.google.com](https://gemini.google.com) | Gemini 3 e Gemini 3 Pro |
| **Anthropic** | Claude | [claude.com](https://claude.com) | Claude 4.5 Sonnet |
| **DeepSeek** | DeepSeek Chat | [chat.deepseek.com](https://chat.deepseek.com) | DeepSeek-V3 |

## Modelo local
A tabela abaixo descreve as especificações do modelo executado localmente para os testes de reprodução:

| Plataforma | Modelo Local | Site Oficial | Método de Adaptação |
| :--- | :--- | :--- | :--- |
| **Ollama** | gpt‑oss‑20B | [ollama.com](https://ollama.com) | Few-shot in-context learning |

### Ambiente de simulação e validação (Mininet-WiFi)
A validação funcional e operacional dos scripts gerados foi realizada em uma **instância do Mininet-WiFi*
* **Mininet-WiFi**: Plataforma de emulação para redes sem fio definidas por software utilizada para executar e validar os scripts Python gerados. 
    * **Site oficial**: https://mininet-wifi.github.io/ 
    * **Versão utilizada**: 2.6.

# Preocupações com segurança
* **Privilégios de Superusuário**: A execução dos artefatos requer comandos `sudo` para a criação de interfaces de rede e namespaces pelo Mininet-WiFi. Recomenda-se o uso de uma Máquina Virtual (VM) dedicada para garantir o isolamento do sistema host.
* **Desempenho de Modelos Locais**: A geração de códigos via modelos locais (como o `gpt‑oss‑20B`) depende diretamente da capacidade de processamento da máquina. Em sistemas sem aceleração por GPU (CUDA), o tempo de resposta pode ser elevado, sendo necessário aguardar a finalização do processamento pelo Ollama sem interromper a execução.



# Instalação
O processo de instalação prepara o ambiente para a execução dos scripts de emulação e replicação dos experimentos.

1.  ### **Atualização do Sistema**:
    ```bash
    sudo apt update && sudo apt upgrade -y
    ```

2.  ### **Instalação do Mininet-WiFi**:
    Recomenda-se o uso do Ubuntu versão 16.04 ou superior, pois alguns recursos do `hostapd` podem não funcionar em versões anteriores.

    Para instalar, siga os passos oficiais abaixo:
    * **Passo 1:** `$ sudo apt-get install git`
    * **Passo 2:** `$ git clone https://github.com/intrig-unicamp/mininet-wifi`
    * **Passo 3:** `$ cd mininet-wifi`
    * **Passo 4:** `$ sudo util/install.sh -Wlnfv`
    
    **Opções do install.sh utilizadas:**
    * `-W`: Dependências sem fio (wireless).
    * `-n`: Dependências do Mininet-WiFi.
    * `-f`: OpenFlow.
    * `-v`: OpenvSwitch.
    * `-l`: wmediumd.

    Para maiores dúvidas e suporte, acesse o repositório oficial: [https://github.com/intrig-unicamp/mininet-wifi](https://github.com/intrig-unicamp/mininet-wifi).

3.  ### **Configuração do Ollama (Necessário para Modelo Local)**:
    Caso deseje replicar os testes com o modelo local `gpt‑oss‑20B`:

    o instalador deve ser baixado diretamente no site oficial:
    * **Download:** [https://ollama.com](https://ollama.com)
      
      ou
      
    ```bash
    curl -fsSL [https://ollama.com/install.sh](https://ollama.com/install.sh) | sh
    ollama pull gpt-oss-20B
    ```
  

4.  ### **Verificação Final**:
    Certifique-se de que o Python 3.10+ está instalado:
    ```bash
    python3 --version
    ```

5. ### **Obtenção dos Artefatos do Artigo**:
    Clone este repositório para acessar os scripts gerados e os prompts utilizados:
    ```bash
    git clone [https://github.com/bps90/llms-mininet-wifi](https://github.com/bps90/llms-mininet-wifi)
    cd llms-mininet-wifi
    ```

# Teste mínimo
Esta seção apresenta um passo a passo para a execução de um teste de fumaça (*smoke test*) dividido em duas vertentes, garantindo que o ambiente e os artefatos estejam funcionais.

## Validação do Mininet-Wifi (Exemplo oficial)
O objetivo é garantir que o Mininet-WiFi foi instalado corretamente e consegue executar um exemplo que já vem instalado.

1. **Comando**:
   ```bash
   sudo python3 mininet-wifi/examples/simplewifi.py
   ```
   O emulador deve abrir o CLI do Mininet-WiFi.
   No prompt mininet-wifi>, digite sta1 ping sta2. (O ping deve responder com sucesso)
   Digite exit para encerrar.

## Validação de Código Gerado por IA
O objetivo é validar a execução de um script gerado por um dos modelos avaliados no artigo (Fase 1).

1. **Local do script**:
   codigos_gerados/gemini_3_pro/cenario_basico_especifico.py

2. **Comando**:
   ```bash
   sudo python3 codigos_gerados/gemini_3_pro/cenario_basico_especifico.py
   ```
   O script instanciará as estações sta1 e sta2, o AP ap1 e o controlador c0.
   ELe executará automaticamente o método pingAll() para testar a conectividade.
   O console deve exibir a montagem da topologia sem erros de sintaxe ou de importação.
   
# Experimentos e Avaliação
## Entradas (arquivos e organização do repositório)

As entradas necessárias para executar os experimentos do artigo estão organizadas em duas estruturas principais: (i) **scripts gerados pelos modelos** e (ii) **prompts utilizados na geração**.

### 1) Scripts gerados (por cenário)

Os códigos gerados estão na pasta `scripts/`, organizada em três subpastas, uma para cada nível de complexidade do cenário:

- `scripts/basico/`
- `scripts/intermed/`
- `scripts/avancado/`

Em cada subpasta, existem múltiplos arquivos `.py`, onde **cada arquivo corresponde a um script gerado por um modelo específico**, utilizando um dos dois tipos de prompt:
- `s_<modelo>.py`  → script gerado pelo `<modelo>` usando **prompt simples**
- `p_<modelo>.py`  → script gerado pelo `<modelo>` usando **prompt detalhado**

Exemplos:
- `s_gemini3.py` → script do **Gemini 3** com prompt simples
- `p_gemini3pro.py` → script do **Gemini 3 Pro** com prompt detalhado
- `s_claud.py` / `p_claud.py` → scripts do **Claude** (simples/detalhado)
- `s_deepseek.py` / `p_deepseek.py` → scripts do **DeepSeek** (simples/detalhado)
- `s_gpt1.py`, `s_gpt2.py` / `p_gpt1.py`, `p_gpt2.py` → scripts do **GPT** (variações conforme definidas no estudo)

> Observação: a pasta do cenário define o nível (básico/intermediário/avançado) e o prefixo `s_`/`p_` define o tipo de prompt.

---

### 2) Prompts utilizados

Os prompts estão na pasta `prompts/` e incluem:

- `prompts/contextualizacao`  
  Contém o texto de **contextualização** aplicado antes dos prompts de cenário, para padronizar o entendimento do modelo sobre o objetivo e o ambiente.

- Prompts de cenário (por nível e tipo):
  - `prompts/p-basico_simples`
  - `prompts/p-basico_especifico`
  - `prompts/p-interm_simples`
  - `prompts/p-interm_especifico`
  - `prompts/p-avanc_simples`
  - `prompts/p-avanc_especifico`

Esses arquivos representam os **prompts de cenário** (básico/intermediário/avançado), cada um em duas versões:
- **simples**: descrição generalista do cenário
- **específico/detalhado**: descrição com maior nível de detalhe e parâmetros relevantes

---

## Execução e validação dos scripts gerados

### Como executar um script

A partir da raiz do repositório, execute o script desejado informando o caminho do arquivo:

```bash
# Exemplo: cenário avançado, prompt simples, modelo Gemini 3
sudo python3 scripts/avancado/s_gemini3.py
````

## Análisr e consolidação dos resultados

Após a execução e validação funcional de cada script, os resultados foram avaliados e consolidados de forma padronizada, com o objetivo de permitir a análise comparativa entre **modelos**, **cenários** e **tipos de prompt** (simples vs específico).

### Critérios de avaliação (por script)

Para cada script executado, foram registrados os seguintes critérios:

1. **Execução (rodou / não rodou)**  
   Verifica se o script iniciou e executou sem interrupções impeditivas (erros fatais), permitindo a criação da topologia no Mininet-WiFi.

2. **Funcionalidade (funcional / não funcional)**  
   Um script foi considerado **funcional** quando:
   - a topologia foi inicializada corretamente, e
   - os elementos principais esperados do cenário foram criados (estações, APs, controlador/switch quando aplicável), e
   - foi possível observar conectividade mínima (ex.: ping entre nós ou teste equivalente) sem falhas críticas.

3. **Necessidade de ajuste (sim / não)**  
   Caso o script executasse apenas após correções, foi indicado **necessidade de ajuste**, distinguindo:
   - ajustes pequenos (imports, nomes de entidades, parâmetros simples, etc), e
   - ajustes estruturais (lógica de criação de topologia, chamadas Mininet-WiFi inexistentes, etc).

**Classificação de erros**  
Quando o script não era funcional, o erro observado foi classificado em:
- **Erro de sintaxe**: falhas imediatas de execução (ex: `SyntaxError`, identação, imports ausentes);
- **Erro de lógica/execução**: código executa parcialmente, mas a topologia não corresponde ao cenário, entidades ausentes, associação Wi-Fi falha, ou interrupções em runtime;
- **Alucinação**: uso de funções, APIs ou parâmetros inexistentes no Mininet-WiFi, atributos inválidos ou chamadas incompatíveis com a versão utilizada.

Os resultados de cada execução foram registrados para comparar desempenho entre **modelos** por nível de complexidade, o impacto de **tipo de prompt**, eos padrões de falhas por **tipo de erro**.

## Execução com modelo local (Ollama)

A etapa com **modelo local** seguiu o mesmo padrão metodológico aplicado na geração com modelos online, preservando a **mesma contextualização inicial** utilizada nos demais experimentos, de forma a manter consistência entre as condições de geração.

Além disso, para aumentar a eficiêcia  do modelo local ao ambiente do **Mininet-WiFi** e reduzir ambiguidades, foi empregada uma estratégia de **contextualização ampliada**, na qual foram adicionados **exemplos concretos (few-shot)** antes do prompt do cenário. Em particular, foram incluídos trechos e/ou instruções baseadas no caso do **`handover.py`** (exemplo de referência do Mininet-WiFi), de modo que o modelo tivesse uma noção mais explícita do padrão de implementação esperado, incluindo organização do script, principais chamadas de configuração e estrutura típica de execução.

Em termos operacionais, a geração local foi conduzida com:
- **Contextualização padrão** (mesmo conteúdo empregado na fase online);
- **Exemplos adicionais (few-shot)**, com destaque para o cenário `handover.py`, para reforçar o formato do código e a utilização correta das APIs do Mininet-WiFi;
- **Prompt do cenário alvo** (simples ou específico), aplicado após o contexto e os exemplos.

Após a geração, o script produzido foi submetido ao mesmo procedimento de validação funcional, incluindo execução no Mininet-WiFi, inspeção das entidades criadas e testes mínimos de conectividade (por exemplo, ping e verificação de associação).

# LICENSE
Este repositório é distribuído sob a licença **MIT**

