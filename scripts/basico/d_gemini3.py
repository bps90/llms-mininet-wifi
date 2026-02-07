#!/usr/bin/python

from mininet.node import Controller
from mininet.log import setLogLevel, info
from mn_wifi.net import MininetWiFi
from mn_wifi.node import Station, AccessPoint
from mn_wifi.cli import CLI
from mn_wifi.link import wlan
from mn_wifi.propagationModels import propagationModel

def simple_topology():
    "Cria uma topologia Wi-Fi com 2 estações, 1 AP (alcance 30m) e 1 controlador SDN."

    # Inicializa a rede Mininet-WiFi com um controlador padrão
    net = MininetWiFi(controller=Controller)

    info("*** Adicionando Controlador SDN\n")
    c0 = net.addController('c0')

    info("*** Adicionando Ponto de Acesso (AP)\n")
    # Configurado no canal 1, com alcance (range) de 30 metros
    ap1 = net.addAccessPoint('ap1', ssid='wifi-network', mode='g', 
                             channel='1', range=30, position='50,50,0')

    info("*** Adicionando Estações (Stations)\n")
    # Posicionadas a 10 metros do AP para garantir conectividade dentro do raio de 30m
    sta1 = net.addStation('sta1', ip='10.0.0.1/8', position='40,50,0')
    sta2 = net.addStation('sta2', ip='10.0.0.2/8', position='60,50,0')

    info("*** Configurando o modelo de propagação\n")
    # Define o modelo de propagação para que o parâmetro 'range' seja respeitado
    net.setPropagationModel(model='logDistance', exp=3)

    info("*** Configurando nós Wi-Fi\n")
    # Aplica as configurações de parâmetros sem fio aos nós
    net.configureWifiNodes()

    info("*** Iniciando a rede\n")
    net.build()
    c0.start()
    ap1.start([c0])

    info("*** Validando conectividade entre estações\n")
    # Realiza um teste de ping automático para verificar a tabela de fluxos do controlador
    net.pingAll()

    info("*** Iniciando CLI do Mininet-WiFi\n")
    CLI(net)

    info("*** Encerrando a rede\n")
    net.stop()

if __name__ == '__main__':
    # Define o nível de log como 'info' para visualizar detalhes da execução no terminal
    setLogLevel('info')
    simple_topology()