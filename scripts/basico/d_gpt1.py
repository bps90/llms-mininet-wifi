#!/usr/bin/env python

"""
Topologia simples no Mininet-WiFi:
- 2 estações sem fio: sta1, sta2
- 1 ponto de acesso Wi-Fi: ap1
- 1 controlador SDN padrão: c0

Requisitos:
- ap1 no canal 1
- alcance (range) de 30 metros
- sta1 e sta2 conectadas ao ap1 via Wi-Fi
"""

from mn_wifi.net import Mininet_wifi
from mn_wifi.node import Controller, OVSKernelAP
from mn_wifi.cli import CLI
from mininet.log import setLogLevel, info


def topology():
    "Cria e executa a topologia Wi-Fi simples com 2 estações, 1 AP e 1 controlador."

    # Cria a rede base utilizando Mininet-WiFi
    net = Mininet_wifi(controller=Controller, accessPoint=OVSKernelAP)

    info('*** Criando nós (estações, AP e controlador)\n')
    # Criação das estações Wi-Fi (endereços IP na mesma sub-rede)
    sta1 = net.addStation('sta1', ip='10.0.0.1/24', position='10,20,0')
    sta2 = net.addStation('sta2', ip='10.0.0.2/24', position='20,20,0')

    # Criação do ponto de acesso Wi-Fi
    ap1 = net.addAccessPoint(
        'ap1',
        ssid='ssid-ap1',
        mode='g',
        channel='1',     # Canal 1
        position='15,25,0',
        range=30         # Alcance de 30 metros
    )

    # Criação do controlador SDN padrão
    c0 = net.addController('c0')  # Controlador padrão (OVSController)

    info('*** Configurando nós Wi-Fi\n')
    # Configuração dos parâmetros físicos das interfaces sem fio
    net.configureWifiNodes()

    info('*** Criando links Wi-Fi (associação sta <-> ap)\n')
    # Links representam associação Wi-Fi entre estações e o AP
    net.addLink(ap1, sta1)
    net.addLink(ap1, sta2)

    info('*** Construindo e iniciando a rede\n')
    net.build()       # Constrói a topologia
    c0.start()        # Inicia o controlador
    ap1.start([c0])   # Associa o AP ao controlador

    info('*** Testando conectividade entre os nós com pingAll()\n')
    # Teste de conectividade básica entre todos os nós
    net.pingAll()

    info('*** CLI interativa (digite exit para encerrar)\n')
    # Interface de linha de comando do Mininet-WiFi (opcional)
    CLI(net)

    info('*** Encerrando a rede\n')
    # Finaliza a simulação e libera recursos
    net.stop()


if __name__ == '__main__':
    # Define nível de log e executa a função de topologia
    setLogLevel('info')
    topology()
