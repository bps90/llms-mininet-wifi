#!/usr/bin/env python

"""
Simulação simples no Mininet-WiFi:
- 2 estações Wi-Fi (sta1, sta2)
- 1 ponto de acesso (ap1)
- 1 controlador SDN (c0)
As estações se conectam ao AP via Wi-Fi e conseguem se comunicar entre si.
"""

from mn_wifi.net import Mininet_wifi
from mn_wifi.node import Controller, OVSKernelAP
from mn_wifi.cli import CLI
from mininet.log import setLogLevel, info


def topology():
    "Cria e executa a topologia Wi-Fi com 2 estações, 1 AP e 1 controlador."

    # Criação da rede baseando-se no Mininet-WiFi
    net = Mininet_wifi(controller=Controller, accessPoint=OVSKernelAP)

    info('*** Criando nós (estações, AP e controlador)\n')
    # Estaçõ​es Wi-Fi com endereços IP na mesma sub-rede
    sta1 = net.addStation('sta1', ip='10.0.0.1/24', position='10,20,0')
    sta2 = net.addStation('sta2', ip='10.0.0.2/24', position='20,20,0')

    # Ponto de acesso Wi-Fi
    ap1 = net.addAccessPoint(
        'ap1',
        ssid='ssid-ap1',
        mode='g',
        channel='1',
        position='15,25,0',
        range=40
    )

    # Controlador SDN
    c0 = net.addController('c0')  # Controlador padrão (OVS)

    info('*** Configurando nós Wi-Fi\n')
    # Aplica parâmetros físicos e de rádio às interfaces sem fio
    net.configureWifiNodes()

    info('*** Criando links Wi-Fi\n')
    # No Mininet-WiFi, addLink entre AP e estações representa associação Wi-Fi
    net.addLink(ap1, sta1)
    net.addLink(ap1, sta2)

    info('*** Iniciando a rede\n')
    net.build()           # Constrói a topologia
    c0.start()            # Inicia o controlador
    ap1.start([c0])       # Associa o AP ao controlador

    info('*** Testando conectividade com pingAll()\n')
    # Teste básico de conectividade entre todos os nós
    net.pingAll()

    info('*** Testando throughput entre sta1 e sta2 com iperf()\n')
    # Teste de desempenho TCP entre as duas estações
    net.iperf((sta1, sta2))

    info('*** Entrando no CLI (use exit para encerrar)\n')
    # Interface interativa para inspeção manual (opcional)
    CLI(net)

    info('*** Encerrando a rede\n')
    net.stop()            # Finaliza toda a simulação


if __name__ == '__main__':
    # Define nível de log e executa a topologia
    setLogLevel('info')
    topology()
