#!/usr/bin/env python3
"""
Topologia Mininet-WiFi: Rede com dois APs, quatro estações, switch central e controlador SDN
Canais não interferentes: AP1 canal 1, AP2 canal 6
Distribuição espacial definida para todas as estações
"""

from mininet.node import Controller, OVSKernelSwitch
from mininet.log import setLogLevel, info
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.link import wmediumd
from mn_wifi.wmediumdConnector import interference

def create_dual_ap_topology():
    """Cria topologia completa com dois APs, switch central e controlador SDN"""
    
    # Configura nível de log para informações detalhadas
    setLogLevel('info')
    
    info("*** Inicializando rede Mininet-WiFi com interferência\n")
    # Cria rede com modelo de interferência realista
    net = Mininet_wifi(
        controller=Controller,
        switch=OVSKernelSwitch,
        accessPoint=OVSKernelSwitch,
        link=wmediumd,
        wmediumd_mode=interference,
        noise_threshold=-91,
        fading_coefficient=3.0,  # Coeficiente de desvanecimento moderado
        autoAssociation=True,    # Associação automática baseada em sinal
        autoTxPower=True         # Potência de transmissão automática
    )
    
    info("*** Adicionando controlador SDN OpenFlow\n")
    # Adiciona controlador com configurações padrão
    c0 = net.addController('c0', 
                           controller=Controller, 
                           ip='127.0.0.1', 
                           protocol='tcp',
                           port=6653,
                           mac='00:00:00:00:00:01')
    
    info("*** Adicionando switch central\n")
    # Switch central que interconecta os APs
    s1 = net.addSwitch('s1', 
                       cls=OVSKernelSwitch, 
                       protocols='OpenFlow13',
                       failMode='standalone',
                       mac='00:00:00:00:00:10')
    
    info("*** Adicionando pontos de acesso com canais não interferentes\n")
    # Primeiro AP no canal 1 (2.412 GHz)
    ap1 = net.addAccessPoint('ap1',
                             ssid='Rede-AP1',
                             mode='g',            # 802.11g 54Mbps
                             channel=1,           # Canal não interferente 1
                             position='30,50,0',
                             range=40,            # Alcance de 40 metros
                             encrypt='wpa2',      # Segurança WPA2
                             passwd='senhaAP1',
                             mac='00:00:00:00:00:11',
                             datapath='kernel',
                             failMode='secure')
    
    # Segundo AP no canal 6 (2.437 GHz) - não interfere com canal 1
    ap2 = net.addAccessPoint('ap2',
                             ssid='Rede-AP2',
                             mode='g',
                             channel=6,           # Canal não interferente 6
                             position='70,50,0',
                             range=40,
                             encrypt='wpa2',
                             passwd='senhaAP2',
                             mac='00:00:00:00:00:12',
                             datapath='kernel',
                             failMode='secure')
    
    info("*** Adicionando estações sem fio com distribuição espacial\n")
    # Estações para AP1 - distribuídas à esquerda
    sta1 = net.addStation('sta1',
                          mac='00:00:00:00:01:01',
                          ip='192.168.1.101/24',
                          position='20,80,0',    # Posição superior esquerda
                          range=30,
                          authmode='wpa2',
                          encrypt='wpa2',
                          passwd='senhaAP1')
    
    sta2 = net.addStation('sta2',
                          mac='00:00:00:00:01:02',
                          ip='192.168.1.102/24',
                          position='40,20,0',    # Posição inferior esquerda
                          range=30,
                          authmode='wpa2',
                          encrypt='wpa2',
                          passwd='senhaAP1')
    
    # Estações para AP2 - distribuídas à direita
    sta3 = net.addStation('sta3',
                          mac='00:00:00:00:02:01',
                          ip='192.168.2.101/24',
                          position='60,80,0',    # Posição superior direita
                          range=30,
                          authmode='wpa2',
                          encrypt='wpa2',
                          passwd='senhaAP2')
    
    sta4 = net.addStation('sta4',
                          mac='00:00:00:00:02:02',
                          ip='192.168.2.102/24',
                          position='80,20,0',    # Posição inferior direita
                          range=30,
                          authmode='wpa2',
                          encrypt='wpa2',
                          passwd='senhaAP2')
    
    info("*** Configurando parâmetros de propagação Wi-Fi\n")
    # Aplica modelo de propagação para todos os nós sem fio
    net.configureWifiNodes()
    
    info("*** Configurando modelo de mobilidade estática\n")
    # Define mobilidade estática (posições fixas)
    net.setMobilityModel(time=0, 
                         model='static',
                         positions=None)  # Usa posições já definidas
    
    info("*** Criando enlaces físicos entre componentes\n")
    # Conexões cabeadas: APs → Switch Central
    net.addLink(ap1, s1, bw=100)  # 100 Mbps
    net.addLink(ap2, s1, bw=100)  # 100 Mbps
    
    info("*** Construindo toda a topologia de rede\n")
    # Constrói todos os componentes da rede
    net.build()
    
    info("*** Iniciando controlador SDN\n")
    # Inicia controlador OpenFlow
    c0.start()
    
    info("*** Iniciando switch central e APs como switches OpenFlow\n")
    # Inicia switch central conectado ao controlador
    s1.start([c0])
    
    # Inicia APs como switches OpenFlow
    ap1.start([c0])
    ap2.start([c0])
    
    info("*** Configurando roteamento entre as sub-redes\n")
    # Habilita roteamento IP nos APs e switch
    ap1.cmd('sysctl -w net.ipv4.ip_forward=1')
    ap2.cmd('sysctl -w net.ipv4.ip_forward=1')
    s1.cmd('sysctl -w net.ipv4.ip_forward=1')
    
    # Configura IPs das interfaces dos APs como gateways
    ap1.cmd('ifconfig ap1-eth1 192.168.1.1/24')
    ap2.cmd('ifconfig ap2-eth1 192.168.2.1/24')
    
    # Configura rotas padrão nas estações
    sta1.cmd('ip route add default via 192.168.1.1')
    sta2.cmd('ip route add default via 192.168.1.1')
    sta3.cmd('ip route add default via 192.168.2.1')
    sta4.cmd('ip route add default via 192.168.2.1')
    
    info("*** Verificando associações Wi-Fi\n")
    # Lista para verificar todas as associações
    associations = [
        (sta1, 'ap1', '192.168.1.101'),
        (sta2, 'ap1', '192.168.1.102'),
        (sta3, 'ap2', '192.168.2.101'),
        (sta4, 'ap2', '192.168.2.102')
    ]
    
    for sta, ap_name, ip in associations:
        # Aguarda associação Wi-Fi
        import time
        time.sleep(1)
        
        # Verifica conexão Wi-Fi
        result = sta.cmd('iw dev %s-wlan0 link' % sta.name)
        if 'Connected' in result:
            info(f"*** ✓ {sta.name} ({ip}) conectado ao {ap_name}\n")
        else:
            info(f"*** ✗ {sta.name} não conectado ao {ap_name}\n")
    
    info("*** Testando conectividade básica com ping\n")
    info("*** Teste 1: Comunicação intra-AP (sta1 -> sta2)\n")
    ping_result = sta1.cmd('ping -c 3 192.168.1.102')
    info(ping_result)
    
    info("*** Teste 2: Comunicação intra-AP (sta3 -> sta4)\n")
    ping_result = sta3.cmd('ping -c 3 192.168.2.102')
    info(ping_result)
    
    info("*** Teste 3: Comunicação inter-AP via switch (sta1 -> sta3)\n")
    ping_result = sta1.cmd('ping -c 3 192.168.2.101')
    info(ping_result)
    
    info("*** Testando conectividade completa com pingAll\n")
    # Teste de ping entre todos os hosts
    net.pingAll(timeout=2)
    
    info("*** Testando throughput com iperf\n")
    info("*** Teste iperf: sta1 (AP1) -> sta3 (AP2)\n")
    # Inicia servidor iperf na sta1
    sta1.cmd('iperf -s -u -i 1 &')
    # Cliente iperf na sta3
    iperf_result = sta3.cmd('iperf -c 192.168.1.101 -u -b 2M -t 3')
    info(iperf_result)
    # Encerra servidor iperf
    sta1.cmd('pkill -f iperf')
    
    info("*** Resumo da topologia criada:\n")
    info("*** Controlador SDN: c0 (127.0.0.1:6653)\n")
    info("*** Switch Central: s1 (conecta ap1 e ap2)\n")
    info("*** AP1: canal 1 (2.412 GHz), SSID: Rede-AP1, Sub-rede: 192.168.1.0/24\n")
    info("***   - sta1: 192.168.1.101 @ (20,80,0)\n")
    info("***   - sta2: 192.168.1.102 @ (40,20,0)\n")
    info("*** AP2: canal 6 (2.437 GHz), SSID: Rede-AP2, Sub-rede: 192.168.2.0/24\n")
    info("***   - sta3: 192.168.2.101 @ (60,80,0)\n")
    info("***   - sta4: 192.168.2.102 @ (80,20,0)\n")
    info("*** Todos os APs usando segurança WPA2\n")
    
    info("*** Iniciando CLI interativa do Mininet-WiFi\n")
    info("*** Comandos disponíveis:\n")
    info("***   'nodes'           - Lista todos os nós da rede\n")
    info("***   'net'             - Mostra conexões da rede\n")
    info("***   'dump'            - Informações detalhadas de cada nó\n")
    info("***   'sta1 iwconfig'   - Configuração Wi-Fi da sta1\n")
    info("***   'sta1 ping 192.168.2.101' - Teste de conectividade\n")
    info("***   'sh ovs-ofctl dump-flows s1' - Mostra regras OpenFlow\n")
    info("***   'exit'            - Encerra a simulação\n\n")
    
    # Inicia interface de linha de comandos para controle manual
    CLI(net)
    
    info("*** Encerrando todos os processos da rede\n")
    # Para e limpa toda a rede
    net.stop()

if __name__ == '__main__':
    # Ponto de entrada do script
    create_dual_ap_topology()