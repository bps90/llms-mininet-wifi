#!/usr/bin/env python3
"""
Topologia Mininet-WiFi: Rede com dois APs, quatro estações e switch central
Cada AP conecta duas estações, interligados por switch central com controlador SDN
"""

from mininet.node import Controller, OVSKernelSwitch
from mininet.log import setLogLevel, info
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.link import wmediumd
from mn_wifi.wmediumdConnector import interference

def create_multi_ap_topology():
    """Cria topologia com dois APs, quatro estações e switch central"""
    
    # Configura nível de log
    setLogLevel('info')
    
    info("*** Inicializando rede Mininet-WiFi\n")
    # Cria objeto da rede com suporte a interferência
    net = Mininet_wifi(
        controller=Controller,
        switch=OVSKernelSwitch,
        accessPoint=OVSKernelSwitch,
        link=wmediumd,
        wmediumd_mode=interference,
        noise_threshold=-91,
        fading_coefficient=0,
        autoAssociation=False
    )
    
    info("*** Adicionando controlador SDN\n")
    # Adiciona controlador OpenFlow
    c0 = net.addController('c0', 
                           controller=Controller, 
                           ip='127.0.0.1', 
                           protocol='tcp',
                           port=6653)
    
    info("*** Adicionando switch central\n")
    # Adiciona switch central que conectará os APs
    s1 = net.addSwitch('s1', 
                       cls=OVSKernelSwitch, 
                       protocols='OpenFlow13',
                       failMode='secure')
    
    info("*** Adicionando pontos de acesso\n")
    # Adiciona primeiro AP (canal 1 para evitar interferência)
    ap1 = net.addAccessPoint('ap1',
                             ssid='rede-wifi-1',
                             mode='g',
                             channel=1,
                             position='30,50,0',
                             range=35,
                             failMode='standalone',
                             datapath='kernel')
    
    # Adiciona segundo AP (canal 6 para evitar interferência)
    ap2 = net.addAccessPoint('ap2',
                             ssid='rede-wifi-2',
                             mode='g',
                             channel=6,
                             position='70,50,0',
                             range=35,
                             failMode='standalone',
                             datapath='kernel')
    
    info("*** Adicionando estações Wi-Fi\n")
    # Estações conectadas ao AP1
    sta1 = net.addStation('sta1',
                          mac='00:00:00:00:01:01',
                          ip='10.0.1.1/24',
                          position='20,80,0',
                          range=30,
                          authmode='open',
                          encrypt='none')
    
    sta2 = net.addStation('sta2',
                          mac='00:00:00:00:01:02',
                          ip='10.0.1.2/24',
                          position='40,80,0',
                          range=30,
                          authmode='open',
                          encrypt='none')
    
    # Estações conectadas ao AP2
    sta3 = net.addStation('sta3',
                          mac='00:00:00:00:02:01',
                          ip='10.0.2.1/24',
                          position='60,80,0',
                          range=30,
                          authmode='open',
                          encrypt='none')
    
    sta4 = net.addStation('sta4',
                          mac='00:00:00:00:02:02',
                          ip='10.0.2.2/24',
                          position='80,80,0',
                          range=30,
                          authmode='open',
                          encrypt='none')
    
    info("*** Configurando parâmetros Wi-Fi\n")
    # Configura modelo de propagação para todos os nós Wi-Fi
    net.configureWifiNodes()
    
    info("*** Configurando mobilidade\n")
    # Configura modelo de mobilidade estática
    net.setMobilityModel(time=0, model='static')
    
    info("*** Criando enlaces físicos\n")
    # Conecta APs ao switch central
    net.addLink(ap1, s1)
    net.addLink(ap2, s1)
    
    info("*** Construindo topologia\n")
    # Constrói todos os elementos da rede
    net.build()
    
    info("*** Iniciando controlador\n")
    # Inicia controlador SDN
    c0.start()
    
    info("*** Configurando switches\n")
    # Inicia switch central
    s1.start([c0])
    
    # Inicia pontos de acesso como switches OpenFlow
    ap1.start([c0])
    ap2.start([c0])
    
    info("*** Configurando associações Wi-Fi\n")
    # Associa estações aos APs correspondentes
    sta1.setMaster('ap1')
    sta2.setMaster('ap1')
    sta3.setMaster('ap2')
    sta4.setMaster('ap2')
    
    info("*** Configurando roteamento entre sub-redes\n")
    # Configura roteamento para permitir comunicação entre sub-redes
    ap1.cmd('sysctl -w net.ipv4.ip_forward=1')
    ap2.cmd('sysctl -w net.ipv4.ip_forward=1')
    s1.cmd('sysctl -w net.ipv4.ip_forward=1')
    
    # Configura rotas nas estações
    sta1.cmd('ip route add 10.0.2.0/24 via 10.0.1.254')
    sta2.cmd('ip route add 10.0.2.0/24 via 10.0.1.254')
    sta3.cmd('ip route add 10.0.1.0/24 via 10.0.2.254')
    sta4.cmd('ip route add 10.0.1.0/24 via 10.0.2.254')
    
    # Configura IPs nos APs para servir como gateways
    ap1.cmd('ifconfig ap1 10.0.1.254/24')
    ap2.cmd('ifconfig ap2 10.0.2.254/24')
    
    info("*** Configurando tabelas ARP\n")
    # Configura entradas ARP para facilitar comunicação
    sta1.cmd('arp -s 10.0.1.254 00:00:00:00:00:11')
    sta2.cmd('arp -s 10.0.1.254 00:00:00:00:00:11')
    sta3.cmd('arp -s 10.0.2.254 00:00:00:00:00:22')
    sta4.cmd('arp -s 10.0.2.254 00:00:00:00:00:22')
    
    info("*** Verificando conexões Wi-Fi\n")
    # Verifica associações Wi-Fi
    for sta, ap in [(sta1, 'ap1'), (sta2, 'ap1'), (sta3, 'ap2'), (sta4, 'ap2')]:
        result = sta.cmd('iw dev %s-wlan0 link' % sta.name)
        if 'Connected' in result:
            info(f"*** {sta.name} conectado ao {ap}\n")
        else:
            info(f"*** {sta.name} NÃO conectado ao {ap}\n")
    
    info("*** Testando conectividade básica\n")
    # Testa ping dentro da mesma sub-rede
    info("*** Teste 1: Ping dentro da mesma sub-rede (sta1 -> sta2)\n")
    result1 = sta1.cmd('ping -c 2 10.0.1.2')
    info(result1)
    
    info("*** Teste 2: Ping dentro da mesma sub-rede (sta3 -> sta4)\n")
    result2 = sta3.cmd('ping -c 2 10.0.2.2')
    info(result2)
    
    info("*** Teste 3: Ping entre sub-redes (sta1 -> sta3)\n")
    result3 = sta1.cmd('ping -c 2 10.0.2.1')
    info(result3)
    
    info("*** Teste 4: Ping entre sub-redes (sta2 -> sta4)\n")
    result4 = sta2.cmd('ping -c 2 10.0.2.2')
    info(result4)
    
    info("*** Testando conectividade completa com pingAll\n")
    # Teste de ping entre todos os hosts
    net.pingAll()
    
    info("*** Testando throughput com iperf\n")
    # Teste de throughput entre estações de APs diferentes
    info("*** Teste iperf: sta1 (AP1) -> sta3 (AP2)\n")
    sta1.cmd('iperf -s -u &')
    sta3.cmd('iperf -c 10.0.1.1 -u -b 2M -t 5')
    sta1.cmd('pkill -f iperf')
    
    info("*** Mostrando informações da topologia\n")
    info("*** Topologia criada com sucesso!\n")
    info("*** Estrutura da rede:\n")
    info("***   Controlador: c0 (127.0.0.1:6653)\n")
    info("***   Switch Central: s1\n")
    info("***   APs: ap1 (SSID: rede-wifi-1, Canal: 1), ap2 (SSID: rede-wifi-2, Canal: 6)\n")
    info("***   Estações: sta1,sta2 -> ap1 / sta3,sta4 -> ap2\n")
    info("***   Sub-redes: 10.0.1.0/24 (AP1), 10.0.2.0/24 (AP2)\n")
    
    info("*** Iniciando CLI interativa\n")
    info("*** Comandos úteis:\n")
    info("***   'nodes' - lista todos os nós\n")
    info("***   'net' - mostra conexões da rede\n")
    info("***   'dump' - mostra informações detalhadas\n")
    info("***   'sta1 ping 10.0.2.1' - testa conectividade entre APs\n")
    info("***   'exit' - encerra a simulação\n\n")
    
    # Inicia interface de linha de comandos
    CLI(net)
    
    info("*** Encerrando rede\n")
    # Para todos os processos e limpa a rede
    net.stop()

if __name__ == '__main__':
    # Ponto de entrada principal
    create_multi_ap_topology()