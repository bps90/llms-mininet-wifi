#!/usr/bin/env python

"""
Topologia Mininet-WiFi:
- 4 estações sem fio: sta1, sta2, sta3, sta4
- 2 pontos de acesso Wi-Fi: ap1, ap2
- 1 switch central: s1
- 1 controlador SDN: c0

Cada AP atende duas estações:
- ap1: sta1, sta2
- ap2: sta3, sta4

Os APs são interligados via switch central s1.
"""

from mn_wifi.net import Mininet_wifi
from mn_wifi.node import Controller, OVSKernelAP
from mn_wifi.cli import CLI
from mininet.node import OVSKernelSwitch
from mininet.log import setLogLevel, info


def topology():
    "Cria e executa a topologia com 2 APs, 4 estações, 1 switch e 1 controlador."

    # Cria a rede base utilizando Mininet-WiFi
    net = Mininet_wifi(controller=Controller,
                       accessPoint=OVSKernelAP,
                       switch=OVSKernelSwitch)

    info('*** Criando nós (estações, APs, switch e controlador)\n')
    # Estações Wi-Fi (endereços IP na mesma sub-rede)
    sta1 = net.addStation('sta1', ip='10.0.0.1/24', position='10,20,0')
    sta2 = net.addStation('sta2', ip='10.0.0.2/24', position='20,20,0')
    sta3 = net.addStation('sta3', ip='10.0.0.3/24', position='40,20,0')
    sta4 = net.addStation('sta4', ip='10.0.0.4/24', position='50,20,0')

    # Pontos de acesso Wi-Fi
    ap1 = net.addAccessPoint(
        'ap1',
        ssid='ssid-ap1',
        mode='g',
        channel='1',
        position='15,30,0',
        range=40
    )

    ap2 = net.addAccessPoint(
        'ap2',
        ssid='ssid-ap2',
        mode='g',
        channel='6',
        position='45,30,0',
        range=40
    )

    # Switch central
    s1 = net.addSwitch('s1')

    # Controlador SDN padrão (OVSController)
    c0 = net.addController('c0')

    info('*** Configurando nós Wi-Fi\n')
    # Aplica parâmetros físicos às interfaces sem fio
    net.configureWifiNodes()

    info('*** Criando links Wi-Fi (estações <-> APs)\n')
    # Estações associadas a ap1
    net.addLink(ap1, sta1)
    net.addLink(ap1, sta2)

    # Estações associadas a ap2
    net.addLink(ap2, sta3)
    net.addLink(ap2, sta4)

    info('*** Criando links cabeados (APs <-> switch)\n')
    # APs conectados ao switch central
    net.addLink(ap1, s1)
    net.addLink(ap2, s1)

    info('*** Construindo e iniciando a rede\n')
    net.build()          # Constrói a topologia
    c0.start()           # Inicia o controlador SDN

    # Inicia o switch e associa ao controlador
    s1.start([c0])

    # Inicia os APs e associa ao controlador
    ap1.start([c0])
    ap2.start([c0])

    info('*** Testando conectividade com pingAll()\n')
    # Teste de conectividade entre todos os nós
    net.pingAll()

    info('*** Testando throughput entre sta1 e sta4 com iperf()\n')
    # Teste de desempenho TCP entre duas estações de APs diferentes
    net.iperf((sta1, sta4))

    info('*** CLI interativa (digite exit para encerrar)\n')
    CLI(net)

    info('*** Encerrando a rede\n')
    net.stop()           # Finaliza a simulação


if __name__ == '__main__':
    setLogLevel('info')
    topology()
