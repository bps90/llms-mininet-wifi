#!/usr/bin/python

"""
Script Mininet-WiFi: Topologia com Switch Central e Múltiplos APs
Componentes:
- 1 Controlador (c0)
- 1 Switch (s1): Interliga os APs
- 2 Access Points (ap1, ap2): Em canais diferentes para evitar interferência
- 4 Estações (sta1, sta2 no ap1; sta3, sta4 no ap2)
Objetivo: Validar comunicação entre células Wi-Fi distintas através de backbone cabeado.
"""

from mininet.node import Controller, OVSSwitch
from mininet.log import setLogLevel, info
from mn_wifi.net import Mininet_wifi
from mn_wifi.node import OVSKernelAP

def topology():
    # Define o nível de log para visualizar o progresso da simulação
    setLogLevel('info')

    info("*** Inicializando a rede Mininet-WiFi\n")
    # Inicializa a rede definindo o switch padrão e o AP padrão
    net = Mininet_wifi(controller=Controller, accessPoint=OVSKernelAP, switch=OVSSwitch)

    info("*** Adicionando o Controlador\n")
    c0 = net.addController('c0')

    info("*** Adicionando o Switch Central\n")
    # O switch s1 servirá como backbone cabeado entre os APs
    s1 = net.addSwitch('s1')

    info("*** Adicionando os Access Points\n")
    # ap1 configurado no lado esquerdo (posição 30,50) com SSID 'wifi-net-1'
    ap1 = net.addAccessPoint('ap1', ssid='wifi-net-1', mode='g', channel='1', position='30,50,0')
    
    # ap2 configurado no lado direito (posição 70,50) com SSID 'wifi-net-2'
    # Utiliza canal 6 para reduzir interferência simulada com ap1
    ap2 = net.addAccessPoint('ap2', ssid='wifi-net-2', mode='g', channel='6', position='70,50,0')

    info("*** Adicionando as Estações\n")
    # sta1 e sta2 associadas explicitamente ao SSID do ap1
    sta1 = net.addStation('sta1', ip='10.0.0.1/8', position='20,50,0', ssid='wifi-net-1')
    sta2 = net.addStation('sta2', ip='10.0.0.2/8', position='40,50,0', ssid='wifi-net-1')

    # sta3 e sta4 associadas explicitamente ao SSID do ap2
    sta3 = net.addStation('sta3', ip='10.0.0.3/8', position='60,50,0', ssid='wifi-net-2')
    sta4 = net.addStation('sta4', ip='10.0.0.4/8', position='80,50,0', ssid='wifi-net-2')

    info("*** Configurando os nós Wi-Fi\n")
    net.configureWifiNodes()

    info("*** Criando os links cabeados (Backbone)\n")
    # Conecta ap1 ao switch s1
    net.addLink(ap1, s1)
    # Conecta ap2 ao switch s1
    net.addLink(ap2, s1)

    info("*** Construindo a topologia\n")
    net.build()

    info("*** Iniciando Controlador, Switch e Access Points\n")
    c0.start()
    s1.start([c0])
    ap1.start([c0])
    ap2.start([c0])

    info("*** Verificando a conectividade (PingAll)\n")
    # O teste deve ter sucesso entre todas as estações (ex: sta1 pinga sta4 via ap1->s1->ap2)
    net.pingAll()

    info("*** Testando largura de banda entre células diferentes\n")
    # Teste de desempenho entre sta1 (no ap1) e sta4 (no ap2)
    net.iperf((sta1, sta4))

    info("*** Finalizando a rede\n")
    net.stop()

if __name__ == '__main__':
    topology()