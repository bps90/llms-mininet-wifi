#!/usr/bin/python

from mininet.node import Controller, OVSKernelSwitch
from mininet.log import setLogLevel, info
from mn_wifi.net import MininetWiFi
from mn_wifi.node import Station, AccessPoint
from mn_wifi.cli import CLI
from mn_wifi.link import wlan
from mn_wifi.propagationModels import propagationModel

def topology():
    "Cria uma topologia com 2 APs (canais 1 e 6), 4 estações, 1 switch central e 1 controlador SDN."

    # Inicializa a rede Mininet-WiFi com suporte a switch OVS e controlador
    net = MininetWiFi(controller=Controller, switch=OVSKernelSwitch)

    info("*** Adicionando o Controlador SDN (c0)\n")
    c0 = net.addController('c0')

    info("*** Adicionando o Switch Central (s1)\n")
    s1 = net.addSwitch('s1')

    info("*** Adicionando Pontos de Acesso (APs)\n")
    # AP1 opera no canal 1 e o AP2 no canal 6 para evitar interferência
    ap1 = net.addAccessPoint('ap1', ssid='ssid-ap1', mode='g', 
                             channel='1', position='30,50,0')
    ap2 = net.addAccessPoint('ap2', ssid='ssid-ap2', mode='g', 
                             channel='6', position='70,50,0')

    info("*** Adicionando Estações e definindo distribuição espacial\n")
    # Estações próximas ao AP1
    sta1 = net.addStation('sta1', ip='10.0.0.1/8', position='20,45,0')
    sta2 = net.addStation('sta2', ip='10.0.0.2/8', position='25,55,0')
    
    # Estações próximas ao AP2
    sta3 = net.addStation('sta3', ip='10.0.0.3/8', position='75,45,0')
    sta4 = net.addStation('sta4', ip='10.0.0.4/8', position='80,55,0')

    info("*** Configurando o modelo de propagação\n")
    net.setPropagationModel(model='logDistance', exp=3)

    info("*** Estabelecendo ligações cabeadas (APs ao Switch)\n")
    # Interliga os APs ao switch central s1
    net.addLink(ap1, s1)
    net.addLink(ap2, s1)

    info("*** Configurando parâmetros dos nós Wi-Fi\n")
    net.configureWifiNodes()

    info("*** Iniciando a rede e componentes\n")
    net.build()
    c0.start()
    s1.start([c0])
    ap1.start([c0])
    ap2.start([c0])

    info("*** Testando conectividade entre todas as estações (pingAll)\n")
    net.pingAll()

    info("*** Abrindo CLI do Mininet-WiFi para testes manuais\n")
    CLI(net)

    info("*** Encerrando a simulação\n")
    net.stop()

if __name__ == '__main__':
    # Define o nível de log para detalhamento da execução no terminal
    setLogLevel('info')
    topology()