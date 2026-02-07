#!/usr/bin/python

"""
Script Mininet-WiFi: Rede Híbrida com Mobilidade e Roaming
Componentes:
- 1 Controlador (c0)
- 1 Switch Central (s1): Backbone cabeado
- 2 Access Points (ap1, ap2): Mesmo SSID para facilitar o roaming
- 6 Estações (sta1 a sta6): Com modelo de mobilidade 'RandomDirection'
Objetivo: Simular conectividade contínua enquanto estações se movem entre áreas de cobertura.
"""

from mininet.node import Controller, OVSSwitch
from mininet.log import setLogLevel, info
from mn_wifi.net import Mininet_wifi
from mn_wifi.node import OVSKernelAP
from mn_wifi.link import wmediumd

def topology():
    # Define o nível de log para detalhar o processo de associação e handover
    setLogLevel('info')

    info("*** Inicializando a rede Mininet-WiFi\n")
    # Utiliza wmediumd para uma simulação mais realista de interferência e sinal
    net = Mininet_wifi(controller=Controller, accessPoint=OVSKernelAP, 
                       switch=OVSSwitch, link=wmediumd)

    info("*** Adicionando o Controlador\n")
    c0 = net.addController('c0')

    info("*** Adicionando o Switch Central\n")
    s1 = net.addSwitch('s1')

    info("*** Adicionando os Access Points\n")
    # Configura APs com o mesmo SSID ('roaming-net') para permitir roaming transparente
    # Canais distintos (1 e 6) para minimizar interferência co-canal
    # ap1 cobre o lado esquerdo, ap2 o lado direito
    ap1 = net.addAccessPoint('ap1', ssid='roaming-net', mode='g', channel='1', 
                             position='30,50,0', range=40)
    ap2 = net.addAccessPoint('ap2', ssid='roaming-net', mode='g', channel='6', 
                             position='70,50,0', range=40)

    info("*** Adicionando as Estações com Mobilidade\n")
    # As estações são inicializadas em posições aleatórias ou fixas
    sta1 = net.addStation('sta1', ip='10.0.0.1/8', position='10,50,0')
    sta2 = net.addStation('sta2', ip='10.0.0.2/8', position='20,50,0')
    sta3 = net.addStation('sta3', ip='10.0.0.3/8', position='30,50,0')
    sta4 = net.addStation('sta4', ip='10.0.0.4/8', position='70,50,0')
    sta5 = net.addStation('sta5', ip='10.0.0.5/8', position='80,50,0')
    sta6 = net.addStation('sta6', ip='10.0.0.6/8', position='90,50,0')

    info("*** Configurando os nós Wi-Fi\n")
    net.configureWifiNodes()

    info("*** Criando os links cabeados (Backbone)\n")
    # Conecta os APs ao switch para permitir comunicação entre clientes de APs diferentes
    net.addLink(ap1, s1)
    net.addLink(ap2, s1)

    info("*** Habilitando Visualização e Mobilidade\n")
    # Define a área de plotagem do gráfico 2D (100x100 metros)
    net.plotGraph(max_x=100, max_y=100)

    # Configura o modelo de mobilidade RandomDirection
    # As estações se moverão aleatoriamente dentro da área definida
    net.startMobility(time=0, model='RandomDirection', 
                      max_x=100, max_y=100, min_v=0.5, max_v=0.8)

    info("*** Construindo a topologia\n")
    net.build()

    info("*** Iniciando Controlador, Switch e Access Points\n")
    c0.start()
    s1.start([c0])
    ap1.start([c0])
    ap2.start([c0])

    info("*** Aguardando estabilização da rede (5 segundos)...\n")
    import time
    time.sleep(5)

    info("*** Verificando a conectividade inicial (PingAll)\n")
    net.pingAll()

    info("*** Executando teste de largura de banda (Iperf) durante mobilidade\n")
    # Testa a comunicação entre sta1 (inicialmente no ap1) e sta6 (inicialmente no ap2)
    net.iperf((sta1, sta6))

    info("*** A rede continua rodando para simular a mobilidade.\n")
    info("*** Pressione Ctrl+C no terminal se estivesse em modo interativo.\n")
    
    # Pausa breve para permitir que a mobilidade ocorra antes de encerrar no script automático
    time.sleep(2)

    info("*** Finalizando a rede\n")
    net.stop()

if __name__ == '__main__':
    topology()