#!/usr/bin/python

"""
Script Mininet-WiFi: Topologia básica com 2 estações sem fio
Componentes: 2 estações, 1 ponto de acesso, 1 controlador SDN
Objetivo: Demonstrar comunicação básica entre estações via Wi-Fi
"""

from mininet.net import Mininet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mn_wifi.net import Mininet_wifi
from mn_wifi.node import OVSKernelAP
from mn_wifi.cli import CLI
from mn_wifi.link import wmediumd
from mn_wifi.wmediumdConnector import interference

def topology():
    """Cria a topologia de rede sem fio"""
    
    # Inicializa a rede Mininet-WiFi
    net = Mininet_wifi(controller=Controller, accessPoint=OVSKernelAP)
    
    info("*** Criando nós da rede\n")
    
    # Adiciona controlador SDN
    c0 = net.addController('c0', controller=Controller, port=6653)
    
    # Adiciona ponto de acesso com configurações básicas
    ap1 = net.addAccessPoint('ap1', ssid='rede-wifi', mode='g', channel='1',
                             position='50,50,0', range=30)
    
    # Adiciona estações sem fio com posições específicas
    sta1 = net.addStation('sta1', ip='10.0.0.1/24', position='30,50,0')
    sta2 = net.addStation('sta2', ip='10.0.0.2/24', position='70,50,0')
    
    info("*** Configurando propagação do sinal Wi-Fi\n")
    net.setPropagationModel(model="logDistance", exp=4)
    
    info("*** Configurando nós Wi-Fi\n")
    net.configureWifiNodes()
    
    info("*** Criando links entre estações e ponto de acesso\n")
    # As estações se conectam automaticamente ao AP devido à proximidade
    
    info("*** Iniciando a rede\n")
    net.build()
    c0.start()
    ap1.start([c0])
    
    info("*** Testando conectividade entre estações\n")
    net.pingAll()
    
    info("*** Executando CLI do Mininet-WiFi\n")
    info("*** Use 'pingall' para testar conectividade\n")
    info("*** Use 'iperf sta1 sta2' para testar largura de banda\n")
    info("*** Use 'exit' para encerrar\n")
    CLI(net)
    
    info("*** Encerrando a rede\n")
    net.stop()

if __name__ == '__main__':
    # Define nível de log para informações detalhadas
    setLogLevel('info')
    
    # Executa a topologia
    topology()