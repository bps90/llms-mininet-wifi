#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mininet-WiFi: Topologia híbrida com mobilidade
- 2 APs Wi-Fi: ap1 (canal 1), ap2 (canal 11), ambos com range=40m
- 6 estações: sta1..sta6 (IP automático via net.setIpBase)
- 1 switch intermediário: s1 (integra o backhaul cabeado)
- 1 controlador SDN remoto: c0 (RemoteController)

Requisitos atendidos:
- addStation, addAccessPoint, addSwitch, addController (RemoteController)
- net.configureWifiNodes()
- APs conectados ao switch s1
- associação inicial equilibrada (3 estações por AP, via posições + SSIDs distintos)
- mobilidade via net.mobility() com tempos distintos (start/stop) e posições iniciais/finais
- rede inicia e encerra corretamente (net.start / net.stop)
"""

from mininet.log import setLogLevel, info
from mininet.node import RemoteController
from mininet.cli import CLI

from mn_wifi.net import Mininet_wifi
from mn_wifi.node import OVSKernelAP
from mn_wifi.link import wmediumd
from mn_wifi.wmediumdConnector import interference


def run():
    info("\n*** Criando a rede Mininet-WiFi\n")
    net = Mininet_wifi(
        controller=RemoteController,
        accessPoint=OVSKernelAP,
        link=wmediumd,
        wmediumd_mode=interference
    )

    info("\n*** Definindo base de IP (endereçamento automático)\n")
    # As estações receberão IPs automaticamente no formato 10.0.0.X/24
    net.setIpBase("10.0.0.0/24")

    info("\n*** Adicionando controlador SDN remoto (c0)\n")
    # Ajuste ip/port conforme seu controlador remoto (ex.: Ryu/ODL/ONOS)
    c0 = net.addController("c0", controller=RemoteController, ip="127.0.0.1", port=6633)

    info("\n*** Adicionando switch intermediário (s1)\n")
    s1 = net.addSwitch("s1")

    info("\n*** Adicionando APs (ap1, ap2) com canais distintos e alcance 40m\n")
    # SSIDs distintos ajudam a manter associação determinística por proximidade/alcance
    ap1 = net.addAccessPoint(
        "ap1",
        ssid="ssid-ap1",
        mode="g",
        channel="1",
        range=40,
        position="30,50,0"
    )
    ap2 = net.addAccessPoint(
        "ap2",
        ssid="ssid-ap2",
        mode="g",
        channel="11",
        range=40,
        position="90,50,0"
    )

    info("\n*** Adicionando estações (sta1..sta6) com associação inicial equilibrada\n")
    # 3 estações próximas de ap1 e 3 próximas de ap2
    sta1 = net.addStation("sta1", position="20,45,0")
    sta2 = net.addStation("sta2", position="20,55,0")
    sta3 = net.addStation("sta3", position="35,50,0")

    sta4 = net.addStation("sta4", position="100,45,0")
    sta5 = net.addStation("sta5", position="100,55,0")
    sta6 = net.addStation("sta6", position="85,50,0")

    info("\n*** Configurando modelo de propagação e parâmetros físicos\n")
    net.setPropagationModel(model="logDistance", exp=4)

    info("\n*** Aplicando configurações Wi-Fi (associação inicial por alcance/posição)\n")
    net.configureWifiNodes()

    info("\n*** Interligando APs ao switch intermediário (s1)\n")
    net.addLink(ap1, s1)
    net.addLink(ap2, s1)

    info("\n*** Construindo e iniciando a rede\n")
    net.build()

    info("\n*** Iniciando controlador e APs (SDN ativo)\n")
    c0.start()
    ap1.start([c0])
    ap2.start([c0])

    info("\n*** Teste inicial de conectividade (pingAll)\n")
    net.pingAll()

    info("\n*** Configurando mobilidade (movimento entre áreas de cobertura)\n")
    # Movimentações cruzadas (algumas estações migram de ap1->ap2 e outras de ap2->ap1)
    # Formato: net.mobility(node, 'start'/'stop', time=<t>, position='x,y,z')

    # sta1: ap1 -> ap2
    net.mobility(sta1, "start", time=1,  position="20,45,0")
    net.mobility(sta1, "stop",  time=14, position="95,45,0")

    # sta2: ap1 -> ap2
    net.mobility(sta2, "start", time=2,  position="20,55,0")
    net.mobility(sta2, "stop",  time=16, position="95,55,0")

    # sta4: ap2 -> ap1
    net.mobility(sta4, "start", time=3,  position="100,45,0")
    net.mobility(sta4, "stop",  time=18, position="25,45,0")

    # sta5: ap2 -> ap1
    net.mobility(sta5, "start", time=4,  position="100,55,0")
    net.mobility(sta5, "stop",  time=20, position="25,55,0")

    # sta3 e sta6 como “âncoras” (mantêm-se próximos de seus APs originais)
    net.mobility(sta3, "start", time=1,  position="35,50,0")
    net.mobility(sta3, "stop",  time=21, position="35,50,0")

    net.mobility(sta6, "start", time=1,  position="85,50,0")
    net.mobility(sta6, "stop",  time=21, position="85,50,0")

    # Inicia e finaliza o mecanismo de mobilidade baseado em tempo
    net.startMobility(time=0)
    net.stopMobility(time=22)

    info("\n*** Teste de conectividade após mobilidade (pingAll)\n")
    net.pingAll()

    info("\n*** CLI para inspeção (opcional)\n")
    # Exemplos úteis na CLI:
    # - sta1 iw dev sta1-wlan0 link
    # - py sta1.params.get('associatedTo')
    CLI(net)

    info("\n*** Encerrando a rede\n")
    net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    run()
