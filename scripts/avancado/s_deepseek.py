#!/usr/bin/env python3
"""
Topologia Mininet-WiFi: Rede Híbrida com Mobilidade e Handover
Dois APs, seis estações, mobilidade entre coberturas, controlador SDN
"""

from mininet.node import Controller, OVSKernelSwitch
from mininet.log import setLogLevel, info
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.link import wmediumd
from mn_wifi.wmediumdConnector import interference
import random
import time

def create_mobile_hybrid_network():
    """Cria rede híbrida com mobilidade e handover entre APs"""
    
    # Configura nível de log
    setLogLevel('info')
    
    info("*** Inicializando rede híbrida com mobilidade\n")
    # Cria rede com suporte a mobilidade e interferência
    net = Mininet_wifi(
        controller=Controller,
        switch=OVSKernelSwitch,
        accessPoint=OVSKernelSwitch,
        link=wmediumd,
        wmediumd_mode=interference,
        noise_threshold=-91,
        fading_coefficient=2.5,
        autoAssociation=True,
        autoTxPower=True,
        associationMethod='new'  # Método de associação mais eficiente
    )
    
    info("*** Adicionando controlador SDN\n")
    # Controlador para gerenciamento centralizado
    c0 = net.addController('c0', 
                           controller=Controller, 
                           ip='127.0.0.1', 
                           protocol='tcp',
                           port=6653,
                           mac='00:00:00:00:c0:01')
    
    info("*** Adicionando switch central\n")
    # Switch que interconecta os APs
    s1 = net.addSwitch('s1', 
                       cls=OVSKernelSwitch, 
                       protocols='OpenFlow13',
                       failMode='standalone',
                       mac='00:00:00:00:sw:01')
    
    info("*** Adicionando pontos de acesso com canais não sobrepostos\n")
    # AP1 - Área de cobertura esquerda
    ap1 = net.addAccessPoint('ap1',
                             ssid='Rede-Corporativa',
                             mode='g',
                             channel=1,           # Canal 1 (2.412 GHz)
                             position='25,50,0',
                             range=45,            # Alcance de 45m
                             encrypt='wpa2',
                             passwd='corp@secure',
                             mac='00:00:00:00:ap:01',
                             datapath='kernel',
                             failMode='secure')
    
    # AP2 - Área de cobertura direita
    ap2 = net.addAccessPoint('ap2',
                             ssid='Rede-Corporativa',  # Mesmo SSID para handover suave
                             mode='g',
                             channel=6,           # Canal 6 (2.437 GHz)
                             position='75,50,0',
                             range=45,
                             encrypt='wpa2',
                             passwd='corp@secure',
                             mac='00:00:00:00:ap:02',
                             datapath='kernel',
                             failMode='secure')
    
    info("*** Adicionando seis estações com mobilidade\n")
    # Configurações comuns para todas as estações
    station_config = {
        'authmode': 'wpa2',
        'encrypt': 'wpa2',
        'passwd': 'corp@secure',
        'range': 35,
    }
    
    # Estações - inicialmente distribuídas entre os APs
    # Grupo 1: Inicialmente conectadas ao AP1
    sta1 = net.addStation('sta1',
                          mac='00:00:00:00:01:01',
                          ip='10.0.0.101/24',
                          position='15,70,0',    # Perto do AP1
                          **station_config)
    
    sta2 = net.addStation('sta2',
                          mac='00:00:00:00:01:02',
                          ip='10.0.0.102/24',
                          position='20,30,0',    # Perto do AP1
                          **station_config)
    
    sta3 = net.addStation('sta3',
                          mac='00:00:00:00:01:03',
                          ip='10.0.0.103/24',
                          position='35,50,0',    # Zona de sobreposição
                          **station_config)
    
    # Grupo 2: Inicialmente conectadas ao AP2
    sta4 = net.addStation('sta4',
                          mac='00:00:00:00:02:01',
                          ip='10.0.0.104/24',
                          position='65,50,0',    # Zona de sobreposição
                          **station_config)
    
    sta5 = net.addStation('sta5',
                          mac='00:00:00:00:02:02',
                          ip='10.0.0.105/24',
                          position='80,70,0',    # Perto do AP2
                          **station_config)
    
    sta6 = net.addStation('sta6',
                          mac='00:00:00:00:02:03',
                          ip='10.0.0.106/24',
                          position='85,30,0',    # Perto do AP2
                          **station_config)
    
    info("*** Configurando parâmetros Wi-Fi e mobilidade\n")
    # Aplica configurações de propagação
    net.configureWifiNodes()
    
    info("*** Configurando modelo de mobilidade para handover\n")
    # Configura modelo de mobilidade com roaming
    net.setMobilityModel(time=0, 
                         model='randomDirection',  # Movimento em direções aleatórias
                         max_x=100,               # Área máxima X
                         max_y=100,               # Área máxima Y
                         min_v=0.5,               # Velocidade mínima (m/s)
                         max_v=2.0,               # Velocidade máxima (m/s)
                         seed=20)                 # Semente para reproduzibilidade
    
    info("*** Criando enlaces físicos\n")
    # Conecta APs ao switch central
    net.addLink(ap1, s1, bw=100)  # 100 Mbps
    net.addLink(ap2, s1, bw=100)  # 100 Mbps
    
    info("*** Construindo topologia completa\n")
    net.build()
    
    info("*** Iniciando controlador SDN\n")
    c0.start()
    
    info("*** Iniciando switch e APs\n")
    s1.start([c0])
    ap1.start([c0])
    ap2.start([c0])
    
    info("*** Configurando rede única para roaming suave\n")
    # Configura mesma sub-rede para todos (facilita roaming)
    ap1.cmd('ifconfig ap1-eth1 10.0.0.1/24')
    ap2.cmd('ifconfig ap2-eth1 10.0.0.2/24')
    
    # Configura gateway padrão nas estações
    for sta in [sta1, sta2, sta3, sta4, sta5, sta6]:
        sta.cmd('ip route add default via 10.0.0.1 metric 100')
        sta.cmd('ip route add default via 10.0.0.2 metric 200')  # Gateway secundário
    
    # Habilita roteamento IP
    ap1.cmd('sysctl -w net.ipv4.ip_forward=1')
    ap2.cmd('sysctl -w net.ipv4.ip_forward=1')
    s1.cmd('sysctl -w net.ipv4.ip_forward=1')
    
    info("*** Iniciando mobilidade e aguardando estabilização\n")
    # Inicia modelo de mobilidade
    net.startMobility(time=0)
    
    # Aguarda associações se estabilizarem
    time.sleep(5)
    
    info("*** Monitorando associações iniciais\n")
    stations = [sta1, sta2, sta3, sta4, sta5, sta6]
    for sta in stations:
        result = sta.cmd('iw dev %s-wlan0 link' % sta.name)
        if 'Connected' in result:
            # Extrai SSID do resultado
            if 'SSID' in result:
                for line in result.split('\n'):
                    if 'SSID' in line:
                        info(f"*** {sta.name} conectado a {line.strip()}\n")
                        break
        else:
            info(f"*** {sta.name} aguardando associação...\n")
    
    info("*** Testando conectividade básica\n")
    info("*** Teste de ping entre extremos (sta1 -> sta6)\n")
    ping_result = sta1.cmd('ping -c 3 10.0.0.106')
    info(ping_result)
    
    info("*** Teste de ping todos vs todos\n")
    net.pingAll(timeout=2)
    
    info("*** Demonstração de mobilidade e handover\n")
    info("*** Movendo estações entre áreas de cobertura...\n")
    
    # Demonstração de movimento controlado
    info("*** Movendo sta3 para área do AP2\n")
    sta3.setPosition('70,50,0')  # Move para área do AP2
    time.sleep(3)
    
    info("*** Movendo sta4 para área do AP1\n")
    sta4.setPosition('30,50,0')  # Move para área do AP1
    time.sleep(3)
    
    info("*** Verificando handover após movimento\n")
    for sta in [sta3, sta4]:
        result = sta.cmd('iw dev %s-wlan0 link' % sta.name)
        if 'Connected' in result:
            info(f"*** {sta.name} reconectado após movimento\n")
    
    info("*** Testando conectividade durante mobilidade\n")
    info("*** Iniciando teste de ping contínuo durante movimento\n")
    
    # Inicia ping em background para monitorar conectividade
    sta1.cmd('ping 10.0.0.106 -i 0.5 -c 20 > /tmp/ping_test.txt &')
    
    # Simula movimento durante o ping
    info("*** Simulando movimento das estações durante 15 segundos\n")
    positions = [
        ('20,80,0'), ('40,20,0'), ('60,60,0'),
        ('80,80,0'), ('40,40,0'), ('70,20,0')
    ]
    
    for i in range(5):
        # Move estações para posições aleatórias
        for idx, sta in enumerate(stations):
            new_pos = positions[(idx + i) % len(positions)]
            sta.setPosition(new_pos)
        
        time.sleep(3)
        info(f"*** Ciclo de movimento {i+1}/5 concluído\n")
    
    # Aguarda ping terminar
    time.sleep(2)
    
    info("*** Resultado do ping durante mobilidade:\n")
    ping_stats = sta1.cmd('tail -n 5 /tmp/ping_test.txt')
    info(ping_stats)
    
    info("*** Testando throughput com iperf durante mobilidade\n")
    info("*** Servidor iperf em sta1, cliente em sta6\n")
    
    # Teste de throughput
    sta1.cmd('iperf -s -u -i 1 > /tmp/iperf_server.log &')
    time.sleep(1)
    iperf_result = sta6.cmd('iperf -c 10.0.0.101 -u -b 1M -t 10')
    info(iperf_result)
    sta1.cmd('pkill -f iperf')
    
    info("*** Analisando log do servidor iperf:\n")
    server_log = sta1.cmd('tail -n 10 /tmp/iperf_server.log')
    info(server_log)
    
    info("*** Resumo da topologia de mobilidade:\n")
    info("*** Controlador: c0 (OpenFlow 1.3)\n")
    info("*** Switch Central: s1\n")
    info("*** APs: ap1 (canal 1) e ap2 (canal 6) - Mesmo SSID para handover\n")
    info("*** Estações: sta1-sta6 (10.0.0.101-106)\n")
    info("*** Área de cobertura: 0-100m em X e Y\n")
    info("*** Mobilidade: Modelo randomDirection com velocidade 0.5-2.0 m/s\n")
    info("*** Handover automático baseado em força de sinal\n")
    
    info("*** Iniciando CLI interativa para controle manual\n")
    info("*** Comandos de mobilidade disponíveis:\n")
    info("***   'py sta1.setPosition(\"50,50,0\")' - Move estação\n")
    info("***   'py sta1.setPosition(\"80,50,0\")' - Força handover\n")
    info("***   'sta1 iw dev sta1-wlan0 link' - Status de conexão\n")
    info("***   'sta1 iw event' - Monitora eventos Wi-Fi\n")
    info("***   'nodes' - Lista todos os nós\n")
    info("***   'exit' - Encerra simulação\n\n")
    
    info("*** Dica: Observe os logs para ver handovers automáticos\n")
    
    # Inicia CLI
    CLI(net)
    
    info("*** Parando mobilidade e encerrando rede\n")
    # Para mobilidade
    net.stopMobility()
    
    # Encerra rede
    net.stop()

def monitor_associations(net, interval=5):
    """Função para monitorar associações periodicamente"""
    stations = [net.get('sta%d' % i) for i in range(1, 7)]
    
    while True:
        info("*** Status de associação:\n")
        for sta in stations:
            result = sta.cmd('iw dev %s-wlan0 link' % sta.name)
            if 'Connected' in result:
                for line in result.split('\n'):
                    if 'SSID' in line:
                        info(f"  {sta.name}: {line.strip()}\n")
                        break
            else:
                info(f"  {sta.name}: Não associado\n")
        
        time.sleep(interval)

if __name__ == '__main__':
    # Ponto de entrada principal
    create_mobile_hybrid_network()