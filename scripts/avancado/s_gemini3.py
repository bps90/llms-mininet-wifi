#!/usr/bin/python

from mininet.node import Controller, OVSKernelSwitch
from mininet.log import setLogLevel, info
from mn_wifi.net import MininetWiFi
from mn_wifi.node import Station, AccessPoint
from mn_wifi.cli import CLI
from mn_wifi.link import wlan
from mn_wifi.propagationModels import propagationModel

def topology():
    "Cria uma rede híbrida com 2 APs, 6 estações, mobilidade e controle SDN."

    # Inicializa a rede Mininet-WiFi
    net = MininetWiFi(controller=Controller, switch=OVSKernelSwitch)

    info("*** Adicionando o Controlador SDN (c0)\n")
    c0 = net.addController('c0')

    info("*** Adicionando o Switch Central de Backbone (s1)\n")
    s1 = net.addSwitch('s1')

    info("*** Adicionando Pontos de acesso (APs)\n")
    # Ambos os APs compartilham o mesmo SSID para facilitar o roaming/handover
    ap1 = net.addAccessPoint('ap1', ssid='mobility-topo', mode='g', 
                             channel='1', position='30,50,0')
    ap2 = net.addAccessPoint('ap2', ssid='mobility-topo', mode='g', 
                             channel='6', position='70,50,0')

    info("*** Adicionando 6 Estações (sta1 a sta6)\n")
    # Estações inicialmente posicionadas próximas ao ap1
    sta1 = net.addStation('sta1', ip='10.0.0.1/8', position='20,40,0')
    sta2 = net.addStation('sta2', ip='10.0.0.2/8', position='25,40,0')
    sta3 = net.addStation('sta3', ip='10.0.0.3/8', position='30,40,0')
    
    # Estações inicialmente posicionadas próximas ao ap2
    sta4 = net.addStation('sta4', ip='10.0.0.4/8', position='70,60,0')
    sta5 = net.addStation('sta5', ip='10.0.0.5/8', position='75,60,0')
    sta6 = net.addStation('sta6', ip='10.0.0.6/8', position='80,60,0')

    info("*** Configurando o modelo de propagação\n")
    net.setPropagationModel(model='logDistance', exp=3)

    info("*** Estabelecendo links de infraestrutura (APs para Switch)\n")
    net.addLink(ap1, s1)
    net.addLink(ap2, s1)

    info("*** Configurando parâmetros Wi-Fi e Mobilidade\n")
    net.configureWifiNodes()

    # Define o modelo de mobilidade Random Walk para simular movimento constante
    # As estações se moverão dentro de uma área de 100x100 metros
    net.setMobilityModel(time=0, model='RandomWalk', 
                         max_x=100, max_y=100, min_v=0.5, max_v=2.0)

    info("*** Iniciando a rede\n")
    net.build()
    c0.start()
    s1.start([c0])
    ap1.start([c0])
    ap2.start([c0])

    info("*** Testando conectividade inicial (pingAll)\n")
    net.pingAll()

    info("*** A rede está operacional com mobilidade ativa.\n")
    info("*** Você pode observar as estações mudando de AP no terminal.\n")
    
    # Abre o CLI para interação e testes manuais (ex: iperf)
    CLI(net)

    info("*** Encerrando a simulação\n")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topology()