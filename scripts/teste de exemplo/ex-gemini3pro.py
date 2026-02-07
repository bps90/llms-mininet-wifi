#!/usr/bin/python

"""
Script Mininet-WiFi: Cenário de Handover com Argumentos de CLI
Componentes:
- 1 Controlador (c0)
- 2 Access Points (ap1, ap2): Canais 1 e 6, conectados via cabo
- 2 Estações (sta1, sta2): MACs fixos
- Modelo de Propagação: logDistance (exp=5)

Argumentos de Linha de Comando:
  -p : Desativa a plotagem gráfica (plotGraph). Padrão: Ativado.
  -s : Ativa modo estático (sem mobilidade). Padrão: Mobilidade ativada.

Exemplo de uso:
  sudo python handover_script.py        (Mobilidade ON, Gráfico ON)
  sudo python handover_script.py -p     (Mobilidade ON, Gráfico OFF)
  sudo python handover_script.py -s     (Estático ON, Gráfico ON)
"""

import sys
import time
from mininet.node import Controller
from mininet.log import setLogLevel, info
from mn_wifi.net import Mininet_wifi
from mn_wifi.node import OVSKernelAP
from mn_wifi.link import wmediumd

def topology():
    # Define nível de log
    setLogLevel('info')

    # Processamento de Argumentos
    enable_plot = True
    static_mode = False

    if '-p' in sys.argv:
        enable_plot = False
        info("*** Argumento detectado: Plotagem gráfica DESATIVADA (-p)\n")
    else:
        info("*** Plotagem gráfica ATIVADA (Padrão)\n")

    if '-s' in sys.argv:
        static_mode = True
        info("*** Argumento detectado: Modo ESTÁTICO ativado (-s)\n")
    else:
        info("*** Modo MOBILIDADE ativado (Padrão)\n")

    info("*** Inicializando a rede Mininet-WiFi\n")
    net = Mininet_wifi(controller=Controller, accessPoint=OVSKernelAP, 
                       link=wmediumd)

    info("*** Configurando Modelo de Propagação\n")
    # Modelo logDistance com expoente 5 (alta atenuação) para facilitar o handover
    net.setPropagationModel(model="logDistance", exp=5)

    info("*** Adicionando o Controlador\n")
    c0 = net.addController('c0')

    info("*** Adicionando os Access Points\n")
    # AP1: Posição 20,30 (Esquerda), Canal 1
    ap1 = net.addAccessPoint('ap1', ssid='handover-net', mode='g', channel='1', 
                             position='20,30,0')
    
    # AP2: Posição 50,30 (Direita), Canal 6
    ap2 = net.addAccessPoint('ap2', ssid='handover-net', mode='g', channel='6', 
                             position='50,30,0')

    info("*** Adicionando as Estações\n")
    # sta1 e sta2 com MACs fixos
    if static_mode:
        # Posições fixas caso a flag -s seja usada
        sta1 = net.addStation('sta1', mac='00:00:00:00:00:01', ip='10.0.0.1/8', 
                              position='20,35,0')
        sta2 = net.addStation('sta2', mac='00:00:00:00:00:02', ip='10.0.0.2/8', 
                              position='50,35,0')
    else:
        # Posições iniciais para mobilidade (serão sobrescritas pelo net.mobility)
        sta1 = net.addStation('sta1', mac='00:00:00:00:00:01', ip='10.0.0.1/8')
        sta2 = net.addStation('sta2', mac='00:00:00:00:00:02', ip='10.0.0.2/8')

    info("*** Configurando os nós Wi-Fi\n")
    net.configureWifiNodes()

    info("*** Criando Link Cabeado entre APs\n")
    # Conexão direta entre AP1 e AP2 (Backbone)
    net.addLink(ap1, ap2)

    # Configuração da Plotagem Gráfica (se não desativada por -p)
    if enable_plot:
        info("*** Habilitando Plotagem Gráfica\n")
        net.plotGraph(max_x=100, max_y=100)

    # Configuração da Mobilidade (se não desativada por -s)
    if not static_mode:
        info("*** Configurando Parâmetros de Mobilidade\n")
        net.startMobility(time=0)
        
        # sta1: Move-se de x=10 para x=60 (passando pelo ap1 e indo para o ap2)
        net.mobility(sta1, 'start', time=1, position='10,30,0')
        net.mobility(sta1, 'stop', time=10, position='60,30,0')

        # sta2: Movimento breve conforme solicitado
        net.mobility(sta2, 'start', time=2, position='10,40,0')
        net.mobility(sta2, 'stop', time=10, position='60,40,0')

    info("*** Construindo a topologia\n")
    net.build()

    info("*** Iniciando Controlador e Access Points\n")
    c0.start()
    ap1.start([c0])
    ap2.start([c0])

    info("*** Aguardando estabilização da rede...\n")
    time.sleep(2)

    info("*** Verificando conectividade (PingAll)\n")
    net.pingAll()

    if not static_mode:
        info("*** Monitorando Handover durante a mobilidade (10 segundos)...\n")
        start_time = time.time()
        while time.time() - start_time < 12:
            # Mantém o script rodando para permitir a visualização do gráfico e movimento
            # O handover ocorre automaticamente gerenciado pelo wmediumd/kernel
            time.sleep(1)
    
    info("*** Finalizando a rede\n")
    net.stop()

if __name__ == '__main__':
    topology()