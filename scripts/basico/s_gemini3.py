#!/usr/bin/python

from mininet.node import Controller
from mininet.log import setLogLevel, info
from mn_wifi.net import MininetWiFi
from mn_wifi.node import Station, AccessPoint
from mn_wifi.cli import CLI
from mn_wifi.link import wlan
from mn_wifi.propagationModels import propagationModel

def topology():
    "Cria uma rede Wi-Fi com 2 estações, 1 AP e um controlador SDN."

    net = MininetWiFi(controller=Controller)

    info("*** Adicionando estações (Stations)\n")
    # Define IP e posição estática (x,y,z) para as estações
    sta1 = net.addStation('sta1', ip='10.0.0.1/8', position='30,50,0')
    sta2 = net.addStation('sta2', ip='10.0.0.2/8', position='70,50,0')

    info("*** Adicionando Ponto de Acesso (Access Point)\n")
    # Configura o AP com um SSID específico, modo 802.11g e canal 1
    ap1 = net.addAccessPoint('ap1', ssid='mininet-wifi-topo',
                             mode='g', channel='1', position='50,50,0')

    info("*** Adicionando Controlador SDN\n")
    c0 = net.addController('c0')

    info("*** Configurando o modelo de propagação\n")
    net.setPropagationModel(model='logDistance', exp=3)

    info("*** Configurando nós Wi-Fi\n")
    net.configureWifiNodes()

    info("*** Iniciando a rede\n")
    net.build()
    c0.start()
    ap1.start([c0])

    info("*** Testando conectividade inicial (pingAll)\n")
    net.pingAll()

    info("*** Executando CLI para interação\n")
    CLI(net)

    info("*** Encerrando a rede\n")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topology()