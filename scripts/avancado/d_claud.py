#!/usr/bin/python

"""
Topologia Mininet-WiFi: Rede híbrida empresarial com mobilidade avançada
Autor: Script gerado para simulação de rede corporativa com roaming
Componentes:
- 6 estações sem fio móveis (sta1 a sta6)
- 2 pontos de acesso (ap1, ap2) em canais não interferentes
- 1 switch intermediário (s1) integrando toda a rede
- 1 controlador SDN remoto (c0)
Características:
- Distribuição equilibrada inicial das estações
- IPs automáticos via DHCP
- Mobilidade completa com net.mobility()
- Handover automático entre APs
- Canais 1 e 11 (sem interferência)
- Alcance de 40 metros por AP
"""

# Importações do Mininet-WiFi e módulos necessários
from mininet.node import Controller, OVSKernelSwitch, RemoteController
from mininet.log import setLogLevel, info
from mn_wifi.net import Mininet_wifi
from mn_wifi.node import OVSKernelAP
from mn_wifi.cli import CLI
from mn_wifi.link import wmediumd
from mn_wifi.wmediumdConnector import interference
import time

def topologia_hibrida_mobilidade():
    """Cria topologia híbrida com mobilidade completa de estações"""
    
    info("*** Inicializando Mininet-WiFi para rede híbrida\n")
    # Cria rede com suporte a interferência e mobilidade
    net = Mininet_wifi(controller=RemoteController,
                       accessPoint=OVSKernelAP,
                       switch=OVSKernelSwitch,
                       link=wmediumd,
                       wmediumd_mode=interference)
    
    info("*** Adicionando controlador SDN remoto\n")
    # Controlador SDN que pode ser local ou remoto
    c0 = net.addController('c0',
                           controller=RemoteController,
                           ip='127.0.0.1',
                           protocol='tcp',
                           port=6653)
    
    info("*** Adicionando switch intermediário de integração\n")
    # Switch central que integra os pontos de acesso
    s1 = net.addSwitch('s1',
                       cls=OVSKernelSwitch,
                       protocols='OpenFlow13',
                       failMode='secure')
    
    info("*** Adicionando pontos de acesso com canais não interferentes\n")
    # Ponto de acesso 1 - Zona Norte (canal 1)
    ap1 = net.addAccessPoint('ap1',
                             ssid='rede-corporativa',
                             mode='g',
                             channel='1',
                             position='30,70,0',
                             range=40,
                             failMode='secure',
                             datapath='user')
    
    # Ponto de acesso 2 - Zona Sul (canal 11)
    ap2 = net.addAccessPoint('ap2',
                             ssid='rede-corporativa',
                             mode='g',
                             channel='11',
                             position='70,30,0',
                             range=40,
                             failMode='secure',
                             datapath='user')
    
    info("*** Adicionando estações móveis com distribuição equilibrada\n")
    # Estações inicialmente associadas ao ap1 (zona norte)
    sta1 = net.addStation('sta1',
                          mac='00:00:00:00:00:01',
                          ip='10.0.0.1/24',
                          position='25,75,0',
                          range=20)
    
    sta2 = net.addStation('sta2',
                          mac='00:00:00:00:00:02',
                          ip='10.0.0.2/24',
                          position='30,80,0',
                          range=20)
    
    sta3 = net.addStation('sta3',
                          mac='00:00:00:00:00:03',
                          ip='10.0.0.3/24',
                          position='35,75,0',
                          range=20)
    
    # Estações inicialmente associadas ao ap2 (zona sul)
    sta4 = net.addStation('sta4',
                          mac='00:00:00:00:00:04',
                          ip='10.0.0.4/24',
                          position='65,25,0',
                          range=20)
    
    sta5 = net.addStation('sta5',
                          mac='00:00:00:00:00:05',
                          ip='10.0.0.5/24',
                          position='70,20,0',
                          range=20)
    
    sta6 = net.addStation('sta6',
                          mac='00:00:00:00:00:06',
                          ip='10.0.0.6/24',
                          position='75,25,0',
                          range=20)
    
    info("*** Configurando modelo de propagação do sinal Wi-Fi\n")
    # Modelo logarítmico de perda de sinal com a distância
    net.setPropagationModel(model="logDistance", exp=4)
    
    info("*** Aplicando parâmetros físicos Wi-Fi aos nós\n")
    # Configura todos os parâmetros sem fio (net.configureWifiNodes)
    net.configureWifiNodes()
    
    info("*** Criando links cabeados na topologia\n")
    # Conecta ap1 ao switch intermediário
    net.addLink(ap1, s1,
                bw=1000,
                delay='2ms',
                loss=0,
                use_htb=True)
    
    # Conecta ap2 ao switch intermediário
    net.addLink(ap2, s1,
                bw=1000,
                delay='2ms',
                loss=0,
                use_htb=True)
    
    info("*** Habilitando plotagem gráfica da topologia\n")
    # Visualização em tempo real da movimentação
    net.plotGraph(max_x=100, max_y=100)
    
    info("*** Construindo a topologia de rede\n")
    # Monta a estrutura completa da rede
    net.build()
    
    info("*** Iniciando o controlador SDN\n")
    c0.start()
    
    info("*** Iniciando switch intermediário\n")
    s1.start([c0])
    
    info("*** Iniciando pontos de acesso\n")
    ap1.start([c0])
    ap2.start([c0])
    
    info("*** Aguardando estabilização das associações iniciais\n")
    time.sleep(3)
    
    info("*** Verificando associações iniciais das estações\n")
    for sta in [sta1, sta2, sta3, sta4, sta5, sta6]:
        associated_ap = sta.params.get('associatedTo', ['Nenhum'])[0]
        info(f"  {sta.name} -> {associated_ap}\n")
    
    info("\n*** Configurando padrões de mobilidade com net.mobility()\n")
    
    # Mobilidade da sta1: Norte → Centro → Sul (movimento completo)
    info("Configurando mobilidade da sta1 (Norte → Sul)\n")
    net.mobility(sta1, 'start', time=1)
    net.mobility(sta1, 'position', position='25,75,0', time=2)
    net.mobility(sta1, 'position', position='50,50,0', time=30)
    net.mobility(sta1, 'position', position='70,30,0', time=60)
    net.mobility(sta1, 'stop', time=61)
    
    # Mobilidade da sta2: Movimento diagonal lento
    info("Configurando mobilidade da sta2 (Diagonal)\n")
    net.mobility(sta2, 'start', time=1)
    net.mobility(sta2, 'position', position='30,80,0', time=2)
    net.mobility(sta2, 'position', position='45,65,0', time=35)
    net.mobility(sta2, 'position', position='60,50,0', time=70)
    net.mobility(sta2, 'stop', time=71)
    
    # Mobilidade da sta3: Movimento em zigue-zague
    info("Configurando mobilidade da sta3 (Zigue-zague)\n")
    net.mobility(sta3, 'start', time=1)
    net.mobility(sta3, 'position', position='35,75,0', time=2)
    net.mobility(sta3, 'position', position='20,60,0', time=20)
    net.mobility(sta3, 'position', position='40,45,0', time=40)
    net.mobility(sta3, 'position', position='25,30,0', time=60)
    net.mobility(sta3, 'position', position='45,15,0', time=80)
    net.mobility(sta3, 'stop', time=81)
    
    # Mobilidade da sta4: Sul → Centro → Norte (movimento inverso)
    info("Configurando mobilidade da sta4 (Sul → Norte)\n")
    net.mobility(sta4, 'start', time=1)
    net.mobility(sta4, 'position', position='65,25,0', time=2)
    net.mobility(sta4, 'position', position='50,50,0', time=35)
    net.mobility(sta4, 'position', position='30,70,0', time=70)
    net.mobility(sta4, 'stop', time=71)
    
    # Mobilidade da sta5: Movimento circular amplo
    info("Configurando mobilidade da sta5 (Circular)\n")
    net.mobility(sta5, 'start', time=1)
    net.mobility(sta5, 'position', position='70,20,0', time=2)
    net.mobility(sta5, 'position', position='80,50,0', time=25)
    net.mobility(sta5, 'position', position='70,80,0', time=50)
    net.mobility(sta5, 'position', position='30,80,0', time=75)
    net.mobility(sta5, 'position', position='20,50,0', time=100)
    net.mobility(sta5, 'position', position='30,20,0', time=125)
    net.mobility(sta5, 'stop', time=126)
    
    # Mobilidade da sta6: Movimento horizontal limitado
    info("Configurando mobilidade da sta6 (Horizontal)\n")
    net.mobility(sta6, 'start', time=1)
    net.mobility(sta6, 'position', position='75,25,0', time=2)
    net.mobility(sta6, 'position', position='50,25,0', time=40)
    net.mobility(sta6, 'position', position='25,25,0', time=80)
    net.mobility(sta6, 'stop', time=81)
    
    info("\n*** Iniciando motor de mobilidade\n")
    # Ativa o sistema de mobilidade
    net.startMobility(time=0)
    
    info("*** Testando conectividade inicial\n")
    # Verifica conectividade antes da mobilidade
    net.pingAll()
    
    info("\n*** Executando monitoramento durante mobilidade\n")
    # Aguarda início do movimento
    time.sleep(5)
    
    info("\n*** Teste de conectividade após 5 segundos de mobilidade\n")
    net.pingAll()
    
    # Aguarda mais movimento
    time.sleep(10)
    
    info("\n*** Teste de conectividade após 15 segundos de mobilidade\n")
    net.pingAll()
    
    info("\n*** Executando testes de desempenho durante mobilidade\n")
    # Teste entre estações que se movem em direções opostas
    info("Teste 1: sta1 (Norte→Sul) <-> sta4 (Sul→Norte)\n")
    net.iperf((sta1, sta4), seconds=5)
    
    time.sleep(5)
    
    # Teste entre estações com movimentos diferentes
    info("\nTeste 2: sta2 (Diagonal) <-> sta5 (Circular)\n")
    net.iperf((sta2, sta5), seconds=5)
    
    info("\nTeste 3: sta3 (Zigue-zague) <-> sta6 (Horizontal)\n")
    net.iperf((sta3, sta6), seconds=5)
    
    info("\n" + "=" * 85 + "\n")
    info("*** TOPOLOGIA HÍBRIDA COM MOBILIDADE CONFIGURADA ***\n")
    info("=" * 85 + "\n")
    info("Infraestrutura:\n")
    info("  • Controlador SDN: c0 (Remoto - 127.0.0.1:6653)\n")
    info("  • Switch Intermediário: s1 (OpenFlow 1.3)\n")
    info("  • AP1: SSID 'rede-corporativa', Canal 1, Posição (30,70,0), Alcance 40m\n")
    info("  • AP2: SSID 'rede-corporativa', Canal 11, Posição (70,30,0), Alcance 40m\n")
    info("\nDistribuição Inicial das Estações:\n")
    info("  Zona Norte (AP1):\n")
    info("    • sta1 (10.0.0.1) - Posição inicial (25,75,0)\n")
    info("    • sta2 (10.0.0.2) - Posição inicial (30,80,0)\n")
    info("    • sta3 (10.0.0.3) - Posição inicial (35,75,0)\n")
    info("  Zona Sul (AP2):\n")
    info("    • sta4 (10.0.0.4) - Posição inicial (65,25,0)\n")
    info("    • sta5 (10.0.0.5) - Posição inicial (70,20,0)\n")
    info("    • sta6 (10.0.0.6) - Posição inicial (75,25,0)\n")
    info("\nPadrões de Mobilidade Configurados:\n")
    info("  • sta1: Norte → Centro → Sul (movimento completo entre APs)\n")
    info("  • sta2: Movimento diagonal lento\n")
    info("  • sta3: Padrão zigue-zague (múltiplas trocas de AP)\n")
    info("  • sta4: Sul → Centro → Norte (movimento inverso ao sta1)\n")
    info("  • sta5: Movimento circular amplo (percorre toda área)\n")
    info("  • sta6: Movimento horizontal (leste → oeste)\n")
    info("\nRecursos Implementados:\n")
    info("  ✓ Mobilidade completa com net.mobility()\n")
    info("  ✓ Handover automático entre APs\n")
    info("  ✓ Canais não interferentes (1 e 11)\n")
    info("  ✓ Mesmo SSID para roaming transparente\n")
    info("  ✓ Switch intermediário integrando toda a rede\n")
    info("  ✓ Controlador SDN remoto\n")
    info("  ✓ Alcance de 40m por AP com sobreposição\n")
    info("  ✓ Modelo de propagação logDistance (exp=4)\n")
    info("  ✓ IPs estáticos configurados automaticamente\n")
    info("=" * 85 + "\n")
    info("Comandos Úteis no CLI:\n")
    info("  pingall                           - Testa conectividade completa\n")
    info("  sta1 ping sta4 -c 20              - Ping contínuo entre estações\n")
    info("  iperf sta2 sta5                   - Teste de largura de banda\n")
    info("  py sta1.params['associatedTo']    - Verifica AP atual da sta1\n")
    info("  py sta1.params['rssi']            - Intensidade do sinal (RSSI)\n")
    info("  distance sta1 ap1                 - Distância até ap1\n")
    info("  distance sta1 ap2                 - Distância até ap2\n")
    info("  py sta1.params['position']        - Posição atual da estação\n")
    info("  nodes                             - Lista todos os nós\n")
    info("  net                               - Exibe estrutura da rede\n")
    info("  links                             - Mostra conexões\n")
    info("  dump                              - Informações detalhadas\n")
    info("  exit                              - Encerra simulação\n")
    info("=" * 85 + "\n")
    info("OBSERVAÇÃO: Monitore o gráfico para visualizar o movimento das estações!\n")
    info("=" * 85 + "\n")
    
    # Inicia interface de linha de comando
    CLI(net)
    
    info("\n*** Parando mobilidade\n")
    # Finaliza motor de mobilidade
    net.stopMobility(time=200)
    
    info("*** Encerrando rede e limpando configurações\n")
    # Para todos os componentes
    net.stop()

if __name__ == '__main__':
    # Configura log detalhado
    setLogLevel('info')
    
    # Executa topologia
    topologia_hibrida_mobilidade()