#!/usr/bin/python

"""
Topologia Mininet-WiFi: Rede híbrida com mobilidade de estações
Autor: Script gerado para simulação de rede sem fio com handover
Componentes:
- 6 estações sem fio (sta1 a sta6) com suporte à mobilidade
- 2 pontos de acesso (ap1, ap2) com áreas de cobertura sobrepostas
- 1 switch central (s1) interligando os APs
- 1 controlador SDN (c0)
Funcionalidades:
- Mobilidade das estações entre APs
- Handover automático
- Comunicação contínua durante movimentação
"""

# Importações necessárias do Mininet-WiFi
from mininet.node import Controller, OVSKernelSwitch
from mininet.log import setLogLevel, info
from mn_wifi.net import Mininet_wifi
from mn_wifi.node import OVSKernelAP
from mn_wifi.cli import CLI
from mn_wifi.link import wmediumd
from mn_wifi.wmediumdConnector import interference

def criar_topologia_com_mobilidade():
    """Função que cria topologia com suporte à mobilidade"""
    
    info("*** Inicializando rede Mininet-WiFi com mobilidade\n")
    # Cria rede com suporte a simulação de interferência
    net = Mininet_wifi(controller=Controller,
                       accessPoint=OVSKernelAP,
                       switch=OVSKernelSwitch,
                       link=wmediumd,
                       wmediumd_mode=interference)
    
    info("*** Adicionando controlador SDN\n")
    # Controlador centralizado para gerenciamento de fluxos
    c0 = net.addController('c0',
                           controller=Controller,
                           protocol='tcp',
                           port=6653)
    
    info("*** Adicionando switch central de interconexão\n")
    # Switch que conecta os pontos de acesso
    s1 = net.addSwitch('s1',
                       cls=OVSKernelSwitch,
                       protocols='OpenFlow13')
    
    info("*** Adicionando pontos de acesso com cobertura sobreposta\n")
    # Ponto de acesso 1 - zona oeste
    ap1 = net.addAccessPoint('ap1',
                             ssid='rede-movel',
                             mode='g',
                             channel='1',
                             position='30,50,0',
                             range=40)
    
    # Ponto de acesso 2 - zona leste com sobreposição
    ap2 = net.addAccessPoint('ap2',
                             ssid='rede-movel',
                             mode='g',
                             channel='6',
                             position='70,50,0',
                             range=40)
    
    info("*** Adicionando estações móveis\n")
    # Estações inicialmente próximas ao ap1
    sta1 = net.addStation('sta1',
                          ip='10.0.0.1/24',
                          mac='00:00:00:00:00:01',
                          position='20,40,0',
                          range=20)
    
    sta2 = net.addStation('sta2',
                          ip='10.0.0.2/24',
                          mac='00:00:00:00:00:02',
                          position='25,50,0',
                          range=20)
    
    sta3 = net.addStation('sta3',
                          ip='10.0.0.3/24',
                          mac='00:00:00:00:00:03',
                          position='30,60,0',
                          range=20)
    
    # Estações inicialmente próximas ao ap2
    sta4 = net.addStation('sta4',
                          ip='10.0.0.4/24',
                          mac='00:00:00:00:00:04',
                          position='70,60,0',
                          range=20)
    
    sta5 = net.addStation('sta5',
                          ip='10.0.0.5/24',
                          mac='00:00:00:00:00:05',
                          position='75,50,0',
                          range=20)
    
    sta6 = net.addStation('sta6',
                          ip='10.0.0.6/24',
                          mac='00:00:00:00:00:06',
                          position='80,40,0',
                          range=20)
    
    info("*** Configurando modelo de propagação realista\n")
    # Modelo que simula perda de sinal com a distância
    net.setPropagationModel(model="logDistance", exp=3.5)
    
    info("*** Aplicando configurações Wi-Fi\n")
    # Configura parâmetros sem fio de todos os nós
    net.configureWifiNodes()
    
    info("*** Criando links cabeados entre APs e switch\n")
    # Conecta ap1 ao switch com link de alta velocidade
    net.addLink(ap1, s1, bw=1000, delay='1ms')
    
    # Conecta ap2 ao switch com link de alta velocidade
    net.addLink(ap2, s1, bw=1000, delay='1ms')
    
    info("*** Habilitando visualização gráfica\n")
    # Exibe topologia em tempo real
    net.plotGraph(max_x=100, max_y=100)
    
    info("*** Construindo e iniciando a rede\n")
    # Constrói topologia completa
    net.build()
    
    # Inicia controlador
    c0.start()
    
    # Inicia switch
    s1.start([c0])
    
    # Inicia pontos de acesso
    ap1.start([c0])
    ap2.start([c0])
    
    info("*** Aguardando estabilização inicial\n")
    import time
    time.sleep(2)
    
    info("*** Configurando mobilidade das estações\n")
    # Define padrões de mobilidade para simular movimento realista
    
    # Mobilidade da sta1: movimento da esquerda para direita
    net.mobility(sta1, 'start', time=1)
    net.mobility(sta1, 'position', position='20,40,0', time=2)
    net.mobility(sta1, 'position', position='50,40,0', time=30)
    net.mobility(sta1, 'position', position='80,40,0', time=60)
    net.mobility(sta1, 'stop', time=61)
    
    # Mobilidade da sta2: movimento circular
    net.mobility(sta2, 'start', time=1)
    net.mobility(sta2, 'position', position='25,50,0', time=2)
    net.mobility(sta2, 'position', position='50,30,0', time=25)
    net.mobility(sta2, 'position', position='75,50,0', time=50)
    net.mobility(sta2, 'position', position='50,70,0', time=75)
    net.mobility(sta2, 'stop', time=76)
    
    # Mobilidade da sta3: movimento lento entre APs
    net.mobility(sta3, 'start', time=1)
    net.mobility(sta3, 'position', position='30,60,0', time=2)
    net.mobility(sta3, 'position', position='50,60,0', time=40)
    net.mobility(sta3, 'position', position='70,60,0', time=80)
    net.mobility(sta3, 'stop', time=81)
    
    # Mobilidade da sta4: movimento da direita para esquerda
    net.mobility(sta4, 'start', time=1)
    net.mobility(sta4, 'position', position='70,60,0', time=2)
    net.mobility(sta4, 'position', position='50,60,0', time=35)
    net.mobility(sta4, 'position', position='30,60,0', time=70)
    net.mobility(sta4, 'stop', time=71)
    
    # Mobilidade da sta5: movimento vertical
    net.mobility(sta5, 'start', time=1)
    net.mobility(sta5, 'position', position='75,50,0', time=2)
    net.mobility(sta5, 'position', position='75,30,0', time=30)
    net.mobility(sta5, 'position', position='75,70,0', time=60)
    net.mobility(sta5, 'stop', time=61)
    
    # Mobilidade da sta6: permanece relativamente estática
    net.mobility(sta6, 'start', time=1)
    net.mobility(sta6, 'position', position='80,40,0', time=2)
    net.mobility(sta6, 'position', position='75,45,0', time=50)
    net.mobility(sta6, 'stop', time=51)
    
    info("*** Iniciando simulação de mobilidade\n")
    # Inicia o motor de mobilidade
    net.startMobility(time=0)
    
    info("*** Testando conectividade inicial\n")
    # Testa ping entre todas as estações
    net.pingAll()
    
    info("\n*** Executando testes durante mobilidade\n")
    # Monitora conectividade durante movimento
    info("Iniciando monitoramento de handover...\n")
    
    # Aguarda para permitir algum movimento
    time.sleep(10)
    
    info("\n*** Testando conectividade após mobilidade parcial\n")
    net.pingAll()
    
    info("\n*** Testes de desempenho durante mobilidade\n")
    # Teste de largura de banda entre estações móveis
    info("Teste: sta1 <-> sta6 (em movimento)\n")
    net.iperf((sta1, sta6), seconds=5)
    
    info("\nTeste: sta2 <-> sta5 (em movimento)\n")
    net.iperf((sta2, sta5), seconds=5)
    
    info("\n" + "=" * 80 + "\n")
    info("*** REDE COM MOBILIDADE CONFIGURADA COM SUCESSO ***\n")
    info("=" * 80 + "\n")
    info("Configuração da Rede:\n")
    info("  • Controlador: c0 (OpenFlow)\n")
    info("  • Switch: s1 (interconexão dos APs)\n")
    info("  • AP1: SSID 'rede-movel', Canal 1, Posição (30,50,0), Alcance 40m\n")
    info("  • AP2: SSID 'rede-movel', Canal 6, Posição (70,50,0), Alcance 40m\n")
    info("  • 6 Estações móveis com padrões de movimento configurados\n")
    info("\nPadrões de Mobilidade:\n")
    info("  • sta1: Movimento horizontal (esquerda → direita)\n")
    info("  • sta2: Movimento circular pela área\n")
    info("  • sta3: Movimento lento entre APs\n")
    info("  • sta4: Movimento horizontal (direita → esquerda)\n")
    info("  • sta5: Movimento vertical\n")
    info("  • sta6: Movimento mínimo (quase estática)\n")
    info("\nRecursos da Simulação:\n")
    info("  ✓ Handover automático entre APs\n")
    info("  ✓ Mesmo SSID para roaming transparente\n")
    info("  ✓ Canais não interferentes (1 e 6)\n")
    info("  ✓ Áreas de cobertura sobrepostas\n")
    info("  ✓ Comunicação contínua durante mobilidade\n")
    info("=" * 80 + "\n")
    info("Comandos Disponíveis:\n")
    info("  pingall                      - Testa conectividade global\n")
    info("  sta1 ping sta4 -c 10         - Ping contínuo durante movimento\n")
    info("  iperf sta2 sta5              - Teste de banda durante mobilidade\n")
    info("  py sta1.params['rssi']       - Verifica intensidade do sinal\n")
    info("  py sta1.params['associatedTo']  - Verifica AP conectado\n")
    info("  distance sta1 ap1            - Calcula distância até AP\n")
    info("  distance sta1 ap2            - Calcula distância até AP\n")
    info("  nodes                        - Lista todos os nós\n")
    info("  net                          - Exibe topologia\n")
    info("  exit                         - Encerra simulação\n")
    info("=" * 80 + "\n")
    info("DICA: Observe o gráfico da rede para ver as estações se movendo!\n")
    info("=" * 80 + "\n")
    
    # Inicia CLI interativa
    CLI(net)
    
    info("\n*** Parando mobilidade e encerrando rede\n")
    # Para simulação de mobilidade
    net.stopMobility(time=100)
    
    # Encerra a rede
    net.stop()

if __name__ == '__main__':
    # Define nível de log detalhado
    setLogLevel('info')
    
    # Executa a topologia com mobilidade
    criar_topologia_com_mobilidade()