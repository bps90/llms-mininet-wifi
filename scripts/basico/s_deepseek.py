#!/usr/bin/env python3
"""
Script Mininet-WiFi: Topologia simples com Wi-Fi e controlador SDN
Duas estações sem fio conectadas a um ponto de acesso
Autor: Engenheiro de Redes - Mininet-WiFi Specialist
"""

from mininet.node import Controller, OVSKernelSwitch
from mininet.log import setLogLevel, info
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.link import wmediumd
from mn_wifi.wmediumdConnector import interference

def run_topology():
    """Cria e executa a topologia de rede com duas estações Wi-Fi"""
    
    # Inicializa logging para debug
    setLogLevel('info')
    
    # Cria a rede Mininet-WiFi
    net = Mininet_wifi(
        controller=Controller,
        switch=OVSKernelSwitch,
        accessPoint=OVSKernelSwitch,
        link=wmediumd,
        wmediumd_mode=interference,
        noise_threshold=-91,
        fading_coefficient=0
    )
    
    info("*** Criando nós da rede\n")
    
    # Adiciona controlador SDN
    info("*** Adicionando controlador SDN\n")
    c0 = net.addController('c0', controller=Controller, ip='127.0.0.1', port=6653)
    
    # Adiciona ponto de acesso Wi-Fi
    info("*** Adicionando ponto de acesso\n")
    ap1 = net.addAccessPoint('ap1',
                             ssid='mininet-wifi',
                             mode='g',
                             channel=1,
                             position='50,50,0',
                             range=30)
    
    # Adiciona estações Wi-Fi (clientes)
    info("*** Adicionando estações Wi-Fi\n")
    sta1 = net.addStation('sta1',
                          ip='10.0.0.1/24',
                          position='30,70,0',
                          range=20)
    
    sta2 = net.addStation('sta2',
                          ip='10.0.0.2/24',
                          position='70,70,0',
                          range=20)
    
    info("*** Configurando modelo de propagação Wi-Fi\n")
    # Configura os parâmetros de propagação para os nós Wi-Fi
    net.configureWifiNodes()
    
    info("*** Configurando mobilidade\n")
    # Configura o modelo de mobilidade (nesse caso, estático)
    net.setMobilityModel(time=0, model='static')
    
    info("*** Criando enlaces\n")
    # Conecta AP ao controlador (interface de gerenciamento)
    net.addLink(ap1, c0)
    
    info("*** Inicializando rede\n")
    # Inicia os componentes da rede
    net.build()
    
    # Inicia controlador
    c0.start()
    
    # Inicia ponto de acesso (agora como switch OpenFlow)
    ap1.start([c0])
    
    info("*** Configurando tabelas ARP\n")
    # Configura ARP para as estações
    sta1.cmd('arp -s 10.0.0.2 00:00:00:00:00:02')
    sta2.cmd('arp -s 10.0.0.1 00:00:00:00:00:01')
    
    info("*** Testando conectividade básica\n")
    # Teste de ping entre as estações
    result = net.ping([sta1, sta2], timeout=1)
    info(f"*** Resultado do ping: {result}%\n")
    
    if result < 100:
        info("*** Atenção: Conectividade não ótima. Verificando configuração...\n")
    
    info("*** Testando largura de banda com iperf\n")
    # Teste de throughput entre as estações
    net.iperf([sta1, sta2], seconds=5)
    
    info("*** Executando CLI interativa\n")
    # Inicia CLI para comandos manuais
    CLI(net)
    
    info("*** Encerrando rede\n")
    # Para e limpa a rede
    net.stop()

if __name__ == '__main__':
    # Ponto de entrada do script
    run_topology()