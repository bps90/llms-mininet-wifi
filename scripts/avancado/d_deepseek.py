#!/usr/bin/env python3
"""
Topologia Mininet-WiFi: Rede Híbrida com Mobilidade Controlada
Dois APs (canais 1 e 11), seis estações, switch intermediário, controlador SDN remoto
Mobilidade com posições e tempos definidos, DHCP automático
"""

from mininet.node import Controller, OVSKernelSwitch, RemoteController
from mininet.log import setLogLevel, info
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.link import wmediumd
from mn_wifi.wmediumdConnector import interference
import time

def create_hybrid_mobile_network():
    """Cria rede híbrida com mobilidade controlada e controlador SDN remoto"""
    
    # Configura nível de log
    setLogLevel('info')
    
    info("*** Inicializando rede híbrida com mobilidade controlada\n")
    # Cria rede com modelo de interferência
    net = Mininet_wifi(
        controller=None,  # Será adicionado como controlador remoto
        switch=OVSKernelSwitch,
        accessPoint=OVSKernelSwitch,
        link=wmediumd,
        wmediumd_mode=interference,
        noise_threshold=-91,
        fading_coefficient=3.0,
        autoAssociation=True,
        autoTxPower=True
    )
    
    info("*** Adicionando controlador SDN remoto\n")
    # Controlador remoto (pode ser externo, mas usando localhost para exemplo)
    c0 = net.addController('c0',
                           controller=RemoteController,
                           ip='127.0.0.1',  # IP do controlador remoto
                           protocol='tcp',
                           port=6653,
                           mac='00:00:00:00:00:c0')
    
    info("*** Adicionando switch intermediário\n")
    # Switch que conecta os APs
    s1 = net.addSwitch('s1',
                       cls=OVSKernelSwitch,
                       protocols='OpenFlow13',
                       failMode='secure',
                       mac='00:00:00:00:00:s1')
    
    info("*** Adicionando pontos de acesso em canais não interferentes\n")
    # AP1 - Canal 1
    ap1 = net.addAccessPoint('ap1',
                             ssid='Rede-Movel-AP1',
                             mode='g',
                             channel=1,           # Canal 1 (2.412 GHz)
                             position='30,50,0',
                             range=40,            # Alcance de 40 metros
                             encrypt='wpa2',
                             passwd='senha123',
                             mac='00:00:00:00:00:a1',
                             datapath='kernel',
                             failMode='standalone')
    
    # AP2 - Canal 11
    ap2 = net.addAccessPoint('ap2',
                             ssid='Rede-Movel-AP2',
                             mode='g',
                             channel=11,          # Canal 11 (2.462 GHz)
                             position='70,50,0',
                             range=40,
                             encrypt='wpa2',
                             passwd='senha123',
                             mac='00:00:00:00:00:a2',
                             datapath='kernel',
                             failMode='standalone')
    
    info("*** Adicionando seis estações sem fio\n")
    # Configuração comum para todas as estações
    station_config = {
        'authmode': 'wpa2',
        'encrypt': 'wpa2',
        'passwd': 'senha123',
        'range': 35,
        'ip': 'dhcp'  # Endereços IP automáticos via DHCP
    }
    
    # Estações - inicialmente 3 em cada AP
    # Grupo AP1 (posições à esquerda)
    sta1 = net.addStation('sta1',
                          mac='00:00:00:00:00:01',
                          position='15,70,0',    # Perto do AP1
                          **station_config)
    
    sta2 = net.addStation('sta2',
                          mac='00:00:00:00:00:02',
                          position='30,30,0',    # Perto do AP1
                          **station_config)
    
    sta3 = net.addStation('sta3',
                          mac='00:00:00:00:00:03',
                          position='45,60,0',    # Zona de transição
                          **station_config)
    
    # Grupo AP2 (posições à direita)
    sta4 = net.addStation('sta4',
                          mac='00:00:00:00:00:04',
                          position='55,60,0',    # Zona de transição
                          **station_config)
    
    sta5 = net.addStation('sta5',
                          mac='00:00:00:00:00:05',
                          position='70,70,0',    # Perto do AP2
                          **station_config)
    
    sta6 = net.addStation('sta6',
                          mac='00:00:00:00:00:06',
                          position='85,30,0',    # Perto do AP2
                          **station_config)
    
    info("*** Configurando parâmetros físicos Wi-Fi\n")
    # Aplica modelo de propagação
    net.configureWifiNodes()
    
    info("*** Configurando mobilidade com tempos controlados\n")
    # Define modelo de mobilidade inicial (estático)
    net.setMobilityModel(time=0, model='static')
    
    info("*** Criando enlaces físicos\n")
    # Conecta APs ao switch intermediário
    net.addLink(ap1, s1, bw=100, delay='1ms')
    net.addLink(ap2, s1, bw=100, delay='1ms')
    
    info("*** Construindo topologia\n")
    net.build()
    
    info("*** Iniciando controlador remoto\n")
    c0.start()
    
    info("*** Iniciando switch e APs\n")
    s1.start([c0])
    ap1.start([c0])
    ap2.start([c0])
    
    info("*** Configurando DHCP para IPs automáticos\n")
    # Configura servidor DHCP em cada AP
    ap1.cmd('ifconfig ap1-eth1 192.168.1.1/24')
    ap1.cmd('/usr/sbin/dnsmasq --dhcp-range=192.168.1.100,192.168.1.150,255.255.255.0,12h')
    
    ap2.cmd('ifconfig ap2-eth1 192.168.2.1/24')
    ap2.cmd('/usr/sbin/dnsmasq --dhcp-range=192.168.2.100,192.168.2.150,255.255.255.0,12h')
    
    # Habilita roteamento entre sub-redes
    ap1.cmd('sysctl -w net.ipv4.ip_forward=1')
    ap2.cmd('sysctl -w net.ipv4.ip_forward=1')
    s1.cmd('sysctl -w net.ipv4.ip_forward=1')
    
    info("*** Aguardando DHCP nas estações\n")
    # Força renovação de DHCP
    for sta in [sta1, sta2, sta3, sta4, sta5, sta6]:
        sta.cmd('dhclient -r %s-wlan0' % sta.name)
        sta.cmd('dhclient %s-wlan0' % sta.name)
    
    time.sleep(5)  # Aguarda concessão de IPs
    
    info("*** Verificando IPs atribuídos\n")
    for sta in [sta1, sta2, sta3, sta4, sta5, sta6]:
        ip_info = sta.cmd('ifconfig %s-wlan0' % sta.name)
        for line in ip_info.split('\n'):
            if 'inet ' in line:
                info(f"*** {sta.name}: {line.strip()}\n")
                break
    
    info("*** Configurando mobilidade controlada com net.mobility()\n")
    # Configura mobilidade para cada estação com tempos específicos
    # net.mobility() é implementado através do setMobilityModel com waypoints
    
    # Define waypoints para mobilidade controlada
    # Formato: (estação, posição_inicial, posição_final, tempo_início, tempo_parada)
    
    # Primeiro grupo: movimentação precoce (início em 10s, parada em 40s)
    net.mobility(sta1, 'start', time=10, position='15,70,0')
    net.mobility(sta1, 'stop', time=40, position='80,70,0')  # Move para área do AP2
    
    net.mobility(sta2, 'start', time=10, position='30,30,0')
    net.mobility(sta2, 'stop', time=40, position='60,30,0')  # Move para zona central
    
    # Segundo grupo: movimentação tardia (início em 30s, parada em 60s)
    net.mobility(sta5, 'start', time=30, position='70,70,0')
    net.mobility(sta5, 'stop', time=60, position='20,70,0')  # Move para área do AP1
    
    net.mobility(sta6, 'start', time=30, position='85,30,0')
    net.mobility(sta6, 'stop', time=60, position='40,30,0')  # Move para zona central
    
    # Terceiro grupo: movimento oscilatório (múltiplos waypoints)
    # sta3: movimento em etapas
    net.mobility(sta3, 'start', time=15, position='45,60,0')
    net.mobility(sta3, 'stop', time=30, position='65,60,0')  # Primeira etapa
    net.mobility(sta3, 'start', time=45, position='65,60,0')
    net.mobility(sta3, 'stop', time=60, position='25,60,0')  # Segunda etapa
    
    # sta4: movimento em etapas
    net.mobility(sta4, 'start', time=20, position='55,60,0')
    net.mobility(sta4, 'stop', time=35, position='35,60,0')  # Primeira etapa
    net.mobility(sta4, 'start', time=50, position='35,60,0')
    net.mobility(sta4, 'stop', time=65, position='75,60,0')  # Segunda etapa
    
    info("*** Iniciando mobilidade programada\n")
    # Inicia o módulo de mobilidade
    net.startMobility(startTime=0)
    
    info("*** Verificando associações iniciais\n")
    for i, sta in enumerate([sta1, sta2, sta3, sta4, sta5, sta6], 1):
        result = sta.cmd('iw dev %s-wlan0 link' % sta.name)
        if 'Connected' in result:
            for line in result.split('\n'):
                if 'SSID' in line:
                    info(f"*** sta{i}: {line.strip()}\n")
                    break
    
    info("*** Testando conectividade inicial\n")
    # Obtém IPs das estações para teste
    sta1_ip = sta1.cmd("ifconfig sta1-wlan0 | grep 'inet ' | awk '{print $2}'").strip()
    sta6_ip = sta6.cmd("ifconfig sta6-wlan0 | grep 'inet ' | awk '{print $2}'").strip()
    
    if sta1_ip and sta6_ip:
        info(f"*** Teste de ping: {sta1_ip} -> {sta6_ip}\n")
        ping_result = sta1.cmd('ping -c 3 %s' % sta6_ip)
        info(ping_result)
    else:
        info("*** Aguardando mais tempo para DHCP...\n")
        time.sleep(3)
    
    info("*** Testando conectividade entre todos os hosts\n")
    net.pingAll(timeout=2)
    
    info("*** Iniciando testes durante mobilidade\n")
    info("*** Os seguintes movimentos estão programados:\n")
    info("*** 1. sta1: (15,70)→(80,70) - t=10s a 40s\n")
    info("*** 2. sta2: (30,30)→(60,30) - t=10s a 40s\n")
    info("*** 3. sta3: (45,60)→(65,60)→(25,60) - t=15s a 60s\n")
    info("*** 4. sta4: (55,60)→(35,60)→(75,60) - t=20s a 65s\n")
    info("*** 5. sta5: (70,70)→(20,70) - t=30s a 60s\n")
    info("*** 6. sta6: (85,30)→(40,30) - t=30s a 60s\n")
    
    info("*** Monitorando handovers durante 70 segundos...\n")
    
    # Monitora handovers durante o período de mobilidade
    for t in range(0, 70, 10):
        info(f"*** Tempo: {t}s\n")
        if t > 0:
            # Verifica algumas estações a cada 10 segundos
            for sta in [sta1, sta3, sta5]:
                result = sta.cmd('iw dev %s-wlan0 link' % sta.name)
                if 'Connected' in result:
                    for line in result.split('\n'):
                        if 'SSID' in line:
                            info(f"  {sta.name}: {line.strip()}\n")
                            break
        
        # Aguarda próximo intervalo
        if t < 60:
            time.sleep(10)
    
    info("*** Teste de throughput após mobilidade\n")
    # Teste iperf entre estações que realizaram handover
    sta1.cmd('iperf -s -u -i 1 > /tmp/iperf_sta1.log &')
    time.sleep(1)
    
    # Usa sta5 que mudou de AP
    sta5_ip = sta5.cmd("ifconfig sta5-wlan0 | grep 'inet ' | awk '{print $2}'").strip()
    if sta5_ip:
        iperf_result = sta5.cmd('iperf -c %s -u -b 1M -t 5' % sta1_ip)
        info(iperf_result)
    
    sta1.cmd('pkill -f iperf')
    
    info("*** Resumo da topologia:\n")
    info("*** Controlador SDN remoto: c0 (127.0.0.1:6653)\n")
    info("*** Switch intermediário: s1\n")
    info("*** AP1: Canal 1, SSID: Rede-Movel-AP1, Alcance: 40m\n")
    info("*** AP2: Canal 11, SSID: Rede-Movel-AP2, Alcance: 40m\n")
    info("*** Estações: sta1-sta6 com IPs automáticos via DHCP\n")
    info("*** Mobilidade: Tempos de início/parada específicos para cada estação\n")
    info("*** DHCP: Sub-redes 192.168.1.0/24 (AP1) e 192.168.2.0/24 (AP2)\n")
    
    info("*** Iniciando CLI interativa\n")
    info("*** Comandos úteis para monitorar mobilidade:\n")
    info("***   'py sta1.params[\"position\"]' - Ver posição atual\n")
    info("***   'py sta1.setPosition(\"50,50,0\")' - Mover manualmente\n")
    info("***   'sta1 iw dev sta1-wlan0 link' - Ver conexão Wi-Fi\n")
    info("***   'sta1 iw event' - Monitorar eventos de handover\n")
    info("***   'nodes' - Listar todos os nós\n")
    info("***   'exit' - Encerrar simulação\n\n")
    
    # Inicia CLI interativa
    CLI(net)
    
    info("*** Parando mobilidade e encerrando rede\n")
    net.stopMobility()
    net.stop()

if __name__ == '__main__':
    # Ponto de entrada
    create_hybrid_mobile_network()