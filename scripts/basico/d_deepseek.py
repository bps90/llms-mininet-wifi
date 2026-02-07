#!/usr/bin/env python3
"""
Topologia Mininet-WiFi: Duas estações Wi-Fi conectadas a um ponto de acesso
Canal: 1, Alcance: 30 metros, Controlador SDN: c0
"""

from mininet.node import Controller, OVSKernelSwitch
from mininet.log import setLogLevel, info
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.link import wmediumd
from mn_wifi.wmediumdConnector import interference

def create_topology():
    """Cria topologia com duas estações Wi-Fi e um ponto de acesso"""
    
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
        autoAssociation=False  # Desativa associação automática para maior controle
    )
    
    info("*** Adicionando controlador SDN\n")
    # Adiciona controlador OpenFlow
    c0 = net.addController('c0', 
                           controller=Controller, 
                           ip='127.0.0.1', 
                           protocol='tcp',
                           port=6653)
    
    info("*** Adicionando ponto de acesso\n")
    # Adiciona AP com especificações fornecidas
    ap1 = net.addAccessPoint('ap1',
                             ssid='mininet-wifi-ssid',
                             mode='g',          # 802.11g
                             channel=1,         # Canal especificado
                             position='50,50,0',
                             range=30,          # Alcance especificado (30m)
                             failMode='standalone',
                             datapath='kernel')
    
    info("*** Adicionando estações Wi-Fi\n")
    # Adiciona primeira estação Wi-Fi
    sta1 = net.addStation('sta1',
                          mac='00:00:00:00:00:01',
                          ip='10.0.0.1/24',
                          position='30,60,0',
                          range=25,
                          authmode='open',      # Autenticação aberta
                          encrypt='wep',        # Criptografia WEP (simples)
                          passwd='mininet123')
    
    # Adiciona segunda estação Wi-Fi
    sta2 = net.addStation('sta2',
                          mac='00:00:00:00:00:02',
                          ip='10.0.0.2/24',
                          position='70,60,0',
                          range=25,
                          authmode='open',
                          encrypt='wep',
                          passwd='mininet123')
    
    info("*** Configurando parâmetros Wi-Fi\n")
    # Configura modelo de propagação para todos os nós Wi-Fi
    net.configureWifiNodes()
    
    info("*** Configurando mobilidade\n")
    # Configura modelo de mobilidade estática
    net.setMobilityModel(time=0, model='static')
    
    info("*** Criando enlaces lógicos\n")
    # Conexão implícita via Wi-Fi (estações se conectam ao AP pelo SSID)
    # O Mininet-WiFi gerencia automaticamente as associações
    
    info("*** Construindo topologia\n")
    # Constrói todos os elementos da rede
    net.build()
    
    info("*** Iniciando controlador\n")
    # Inicia controlador SDN
    c0.start()
    
    info("*** Iniciando ponto de acesso\n")
    # Inicia AP como switch OpenFlow conectado ao controlador
    ap1.start([c0])
    
    info("*** Configurando associações Wi-Fi\n")
    # Associa manualmente as estações ao AP
    sta1.setMaster('ap1')
    sta2.setMaster('ap1')
    
    info("*** Verificando conexões Wi-Fi\n")
    # Verifica se as estações estão conectadas ao AP
    for sta in [sta1, sta2]:
        result = sta.cmd('iw dev %s-wlan0 link' % sta.name)
        if 'Connected' in result:
            info(f"*** {sta.name} conectado ao AP\n")
        else:
            info(f"*** {sta.name} NÃO conectado ao AP\n")
    
    info("*** Configurando tabelas ARP\n")
    # Configura entradas ARP estáticas para evitar problemas de descoberta
    sta1.cmd('arp -s 10.0.0.2 00:00:00:00:00:02')
    sta2.cmd('arp -s 10.0.0.1 00:00:00:00:00:01')
    
    info("*** Testando conectividade\n")
    # Testa ping entre as estações
    info("*** Ping de sta1 para sta2:\n")
    ping_result = sta1.cmd('ping -c 4 10.0.0.2')
    info(ping_result)
    
    # Verifica se houve sucesso no ping
    if '64 bytes from' in ping_result:
        info("*** ✓ Conectividade Wi-Fi estabelecida com sucesso!\n")
    else:
        info("*** ✗ Problemas na conectividade Wi-Fi\n")
    
    info("*** Iniciando CLI interativa\n")
    info("*** Comandos úteis:\n")
    info("***   'nodes' - lista todos os nós\n")
    info("***   'net' - mostra conexões da rede\n")
    info("***   'sta1 iwconfig' - mostra configuração Wi-Fi da sta1\n")
    info("***   'sta1 ping 10.0.0.2' - testa conectividade\n")
    info("***   'exit' - encerra a simulação\n\n")
    
    # Inicia interface de linha de comandos
    CLI(net)
    
    info("*** Encerrando rede\n")
    # Para todos os processos e limpa a rede
    net.stop()

if __name__ == '__main__':
    # Ponto de entrada principal
    create_topology()