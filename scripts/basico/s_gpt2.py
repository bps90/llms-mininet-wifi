#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mininet-WiFi: 2 estações (Wi-Fi) + 1 AP + 1 controlador SDN
Objetivo: sta1 e sta2 associados ao ap1 e comunicando-se entre si.
"""

from mininet.log import setLogLevel, info
from mininet.node import Controller
from mininet.cli import CLI

from mn_wifi.net import Mininet_wifi
from mn_wifi.node import OVSKernelAP
from mn_wifi.link import wmediumd
from mn_wifi.wmediumdConnector import interference


def topology():
    # Cria a rede Mininet-WiFi com modelo de rádio (interferência) para maior realismo
    net = Mininet_wifi(
        controller=Controller,
        accessPoint=OVSKernelAP,
        link=wmediumd,
        wmediumd_mode=interference
    )

    info("\n*** Criando nós (controlador, AP e estações)\n")

    # Controlador SDN (ativo)
    c0 = net.addController("c0", controller=Controller, ip="127.0.0.1", port=6633)

    # Ponto de acesso (AP) com SSID e canal definidos
    ap1 = net.addAccessPoint(
        "ap1",
        ssid="ssid-ap1",
        mode="g",
        channel="1",
        position="50,50,0"
    )

    # Duas estações sem fio com IPs no mesmo /24
    sta1 = net.addStation("sta1", ip="10.0.0.1/24", position="40,50,0")
    sta2 = net.addStation("sta2", ip="10.0.0.2/24", position="60,50,0")

    info("\n*** Configurando propagação e nós Wi-Fi\n")
    # Modelo de propagação (padrão comum em exemplos do Mininet-WiFi)
    net.setPropagationModel(model="logDistance", exp=4)

    info("\n*** Configurando nós Wi-Fi (associação sta<->ap)\n")
    net.configureWifiNodes()

    info("\n*** Construindo a rede\n")
    net.build()

    info("\n*** Iniciando controlador e AP\n")
    c0.start()
    ap1.start([c0])  # AP controlado pelo controlador SDN

    info("\n*** Teste básico de conectividade (ping entre todos)\n")
    net.pingAll()

    info("\n*** Teste de desempenho (iperf TCP: sta1 -> sta2)\n")
    # iperf entre as estações (uma como server, outra como client)
    net.iperf((sta1, sta2))

    info("\n*** Abrindo CLI para inspeção manual (opcional)\n")
    CLI(net)

    info("\n*** Encerrando a rede\n")
    net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    topology()
