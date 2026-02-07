#!/usr/bin/env python

"""
Topologia híbrida Mininet-WiFi com mobilidade:
- 6 estações sem fio: sta1 a sta6
- 2 pontos de acesso Wi-Fi: ap1, ap2
- 1 switch central: s1
- 1 controlador SDN: c0

Requisitos:
- Estações distribuídas entre ap1 e ap2
- Possibilidade de mobilidade entre áreas de cobertura
- Comunicação entre todas as estações (APs interligados via switch)
"""

from mn_wifi.net import Mininet_wifi
from mn_wifi.node import Controller, OVSKernelAP
from mn_wifi.cli import CLI
from mininet.node import OVSKernelSwitch
from mininet.log import setLogLevel, info


def topology():
    "Cria e executa a topologia híbrida com 2 APs, 6 estações, 1 switch e 1 controlador."

    # Criação da rede base utilizando Mininet-WiFi
    net = Mininet_wifi(controller=Controller,
                       accessPoint=OVSKernelAP,
                       switch=OVSKernelSwitch)

    info('*** Criando nós (estações, APs, switch e controlador)\n')
    # Estações Wi-Fi com IPs na mesma sub-rede
    # Inicialmente, 3 estações próximas de cada AP (distribuição espacial)
    sta1 = net.addStation('sta1', ip='10.0.0.1/24', position='10,25,0')
    sta2 = net.addStation('sta2', ip='10.0.0.2/24', position='15,20,0')
    sta3 = net.addStation('sta3', ip='10.0.0.3/24', position='20,15,0')

    sta4 = net.addStation('sta4', ip='10.0.0.4/24', position='80,25,0')
    sta5 = net.addStation('sta5', ip='10.0.0.5/24', position='85,20,0')
    sta6 = net.addStation('sta6', ip='10.0.0.6/24', position='90,15,0')

    # Pontos de acesso Wi-Fi em canais não interferentes
    ap1 = net.addAccessPoint(
        'ap1',
        ssid='ssid-ap1',
        mode='g',
        channel='1',        # Canal 1
        position='25,30,0',
        range=40            # Alcance em metros
    )

    ap2 = net.addAccessPoint(
        'ap2',
        ssid='ssid-ap2',
        mode='g',
        channel='6',        # Canal 6 (menos interferência com canal 1)
        position='75,30,0',
        range=40
    )

    # Switch central interligando os APs (parte cabeada da rede)
    s1 = net.addSwitch('s1')

    # Controlador SDN padrão
    c0 = net.addController('c0')

    info('*** Configurando nós Wi-Fi\n')
    # Aplica parâmetros físicos e de rádio às interfaces sem fio
    net.configureWifiNodes()

    info('*** Configurando modelo de mobilidade\n')
    # Define um modelo de mobilidade aleatória para as estações, permitindo
    # que se desloquem pelo cenário e alternem entre as áreas de cobertura
    net.setMobilityModel(
        time=0,
        model='RandomWayPoint',
        max_x=100,  # Limite do cenário em X
        max_y=60,   # Limite do cenário em Y
        min_v=0.5,  # Velocidade mínima (m/s)
        max_v=2.0   # Velocidade máxima (m/s)
    )

    info('*** Criando links cabeados (APs <-> switch)\n')
    # Parte cabeada: cada AP conectado ao switch central
    net.addLink(ap1, s1)
    net.addLink(ap2, s1)

    # Observação:
    # Não criamos links explícitos entre estações e APs.
    # A associação Wi-Fi é feita automaticamente com base na posição e alcance,
    # permitindo que as estações alternem entre ap1 e ap2 conforme se movimentam.

    info('*** Construindo e iniciando a rede\n')
    net.build()            # Constrói a topologia
    c0.start()             # Inicia o controlador SDN

    # Inicia o switch e associa ao controlador
    s1.start([c0])

    # Inicia os APs e associa ao controlador
    ap1.start([c0])
    ap2.start([c0])

    info('*** Testando conectividade entre todas as estações com pingAll()\n')
    # Teste de conectividade entre todos os nós (todas as estações devem se comunicar)
    net.pingAll()

    info('*** Testando throughput entre sta1 (próxima de ap1) e sta6 (próxima de ap2) com iperf()\n')
    # Teste de desempenho TCP entre estações em áreas de cobertura diferentes
    net.iperf((sta1, sta6))

    info('*** CLI interativa (digite exit para encerrar)\n')
    # A partir da CLI, é possível inspecionar associações, movimentação e rotas
    CLI(net)

    info('*** Encerrando a rede\n')
    net.stop()             # Finaliza a simulação e libera recursos


if __name__ == '__main__':
    setLogLevel('info')
    topology()
