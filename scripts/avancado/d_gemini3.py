#!/usr/bin/python

from mininet.node import RemoteController, OVSKernelSwitch
from mininet.log import setLogLevel, info
from mn_wifi.net import MininetWiFi
from mn_wifi.node import Station, AccessPoint
from mn_wifi.cli import CLI
from mn_wifi.link import wlan
from mn_wifi.propagationModels import propagationModel

def topology():
    "Cria uma rede híbrida com mobilidade programada, 2 APs, 6 estações e switch central."

    # Inicializa a rede com suporte a controlador remoto e switch OVS
    net = MininetWiFi(controller=RemoteController, switch=OVSKernelSwitch)

    info("*** Adicionando o Controlador SDN Remoto (c0)\n")
    # Assume que o controlador está rodando localmente na porta padrão 6633
    c0 = net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6633)

    info("*** Adicionando o Switch de Integração (s1)\n")
    s1 = net.addSwitch('s1')

    info("*** Adicionando Pontos de Acesso (ap1 e ap2)\n")
    # Canais 1 e 11 para evitar interferência; Alcance de 40 metros
    ap1 = net.addAccessPoint('ap1', ssid='infra-net', mode='g', channel='1', 
                             range=40, position='40,50,0')
    ap2 = net.addAccessPoint('ap2', ssid='infra-net', mode='g', channel='11', 
                             range=40, position='100,50,0')

    info("*** Adicionando Estações (sta1 a sta6) com IPs automáticos\n")
    # Estações para o AP1
    sta1 = net.addStation('sta1', ip='10.0.0.1/8', position='30,45,0')
    sta2 = net.addStation('sta2', ip='10.0.0.2/8', position='35,50,0')
    sta3 = net.addStation('sta3', ip='10.0.0.3/8', position='30,55,0')
    
    # Estações para o AP2
    sta4 = net.addStation('sta4', ip='10.0.0.4/8', position='110,45,0')
    sta5 = net.addStation('sta5', ip='10.0.0.5/8', position='105,50,0')
    sta6 = net.addStation('sta6', ip='10.0.0.6/8', position='110,55,0')

    info("*** Configurando o modelo de propagação\n")
    net.setPropagationModel(model='logDistance', exp=3)

    info("*** Estabelecendo links cabeados (APs -> Switch)\n")
    net.addLink(ap1, s1)
    net.addLink(ap2, s1)

    info("*** Configurando nós Wi-Fi\n")
    net.configureWifiNodes()

    info("*** Definindo parâmetros de Mobilidade Programada\n")
    # sta1 se move do AP1 em direção ao AP2
    net.mobility(sta1, 'start', time=10, position='30,45,0')
    net.mobility(sta1, 'stop', time=30, position='110,45,0')
    
    # sta4 se move do AP2 em direção ao AP1
    net.mobility(sta4, 'start', time=15, position='110,45,0')
    net.mobility(sta4, 'stop', time=35, position='30,45,0')

    info("*** Iniciando a rede\n")
    net.build()
    c0.start()
    s1.start([c0])
    ap1.start([c0])
    ap2.start([c0])

    info("*** A rede está operacional. Iniciando CLI...\n")
    info("*** Nota: Certifique-se de que o seu controlador (Ryu/ONOS) esteja ativo.\n")
    
    # Ativa o gráfico para visualizar o movimento das estações
    net.plotGraph(max_x=160, max_y=100)

    CLI(net)

    info("*** Encerrando a emulação\n")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topology()