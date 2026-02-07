#!/usr/bin/python

"""
Script Mininet-WiFi: Topologia com Múltiplos APs e Switch Central
Componentes:
- 1 Controlador (c0)
- 1 Switch (s1)
- 2 Access Points (ap1, ap2): Configurados em canais não sobrepostos (1 e 6)
- 4 Estações (sta1 a sta4): Associadas estaticamente aos APs designados
Objetivo: Simular roaming ou interconexão de células Wi-Fi via backbone Ethernet.
"""

from mininet.node import Controller, OVSSwitch
from mininet.log import setLogLevel, info
from mn_wifi.net import Mininet_wifi
from mn_wifi.node import OVSKernelAP

def topology():
    # Define o nível de log para 'info' para visualizar os detalhes da execução
    setLogLevel('info')

    info("*** Inicializando a rede Mininet-WiFi\n")
    # Cria a rede especificando o tipo de AP e Switch
    net = Mininet_wifi(controller=Controller, accessPoint=OVSKernelAP, switch=OVSSwitch)

    info("*** Adicionando o Controlador SDN\n")
    c0 = net.addController('c0')

    info("*** Adicionando o Switch Central\n")
    s1 = net.addSwitch('s1')

    info("*** Adicionando os Access Points\n")
    # AP1: Lado esquerdo, Canal 1 (2.4GHz), SSID específico para segregar sta1/sta2
    ap1 = net.addAccessPoint('ap1', ssid='rede-oeste', mode='g', channel='1', 
                             position='30,50,0')

    # AP2: Lado direito, Canal 6 (2.4GHz - não interfere com canal 1), SSID para sta3/sta4
    ap2 = net.addAccessPoint('ap2', ssid='rede-leste', mode='g', channel='6', 
                             position='70,50,0')

    info("*** Adicionando as Estações\n")
    # sta1 e sta2 associadas ao ap1 ('rede-oeste')
    sta1 = net.addStation('sta1', ip='10.0.0.1/8', position='20,60,0', ssid='rede-oeste')
    sta2 = net.addStation('sta2', ip='10.0.0.2/8', position='40,60,0', ssid='rede-oeste')

    # sta3 e sta4 associadas ao ap2 ('rede-leste')
    sta3 = net.addStation('sta3', ip='10.0.0.3/8', position='60,60,0', ssid='rede-leste')
    sta4 = net.addStation('sta4', ip='10.0.0.4/8', position='80,60,0', ssid='rede-leste')

    info("*** Configurando os nós Wi-Fi\n")
    # Aplica configurações de rádio e propagação
    net.configureWifiNodes()

    info("*** Criando os links cabeados (Backbone)\n")
    # Conecta os APs ao switch central s1
    net.addLink(ap1, s1)
    net.addLink(ap2, s1)

    info("*** Construindo a topologia\n")
    net.build()

    info("*** Iniciando Controlador, Switch e Access Points\n")
    c0.start()
    s1.start([c0])
    ap1.start([c0])
    ap2.start([c0])

    info("*** Verificando a conectividade (PingAll)\n")
    # Testa a conectividade entre todas as estações.
    # O tráfego entre sta1 e sta4, por exemplo, passará por: sta1->ap1->s1->ap2->sta4
    net.pingAll()

    info("*** Executando teste de largura de banda (Iperf)\n")
    # Teste de desempenho entre uma estação no ap1 e uma estação no ap2
    net.iperf((sta1, sta4))

    info("*** Finalizando a rede\n")
    net.stop()

if __name__ == '__main__':
    topology()