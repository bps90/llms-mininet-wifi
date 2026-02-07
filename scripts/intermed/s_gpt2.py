#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mininet-WiFi: 2 APs + 4 estações + 1 switch central + 1 controlador SDN
- ap1 atende sta1 e sta2
- ap2 atende sta3 e sta4
- ap1 e ap2 interligados por um switch central s1
- Controlador SDN ativo: c0
Inclui: configureWifiNodes(), pingAll(), iperf(), net.start()/net.stop()
"""

from mininet.log import setLogLevel, info
from mininet.node import Controller
from mininet.cli import CLI

from mn_wifi.net import Mininet_wifi
from mn_wifi.node import OVSKernelAP
from mn_wifi.link import wmediumd
from mn_wifi.wmediumdConnector import interference


def run():
    info("\n*** Criando rede Mininet-WiFi\n")
    net = Mininet_wifi(
        controller=Controller,
        accessPoint=OVSKernelAP,
        link=wmediumd,
        wmediumd_mode=interference
    )

    info("\n*** Adicionando controlador SDN (c0)\n")
    c0 = net.addController("c0", controller=Controller, ip="127.0.0.1", port=6633)

    info("\n*** Adicionando switch central (s1)\n")
    s1 = net.addSwitch("s1")

    info("\n*** Adicionando pontos de acesso (ap1, ap2)\n")
    # SSIDs distintos para forçar associação determinística das estações
    ap1 = net.addAccessPoint(
        "ap1",
        ssid="ssid-ap1",
        mode="g",
        channel="1",
        position="30,50,0"
    )
    ap2 = net.addAccessPoint(
        "ap2",
        ssid="ssid-ap2",
        mode="g",
        channel="6",
        position="70,50,0"
    )

    info("\n*** Adicionando estações (sta1..sta4)\n")
    # sta1/sta2 próximos de ap1; sta3/sta4 próximos de ap2
    sta1 = net.addStation("sta1", ip="10.0.0.1/24", position="20,45,0")
    sta2 = net.addStation("sta2", ip="10.0.0.2/24", position="20,55,0")
    sta3 = net.addStation("sta3", ip="10.0.0.3/24", position="80,45,0")
    sta4 = net.addStation("sta4", ip="10.0.0.4/24", position="80,55,0")

    info("\n*** Configurando modelo de propagação\n")
    net.setPropagationModel(model="logDistance", exp=4)

    info("\n*** Configurando nós Wi-Fi (associação sta<->ap)\n")
    net.configureWifiNodes()

    info("\n*** Ligando APs ao switch central (backhaul cabeado)\n")
    # Interligação L2: ap1 <-> s1 e ap2 <-> s1
    net.addLink(ap1, s1)
    net.addLink(ap2, s1)

    info("\n*** Construindo e iniciando rede\n")
    net.build()

    info("\n*** Iniciando controlador e elementos SDN\n")
    c0.start()
    ap1.start([c0])
    ap2.start([c0])

    info("\n*** Teste de conectividade (pingAll)\n")
    net.pingAll()

    info("\n*** Teste de desempenho (iperf TCP: sta1 -> sta3)\n")
    net.iperf((sta1, sta3))

    info("\n*** CLI para inspeção (opcional)\n")
    CLI(net)

    info("\n*** Encerrando rede\n")
    net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    run()
