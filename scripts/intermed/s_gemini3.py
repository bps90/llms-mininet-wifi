#!/usr/bin/python

from mininet.node import Controller, OVSKernelSwitch
from mininet.log import setLogLevel, info
from mn_wifi.net import MininetWiFi
from mn_wifi.node import Station, AccessPoint
from mn_wifi.cli import CLI
from mn_wifi.link import wlan
from mn_wifi.propagationModels import propagationModel

def topology():
    "Cria uma topologia com 2 APs, 4 estações, 1 switch central e 1 controlador."

    net = MininetWiFi(controller=Controller, switch=OVSKernelSwitch)

    info("*** Adicionando o Controlador SDN\n")
    c0 = net.addController('c0')

    info("*** Adicionando o Switch Central (Cabelado)\n")
    s1 = net.addSwitch('s1')

    info("*** Adicionando Pontos de Acesso (APs)\n")
    # AP1 posicionado à esquerda e AP2 à direita
    ap1 = net.addAccessPoint('ap1', ssid='ssid-ap1', mode='g', channel='1', position='30,50,0')
    ap2 = net.addAccessPoint('ap2', ssid='ssid-ap2', mode='g', channel='6', position='70,50,0')

    info("*** Adicionando Estações (Stations)\n")
    # Estações para o AP1 (sta1 e sta2)
    sta1 = net.addStation('sta1', ip='10.0.0.1/8', position='20,40,0')
    sta2 = net.addStation('sta2', ip='10.0.0.2/8', position='20,60,0')
    
    # Estações para o AP2 (sta3 e sta4)
    sta3 = net.addStation('sta3', ip='10.0.0.3/8', position='80,40,0')
    sta4 = net.addStation('sta4', ip='10.0.0.4/8', position='80,60,0')

    info("*** Configurando o modelo de propagação\n")
    net.setPropagationModel(model='logDistance', exp=3)

    info("*** Criando links cabeados (APs para o Switch)\n")
    # Interliga os pontos de acesso ao switch central
    net.addLink(ap1, s1)
    net.addLink(ap2, s1)

    info("*** Configurando nós Wi-Fi\n")
    net.configureWifiNodes()

    info("*** Iniciando a rede\n")
    net.build()
    c0.start()
    s1.start([c0])
    ap1.start([c0])
    ap2.start([c0])

    info("*** Testando conectividade global (pingAll)\n")
    # Realiza o teste para garantir que estações em APs diferentes se comunicam via Switch
    net.pingAll()

    info("*** Iniciando CLI para interação\n")
    CLI(net)

    info("*** Encerrando a emulação\n")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topology()