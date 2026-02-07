#!/usr/bin/python

"""
Topologia Mininet-WiFi: Rede distribuída com múltiplos APs e switch central
Autor: Script gerado para simulação de rede sem fio empresarial
Componentes:
- 4 estações sem fio (sta1, sta2, sta3, sta4)
- 2 pontos de acesso (ap1, ap2) em canais não interferentes
- 1 switch central (s1) interligando os APs
- 1 controlador SDN (c0)
Distribuição:
- ap1 (canal 1): sta1, sta2
- ap2 (canal 6): sta3, sta4
"""

# Importações necessárias do Mininet-WiFi e Mininet
from mininet.node import Controller, OVSKernelSwitch
from mininet.log import setLogLevel, info
from mn_wifi.net import Mininet_wifi
from mn_wifi.node import OVSKernelAP
from mn_wifi.cli import CLI
from mn_wifi.link import wmediumd
from mn_wifi.wmediumdConnector import interference

def criar_topologia():
    """Função que cria e configura a topologia completa da rede"""
    
    info("*** Inicializando rede Mininet-WiFi\n")
    # Cria instância da rede com tipos de nós especificados
    net = Mininet_wifi(controller=Controller,
                       accessPoint=OVSKernelAP,
                       switch=OVSKernelSwitch,
                       link=wmediumd,
                       wmediumd_mode=interference)
    
    info("*** Adicionando controlador SDN\n")
    # Controlador OpenFlow para gerenciamento centralizado
    c0 = net.addController('c0',
                           controller=Controller,
                           protocol='tcp',
                           port=6653)
    
    info("*** Adicionando switch central da topologia\n")
    # Switch que interconecta os pontos de acesso
    s1 = net.addSwitch('s1',
                       cls=OVSKernelSwitch,
                       protocols='OpenFlow13',
                       failMode='standalone')
    
    info("*** Adicionando pontos de acesso Wi-Fi\n")
    # Ponto de acesso 1 - região oeste da rede
    ap1 = net.addAccessPoint('ap1',
                             ssid='rede-corporativa-oeste',
                             mode='g',
                             channel='1',
                             position='25,50,0',
                             range=30,
                             failMode='standalone')
    
    # Ponto de acesso 2 - região leste da rede
    ap2 = net.addAccessPoint('ap2',
                             ssid='rede-corporativa-leste',
                             mode='g',
                             channel='6',
                             position='75,50,0',
                             range=30,
                             failMode='standalone')
    
    info("*** Adicionando estações sem fio da rede\n")
    # Estações do ponto de acesso 1 (ap1)
    sta1 = net.addStation('sta1',
                          ip='10.0.0.1/24',
                          mac='00:00:00:00:00:01',
                          position='15,45,0',
                          range=15)
    
    sta2 = net.addStation('sta2',
                          ip='10.0.0.2/24',
                          mac='00:00:00:00:00:02',
                          position='20,55,0',
                          range=15)
    
    # Estações do ponto de acesso 2 (ap2)
    sta3 = net.addStation('sta3',
                          ip='10.0.0.3/24',
                          mac='00:00:00:00:00:03',
                          position='80,45,0',
                          range=15)
    
    sta4 = net.addStation('sta4',
                          ip='10.0.0.4/24',
                          mac='00:00:00:00:00:04',
                          position='85,55,0',
                          range=15)
    
    info("*** Configurando modelo de propagação do sinal\n")
    # Modelo de propagação baseado em distância logarítmica
    net.setPropagationModel(model="logDistance", exp=4.5)
    
    info("*** Aplicando configurações Wi-Fi aos nós\n")
    # Configura todos os parâmetros sem fio das estações e APs
    net.configureWifiNodes()
    
    info("*** Criando links cabeados na topologia\n")
    # Conecta ap1 ao switch central com link Ethernet
    net.addLink(ap1, s1,
                bw=1000,
                delay='1ms',
                loss=0)
    
    # Conecta ap2 ao switch central com link Ethernet
    net.addLink(ap2, s1,
                bw=1000,
                delay='1ms',
                loss=0)
    
    info("*** Configurando associação das estações aos APs\n")
    # As estações se associam automaticamente aos APs mais próximos
    # sta1 e sta2 se conectarão ao ap1 devido à proximidade
    # sta3 e sta4 se conectarão ao ap2 devido à proximidade
    
    info("*** Plotando topologia da rede\n")
    # Habilita visualização gráfica da topologia (opcional)
    net.plotGraph(max_x=100, max_y=100)
    
    info("*** Construindo e iniciando a rede\n")
    # Constrói a topologia completa
    net.build()
    
    # Inicia o controlador SDN
    c0.start()
    
    # Inicia o switch central e o conecta ao controlador
    s1.start([c0])
    
    # Inicia os pontos de acesso e os conecta ao controlador
    ap1.start([c0])
    ap2.start([c0])
    
    info("*** Aguardando estabilização das conexões\n")
    # Pausa para permitir associação completa das estações
    import time
    time.sleep(3)
    
    info("*** Verificando associações das estações\n")
    # Exibe informações sobre as associações Wi-Fi
    for sta in [sta1, sta2, sta3, sta4]:
        info(f"{sta.name} conectada ao AP: {sta.params.get('associatedTo', 'Nenhum')}\n")
    
    info("\n*** Executando testes de conectividade global\n")
    # Testa conectividade entre todos os nós da rede
    net.pingAll()
    
    info("\n*** Testes de desempenho entre APs diferentes\n")
    # Teste de largura de banda entre estações de APs distintos
    info("Teste 1: sta1 (ap1) <-> sta3 (ap2)\n")
    net.iperf((sta1, sta3), seconds=5)
    
    info("\nTeste 2: sta2 (ap1) <-> sta4 (ap2)\n")
    net.iperf((sta2, sta4), seconds=5)
    
    info("\n*** Testes de desempenho no mesmo AP\n")
    # Teste de largura de banda entre estações do mesmo AP
    info("Teste 3: sta1 <-> sta2 (ambos em ap1)\n")
    net.iperf((sta1, sta2), seconds=5)
    
    info("\nTeste 4: sta3 <-> sta4 (ambos em ap2)\n")
    net.iperf((sta3, sta4), seconds=5)
    
    info("\n" + "=" * 70 + "\n")
    info("*** TOPOLOGIA CONFIGURADA COM SUCESSO ***\n")
    info("=" * 70 + "\n")
    info("Estrutura da rede:\n")
    info("  • Controlador: c0 (porta 6653)\n")
    info("  • Switch Central: s1 (OpenFlow 1.3)\n")
    info("  • Ponto de Acesso 1: ap1 (SSID: rede-corporativa-oeste, Canal: 1)\n")
    info("    └─ sta1 (10.0.0.1) - posição (15,45,0)\n")
    info("    └─ sta2 (10.0.0.2) - posição (20,55,0)\n")
    info("  • Ponto de Acesso 2: ap2 (SSID: rede-corporativa-leste, Canal: 6)\n")
    info("    └─ sta3 (10.0.0.3) - posição (80,45,0)\n")
    info("    └─ sta4 (10.0.0.4) - posição (85,55,0)\n")
    info("=" * 70 + "\n")
    info("Comandos disponíveis no CLI:\n")
    info("  pingall                  - Testa conectividade completa\n")
    info("  sta1 ping sta3           - Ping específico entre estações\n")
    info("  iperf sta1 sta4          - Mede largura de banda\n")
    info("  sta1 iwconfig            - Exibe configuração Wi-Fi\n")
    info("  sta1 ifconfig            - Mostra interface de rede\n")
    info("  nodes                    - Lista todos os nós\n")
    info("  net                      - Exibe estrutura da rede\n")
    info("  links                    - Mostra todas as conexões\n")
    info("  dump                     - Informações detalhadas\n")
    info("  xterm sta1               - Abre terminal na estação\n")
    info("  exit                     - Encerra a simulação\n")
    info("=" * 70 + "\n")
    
    # Inicia CLI interativa do Mininet-WiFi
    CLI(net)
    
    info("\n*** Encerrando a rede e limpando configurações\n")
    # Para todos os processos e remove configurações
    net.stop()

if __name__ == '__main__':
    # Configura nível de detalhamento dos logs
    setLogLevel('info')
    
    # Executa a criação da topologia
    criar_topologia()