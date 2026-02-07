#!/usr/bin/python

"""
Script Mininet-WiFi: Topologia Híbrida com Mobilidade Programada
Componentes:
- 1 Controlador (c0)
- 1 Switch Intermediário (s1)
- 2 Access Points (ap1, ap2): Canais 1 e 11, Alcance 40m
- 6 Estações (sta1 a sta6): Distribuição inicial equilibrada e mobilidade definida
Objetivo: Simular roaming e conectividade contínua com movimentação de nós.
"""

from mininet.node import Controller, OVSSwitch
from mininet.log import setLogLevel, info
from mn_wifi.net import Mininet_wifi
from mn_wifi.node import OVSKernelAP
from mn_wifi.link import wmediumd
import time

def topology():
    # Define o nível de log para visualizar detalhes da execução
    setLogLevel('info')

    info("*** Inicializando a rede Mininet-WiFi\n")
    # Utiliza wmediumd para simulação avançada de sinal e interferência
    net = Mininet_wifi(controller=Controller, accessPoint=OVSKernelAP, 
                       switch=OVSSwitch, link=wmediumd)

    info("*** Adicionando o Controlador\n")
    # Utiliza o controlador padrão (pode ser substituído por RemoteController se houver um externo)
    c0 = net.addController('c0')

    info("*** Adicionando o Switch Intermediário\n")
    s1 = net.addSwitch('s1')

    info("*** Adicionando os Access Points\n")
    # AP1: Lado esquerdo (30, 50), Canal 1, Alcance 40m
    ap1 = net.addAccessPoint('ap1', ssid='hybrid-net', mode='g', channel='1',
                             position='30,50,0', range=40)
    
    # AP2: Lado direito (70, 50), Canal 11 (não interfere com canal 1), Alcance 40m
    ap2 = net.addAccessPoint('ap2', ssid='hybrid-net', mode='g', channel='11',
                             position='70,50,0', range=40)

    info("*** Adicionando as Estações\n")
    # Adiciona as estações. A posição inicial será definida via net.mobility logo abaixo.
    # Atribuição de IPs sequenciais (10.0.0.1 a 10.0.0.6)
    sta1 = net.addStation('sta1', ip='10.0.0.1/8')
    sta2 = net.addStation('sta2', ip='10.0.0.2/8')
    sta3 = net.addStation('sta3', ip='10.0.0.3/8')
    sta4 = net.addStation('sta4', ip='10.0.0.4/8')
    sta5 = net.addStation('sta5', ip='10.0.0.5/8')
    sta6 = net.addStation('sta6', ip='10.0.0.6/8')

    info("*** Configurando os nós Wi-Fi\n")
    net.configureWifiNodes()

    info("*** Criando os links cabeados\n")
    # Conecta os APs ao switch central s1
    net.addLink(ap1, s1)
    net.addLink(ap2, s1)

    info("*** Habilitando visualização gráfica\n")
    net.plotGraph(max_x=100, max_y=100)

    info("*** Configurando a Mobilidade (Start/Stop)\n")
    # Configura o início da mobilidade no tempo 1s e o fim no tempo 10s
    
    # Grupo 1: Começa na área do AP1 (Esquerda) e move-se para AP2 (Direita)
    net.mobility(sta1, 'start', time=1, position='10,50,0')
    net.mobility(sta1, 'stop', time=10, position='90,50,0')

    net.mobility(sta2, 'start', time=1, position='20,60,0')
    net.mobility(sta2, 'stop', time=10, position='80,60,0')

    net.mobility(sta3, 'start', time=1, position='20,40,0')
    net.mobility(sta3, 'stop', time=10, position='80,40,0')

    # Grupo 2: Começa na área do AP2 (Direita) e move-se para AP1 (Esquerda)
    net.mobility(sta4, 'start', time=1, position='90,50,0')
    net.mobility(sta4, 'stop', time=10, position='10,50,0')

    net.mobility(sta5, 'start', time=1, position='80,60,0')
    net.mobility(sta5, 'stop', time=10, position='20,60,0')

    net.mobility(sta6, 'start', time=1, position='80,40,0')
    net.mobility(sta6, 'stop', time=10, position='20,40,0')

    info("*** Construindo a topologia\n")
    net.build()

    info("*** Iniciando Controlador, Switch e Access Points\n")
    c0.start()
    s1.start([c0])
    ap1.start([c0])
    ap2.start([c0])

    info("*** Aguardando início da mobilidade...\n")
    # Pequena pausa para garantir que as interfaces subiram
    time.sleep(2)

    info("*** Verificando conectividade inicial (PingAll)\n")
    net.pingAll()

    info("*** Executando simulação de movimento...\n")
    # Loop simples para manter o script rodando enquanto a mobilidade ocorre (simulado por 10s)
    # Durante este tempo, as estações trocarão de AP (Handover)
    start_time = time.time()
    while time.time() - start_time < 12:
        # Imprime a posição atual de sta1 e sta4 como exemplo de monitoramento
        # x, y, z = sta1.position
        # info(f"sta1 pos: {x:.2f},{y:.2f} | ")
        # x, y, z = sta4.position
        # info(f"sta4 pos: {x:.2f},{y:.2f}\n")
        time.sleep(1)

    info("*** Verificando conectividade final (pós-mobilidade)\n")
    net.pingAll()

    info("*** Finalizando a rede\n")
    net.stop()

if __name__ == '__main__':
    topology()