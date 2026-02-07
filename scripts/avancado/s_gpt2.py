#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mininet-WiFi: Rede híbrida com mobilidade
- 2 APs (ap1, ap2) + 6 estações (sta1..sta6) + 1 switch central (s1) + 1 controlador SDN (c0)
- Estações distribuídas entre APs, com mobilidade (handover) entre áreas de cobertura
- Objetivo: comunicação fim-a-fim entre todas as estações, mesmo durante/apos movimentação

Observações:
- O backhaul cabeado (ap1/ap2 -> s1) garante conectividade L2 entre APs e, portanto, entre estações
- A associação/roaming das estações é gerida pelo Mininet-WiFi conforme posição + range + SSID
"""

from mininet.log import setLogLevel, info
from mininet.node import Controller
from mininet.cli import CLI

from mn_wifi.net import Mininet_wifi
from mn_wifi.node import OVSKernelAP
from mn_wifi.link import wmediumd
from mn_wifi.wmediumdConnector import interference


def run():
    info("\n*** Criando a rede Mininet-WiFi\n")
    net = Mininet_wifi(
        controller=Controller,
        accessPoint=OVSKernelAP,
        link=wmediumd,
        wmediumd_mode=interference
    )

    info("\n*** Adicionando controlador SDN (c0)\n")
    c0 = net.addController("c0", controller=Controller, ip="127.0.0.1", port=6633)

    info("\n*** Adicionando switch central (s1) para backhaul cabeado\n")
    s1 = net.addSwitch("s1")

    info("\n*** Adicionando APs (canais não interferentes) e definindo alcance\n")
    # range define o raio aproximado de cobertura; posicione APs separados para forçar handover com mobilidade
    ap1 = net.addAccessPoint(
        "ap1",
        ssid="ssid-ap1",
        mode="g",
        channel="1",
        range=35,
        position="30,50,0"
    )
    ap2 = net.addAccessPoint(
        "ap2",
        ssid="ssid-ap2",
        mode="g",
        channel="6",
        range=35,
        position="90,50,0"
    )

    info("\n*** Adicionando 6 estações e posicionando-as em áreas iniciais de cobertura\n")
    # sta1..sta3 iniciam próximos de ap1; sta4..sta6 iniciam próximos de ap2
    sta1 = net.addStation("sta1", ip="10.0.0.1/24", position="20,45,0")
    sta2 = net.addStation("sta2", ip="10.0.0.2/24", position="20,55,0")
    sta3 = net.addStation("sta3", ip="10.0.0.3/24", position="35,50,0")

    sta4 = net.addStation("sta4", ip="10.0.0.4/24", position="100,45,0")
    sta5 = net.addStation("sta5", ip="10.0.0.5/24", position="100,55,0")
    sta6 = net.addStation("sta6", ip="10.0.0.6/24", position="85,50,0")

    info("\n*** Configurando modelo de propagação\n")
    net.setPropagationModel(model="logDistance", exp=4)

    info("\n*** Aplicando configurações Wi-Fi (associação inicial)\n")
    net.configureWifiNodes()

    info("\n*** Interligando APs ao switch central (backhaul)\n")
    net.addLink(ap1, s1)
    net.addLink(ap2, s1)

    info("\n*** Construindo e iniciando rede\n")
    net.build()

    info("\n*** Iniciando controlador e APs (SDN ativo)\n")
    c0.start()
    ap1.start([c0])
    ap2.start([c0])

    info("\n*** Teste inicial de conectividade (pingAll)\n")
    net.pingAll()

    info("\n*** Habilitando mobilidade (handover entre APs)\n")
    # Inicia modo de mobilidade com eventos definidos no tempo
    net.mobility(sta1, "start", time=1, position="20,45,0")
    net.mobility(sta1, "stop",  time=12, position="95,45,0")  # sta1 cruza para perto do ap2

    net.mobility(sta2, "start", time=2, position="20,55,0")
    net.mobility(sta2, "stop",  time=14, position="95,55,0")  # sta2 cruza para ap2

    net.mobility(sta4, "start", time=3, position="100,45,0")
    net.mobility(sta4, "stop",  time=16, position="25,45,0")  # sta4 cruza para perto do ap1

    net.mobility(sta5, "start", time=4, position="100,55,0")
    net.mobility(sta5, "stop",  time=18, position="25,55,0")  # sta5 cruza para ap1

    # Mantemos sta3 e sta6 como “âncoras” em seus domínios para validar comunicação contínua
    net.mobility(sta3, "start", time=1, position="35,50,0")
    net.mobility(sta3, "stop",  time=20, position="35,50,0")

    net.mobility(sta6, "start", time=1, position="85,50,0")
    net.mobility(sta6, "stop",  time=20, position="85,50,0")

    # Inicia execução da mobilidade conforme eventos acima
    net.startMobility(time=0)
    net.stopMobility(time=21)

    info("\n*** Teste pós-mobilidade (pingAll)\n")
    net.pingAll()

    info("\n*** Teste de desempenho pós-mobilidade (iperf TCP: sta1 -> sta5)\n")
    net.iperf((sta1, sta5))

    info("\n*** CLI para inspeção (opcional)\n")
    # Dicas na CLI:
    # - 'py sta1.params["associatedTo"]' para ver associação atual
    # - 'sta1 iw dev sta1-wlan0 link' para verificar o AP associado
    CLI(net)

    info("\n*** Encerrando a rede\n")
    net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    run()
