#!/usr/bin/env python

"""
Topologia híbrida Mininet-WiFi com mobilidade:
- 6 estações sem fio: sta1 a sta6
- 2 pontos de acesso Wi-Fi: ap1, ap2
- 1 switch intermediário: s1
- 1 controlador SDN remoto: c0

Características:
- APs conectados ao switch s1
- Estações inicialmente distribuídas de forma equilibrada (3 em cada AP)
- IPs atribuídos automaticamente pelo Mininet-WiFi
- APs em canais diferentes (1 e 11), com alcance de 40m
- Mobilidade configurada com net.mobility(), definindo posições iniciais e finais
"""

from mn_wifi.net import Mininet_wifi
from mn_wifi.node import OVSKernelAP
from mn_wifi.cli import CLI
from mininet.node import RemoteController, OVSKernelSwitch
from mininet.log import setLogLevel, info


def topology():
    "Cria e executa a topologia híbrida com 2 APs, 6 estações, 1 switch e 1 controlador remoto."

    # Criação da rede base utilizando Mininet-WiFi
    net = Mininet_wifi(controller=RemoteController,
                       accessPoint=OVSKernelAP,
                       switch=OVSKernelSwitch)

    info('*** Criando nós (estações, APs, switch e controlador)\n')
    # Estações Wi-Fi (endereços IP automáticos; posições iniciais próximas aos APs)
    # Inicialmente, sta1–sta3 próximas ao ap1; sta4–sta6 próximas ao ap2
    sta1 = net.addStation('sta1', position='10,20,0')
    sta2 = net.addStation('sta2', position='15,18,0')
    sta3 = net.addStation('sta3', position='20,22,0')

    sta4 = net.addStation('sta4', position='80,20,0')
    sta5 = net.addStation('sta5', position='85,18,0')
    sta6 = net.addStation('sta6', position='90,22,0')

    # Pontos de acesso Wi-Fi em canais diferentes (não interferentes) e alcance de 40m
    ap1 = net.addAccessPoint(
        'ap1',
        ssid='ap1-ssid',
        mode='g',
        channel='1',        # Canal 1
        position='25,30,0',
        range=40            # Alcance em metros
    )

    ap2 = net.addAccessPoint(
        'ap2',
        ssid='ap2-ssid',
        mode='g',
        channel='11',       # Canal 11
        position='75,30,0',
        range=40
    )

    # Switch intermediário integrando os APs
    s1 = net.addSwitch('s1')

    # Controlador SDN remoto (por exemplo, Ryu/ONOS/OpenDaylight em 127.0.0.1:6653)
    c0 = net.addController(
        'c0',
        controller=RemoteController,
        ip='127.0.0.1',
        port=6653
    )

    info('*** Configurando nós Wi-Fi (parâmetros físicos)\n')
    # Aplica parâmetros físicos e de rádio às interfaces sem fio
    net.configureWifiNodes()

    info('*** Criando links Wi-Fi iniciais (associação equilibrada sta <-> ap)\n')
    # Estações inicialmente associadas de forma equilibrada:
    # ap1: sta1, sta2, sta3
    net.addLink(ap1, sta1)
    net.addLink(ap1, sta2)
    net.addLink(ap1, sta3)

    # ap2: sta4, sta5, sta6
    net.addLink(ap2, sta4)
    net.addLink(ap2, sta5)
    net.addLink(ap2, sta6)

    info('*** Criando links cabeados (APs <-> switch)\n')
    # Parte cabeada: cada AP conectado ao switch central
    net.addLink(ap1, s1)
    net.addLink(ap2, s1)

    info('*** Construindo e iniciando a rede\n')
    net.build()            # Constrói a topologia
    c0.start()             # Inicia o controlador SDN remoto

    # Inicia o switch e associa ao controlador
    s1.start([c0])

    # Inicia os APs e associa ao controlador
    ap1.start([c0])
    ap2.start([c0])

    info('*** Configurando mobilidade das estações com net.mobility()\n')
    # Mobilidade baseada em eventos (posições iniciais e finais, com tempos distintos)
    # Janela de mobilidade global
    net.startMobility(time=0)

    # Estações inicialmente próximas ao ap1 se deslocam em direção ao ap2
    net.mobility(sta1, 'start', time=1, position='10,20,0')
    net.mobility(sta1, 'stop',  time=20, position='70,20,0')

    net.mobility(sta2, 'start', time=2, position='15,18,0')
    net.mobility(sta2, 'stop',  time=22, position='72,18,0')

    net.mobility(sta3, 'start', time=3, position='20,22,0')
    net.mobility(sta3, 'stop',  time=24, position='74,22,0')

    # Estações inicialmente próximas ao ap2 se deslocam em direção ao ap1
    net.mobility(sta4, 'start', time=4, position='80,20,0')
    net.mobility(sta4, 'stop',  time=21, position='30,20,0')

    net.mobility(sta5, 'start', time=5, position='85,18,0')
    net.mobility(sta5, 'stop',  time=23, position='32,18,0')

    net.mobility(sta6, 'start', time=6, position='90,22,0')
    net.mobility(sta6, 'stop',  time=25, position='34,22,0')

    net.stopMobility(time=30)

    info('*** Testando conectividade com pingAll()\n')
    # Teste de conectividade entre todos os nós
    net.pingAll()

    info('*** CLI interativa (digite exit para encerrar)\n')
    # Na CLI é possível inspecionar associações, mobilidade e rotas
    CLI(net)

    info('*** Encerrando a rede\n')
    net.stop()             # Finaliza a simulação e libera recursos


if __name__ == '__main__':
    setLogLevel('info')
    topology()
