#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mininet-WiFi: Topologia simples
- 2 estações Wi-Fi: sta1, sta2
- 1 ponto de acesso: ap1 (canal 1, alcance ~30m)
- 1 controlador SDN padrão: c0
Requisitos: nós associados ao AP via Wi-Fi e conectividade entre as estações.
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
    # wmediumd (interference) dá maior fidelidade ao enlace sem fio
    net = Mininet_wifi(
        controller=Controller,
        accessPoint=OVSKernelAP,
        link=wmediumd,
        wmediumd_mode=interference
    )

    info("\n*** Adicionando controlador SDN (c0)\n")
    c0 = net.addController("c0", controller=Controller, ip="127.0.0.1", port=6633)

    info("\n*** Adicionando ponto de acesso (ap1) - canal 1 e alcance 30m\n")
    # range=30 define o raio aproximado de cobertura (em metros) no modelo do Mininet-WiFi
    ap1 = net.addAccessPoint(
        "ap1",
        ssid="ssid-ap1",
        mode="g",
        channel="1",
        range=30,
        position="50,50,0"
    )

    info("\n*** Adicionando estações (sta1, sta2)\n")
    sta1 = net.addStation("sta1", ip="10.0.0.1/24", position="40,50,0")
    sta2 = net.addStation("sta2", ip="10.0.0.2/24", position="60,50,0")

    info("\n*** Configurando modelo de propagação\n")
    net.setPropagationModel(model="logDistance", exp=4)

    info("\n*** Habilitando e configurando parâmetros Wi-Fi\n")
    net.configureWifiNodes()

    info("\n*** Construindo a rede\n")
    net.build()

    info("\n*** Iniciando controlador e AP (SDN ativo no AP)\n")
    c0.start()
    ap1.start([c0])

    # Observação importante:
    # Em Mininet-WiFi, a associação Wi-Fi sta<->ap é gerida pelo configureWifiNodes()
    # com base em SSID/alcance/posição, então não é necessário criar link explícito.
    # Ainda assim, garantimos a associação via SSID e cobertura (range=30).

    info("\n*** Testando conectividade (pingAll)\n")
    net.pingAll()

    info("\n*** Abrindo CLI (opcional)\n")
    CLI(net)

    info("\n*** Encerrando rede\n")
    net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    run()
