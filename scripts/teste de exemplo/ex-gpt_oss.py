#!/usr/bin/env python
"""
Mininet‑WiFi topologia de Handover

- 2 pontos de acesso (ap1, ap2) nos canais 1 e 6
- 2 estações (sta1, sta2) com MACs fixos
- Link cabeado entre os APs
- Modelo de propagação logDistance, expoente 5
- Plot gráfico ativado por padrão; desativado com a flag '-p'
- Flag '-s': posições estáticas iniciais; sem flag habilita mobilidade
- SSID dos dois APs são idênticos (handover-net) para roaming transparente
"""

import sys

from mininet.log import setLogLevel, info
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi


def topology(args):
    """Cria a topologia de acordo com os argumentos passados."""
    net = Mininet_wifi()

    info("*** Criando nós\n")
    sta1_args, sta2_args = {}, {}

    # Se '-s' for presente, definimos posições estáticas
    if '-s' in args:
        sta1_args['position'] = '10,30,0'
        sta2_args['position'] = '10,40,0'          # posicionamento arbitrário estático

    # Estações com MACs fixos
    sta1 = net.addStation('sta1',
                          mac='00:00:00:00:00:01',
                          ip='10.0.0.1/24',
                          **sta1_args)

    sta2 = net.addStation('sta2',
                          mac='00:00:00:00:00:02',
                          ip='10.0.0.2/24',
                          **sta2_args)

    # Pontos de acesso (SSID igual para roaming)
    ap1 = net.addAccessPoint('ap1',
                             ssid='handover-net',
                             mode='g',
                             channel='1',
                             position='15,30,0',
                             ip='10.0.0.3/24')

    ap2 = net.addAccessPoint('ap2',
                             ssid='handover-net',
                             mode='g',
                             channel='6',
                             position='55,30,0',
                             ip='10.0.0.4/24')

    # Controlador SDN
    c1 = net.addController('c1')

    # Modelo de propagação
    net.setPropagationModel(model='logDistance', exp=5)

    info("*** Configurando nós\n")
    net.configureWifiNodes()

    info("*** Criando links físicos (backhaul)\n")
    net.addLink(ap1, ap2)        # link cabeado entre os APs

    # Plot gráfico (habilitado por padrão)
    if '-p' not in args:
        net.plotGraph(max_x=100, max_y=100)

    # Mobilidade a menos que '-s' esteja presente
    if '-s' not in args:
        info("*** Habilitando mobilidade\n")
        net.startMobility(time=0)

        # Sta1: de 10,30,0 até 60,30,0 (seg 1‑10)
        net.mobility(sta1, 'start', time=1, position='10,30,0')
        net.mobility(sta1, 'stop', time=10, position='60,30,0')

        # Sta2: breve deslocamento (seg 2‑10)
        net.mobility(sta2, 'start', time=2, position='10,40,0')
        net.mobility(sta2, 'stop', time=10, position='25,40,0')

        net.stopMobility(time=11)

    info("*** Iniciando a rede\n")
    net.build()
    c1.start()
    ap1.start([c1])
    ap2.start([c1])

    info("*** Acessando CLI\n")
    CLI(net)

    info("*** Finalizando rede\n")
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    topology(sys.argv)
