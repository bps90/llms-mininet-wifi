#!/usr/bin/python

"""
Script Mininet-WiFi: Topologia Simples (Infraestrutura)
Componentes:
- 1 Controlador (c0)
- 1 Access Point (ap1)
- 2 Estações (sta1, sta2)
Objetivo: Validar conectividade básica via ping entre estações sem fio.
"""

from mininet.node import Controller
from mininet.log import setLogLevel, info
from mn_wifi.net import Mininet_wifi
from mn_wifi.node import OVSKernelAP

def topology():
    # Define o nível de log para exibir informações detalhadas durante a execução
    setLogLevel('info')

    info("*** Inicializando a rede Mininet-WiFi\n")
    # Cria a instância da rede. O 'link=wmediumd' é opcional mas recomendado
    # para simulações mais realistas; aqui usamos o padrão kernel para simplicidade.
    net = Mininet_wifi(controller=Controller, accessPoint=OVSKernelAP)

    info("*** Adicionando o Controlador\n")
    c0 = net.addController('c0')

    info("*** Adicionando o Access Point\n")
    # Configura o AP com SSID, modo 802.11g e canal 1
    # A posição é definida em coordenadas (x, y, z)
    ap1 = net.addAccessPoint('ap1', ssid='simple-wifi', mode='g', channel='1', position='50,50,0')

    info("*** Adicionando as Estações\n")
    # sta1 e sta2 são configuradas com IPs estáticos e posições ao alcance do ap1
    sta1 = net.addStation('sta1', ip='10.0.0.1/8', position='30,50,0')
    sta2 = net.addStation('sta2', ip='10.0.0.2/8', position='70,50,0')

    info("*** Configurando os nós Wi-Fi\n")
    # Aplica as configurações físicas e de rádio
    net.configureWifiNodes()

    info("*** Construindo a topologia\n")
    net.build()

    info("*** Iniciando o Controlador e o Access Point\n")
    c0.start()
    ap1.start([c0])

    info("*** Verificando a conectividade (PingAll)\n")
    # Realiza o teste de ping entre todos os hosts (sta1 e sta2)
    # Se houver conectividade, o resultado será "0% dropped"
    net.pingAll()

    info("*** Finalizando a rede\n")
    net.stop()

if __name__ == '__main__':
    topology()