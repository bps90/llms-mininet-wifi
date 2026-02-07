#!/usr/bin/python

"""
Script Mininet-WiFi: Topologia com Alcance Definido
Componentes:
- 1 Controlador (c0)
- 1 Access Point (ap1): Canal 1, Alcance 30m
- 2 Estações (sta1, sta2)
Objetivo: Validar conectividade com restrição de alcance de sinal.
"""

from mininet.log import setLogLevel, info
from mn_wifi.net import Mininet_wifi
from mn_wifi.node import OVSKernelAP
from mininet.node import Controller

def topology():
    # Define o nível de log para exibir o status da execução
    setLogLevel('info')

    info("*** Inicializando a rede Mininet-WiFi\n")
    # Cria a rede utilizando o Access Point baseado em Open vSwitch (Kernel)
    net = Mininet_wifi(controller=Controller, accessPoint=OVSKernelAP)

    info("*** Adicionando o Controlador SDN\n")
    c0 = net.addController('c0')

    info("*** Adicionando o Access Point\n")
    # Configura o ap1 com SSID 'mininet-wifi', modo 802.11g, canal 1
    # O parâmetro 'range=30' define visualmente e logicamente o alcance máximo de 30 metros
    # Posição centralizada em (50, 50, 0)
    ap1 = net.addAccessPoint('ap1', ssid='simple-topo', mode='g', channel='1',
                             range=30, position='50,50,0')

    info("*** Adicionando as Estações\n")
    # Posiciona as estações dentro do raio de 30 metros do AP
    # sta1 em (35, 50, 0) -> Distância de 15m do AP
    sta1 = net.addStation('sta1', ip='10.0.0.1/8', position='35,50,0')
    
    # sta2 em (65, 50, 0) -> Distância de 15m do AP
    sta2 = net.addStation('sta2', ip='10.0.0.2/8', position='65,50,0')

    info("*** Configurando os nós Wi-Fi\n")
    # Aplica configurações de rádio e propagação
    net.configureWifiNodes()

    info("*** Construindo a topologia\n")
    net.build()

    info("*** Iniciando o Controlador e o Access Point\n")
    c0.start()
    ap1.start([c0])

    info("*** Testando a conectividade (PingAll)\n")
    # Realiza ping entre todos os nós para confirmar que estão dentro do alcance
    net.pingAll()

    info("*** Executando teste de largura de banda (Iperf)\n")
    # Teste simples de TCP entre sta1 (servidor) e sta2 (cliente)
    net.iperf((sta1, sta2))

    info("*** Finalizando a rede\n")
    net.stop()

if __name__ == '__main__':
    topology()