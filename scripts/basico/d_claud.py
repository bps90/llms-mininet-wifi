#!/usr/bin/python

"""
Topologia Mininet-WiFi: Rede básica com 2 estações e 1 AP
Autor: Script gerado para simulação de rede sem fio
Componentes:
- 2 estações sem fio (sta1, sta2)
- 1 ponto de acesso (ap1) - canal 1, alcance 30m
- 1 controlador SDN (c0)
"""

# Importações necessárias do Mininet-WiFi
from mininet.node import Controller
from mininet.log import setLogLevel, info
from mn_wifi.net import Mininet_wifi
from mn_wifi.node import OVSKernelAP
from mn_wifi.cli import CLI
from mn_wifi.link import wmediumd
from mn_wifi.wmediumdConnector import interference

def topologia_simples():
    """Função principal que cria e executa a topologia"""
    
    info("*** Criando rede Mininet-WiFi\n")
    # Inicializa a rede com controlador e tipo de AP especificados
    net = Mininet_wifi(controller=Controller, accessPoint=OVSKernelAP)
    
    info("*** Adicionando controlador SDN\n")
    # Cria controlador SDN padrão na porta 6653
    c0 = net.addController('c0', controller=Controller, port=6653)
    
    info("*** Adicionando ponto de acesso\n")
    # Cria AP com SSID, modo 802.11g, canal 1 e alcance de 30 metros
    ap1 = net.addAccessPoint('ap1', 
                             ssid='rede-simples',
                             mode='g',
                             channel='1',
                             position='50,50,0',
                             range=30)
    
    info("*** Adicionando estações sem fio\n")
    # Cria primeira estação com IP e posição definidos
    sta1 = net.addStation('sta1',
                          ip='10.0.0.1/24',
                          mac='00:00:00:00:00:01',
                          position='40,50,0')
    
    # Cria segunda estação com IP e posição definidos
    sta2 = net.addStation('sta2',
                          ip='10.0.0.2/24',
                          mac='00:00:00:00:00:02',
                          position='60,50,0')
    
    info("*** Configurando modelo de propagação\n")
    # Define modelo de propagação para simulação realista do sinal
    net.setPropagationModel(model="logDistance", exp=3.5)
    
    info("*** Configurando parâmetros Wi-Fi dos nós\n")
    # Habilita e configura os parâmetros sem fio de todas as estações e APs
    net.configureWifiNodes()
    
    info("*** Criando links entre estações e ponto de acesso\n")
    # As estações se associam automaticamente ao AP baseado na proximidade
    # Opcionalmente, pode-se criar links explícitos:
    # net.addLink(sta1, ap1)
    # net.addLink(sta2, ap1)
    
    info("*** Iniciando a rede\n")
    # Constrói a topologia
    net.build()
    
    # Inicia o controlador
    c0.start()
    
    # Inicia o ponto de acesso e o conecta ao controlador
    ap1.start([c0])
    
    info("*** Testando conectividade entre todas as estações\n")
    # Executa teste de ping entre todos os nós
    net.pingAll()
    
    info("*** Executando testes de desempenho\n")
    # Teste de largura de banda entre sta1 e sta2
    net.iperf((sta1, sta2))
    
    info("*** Iniciando CLI do Mininet-WiFi\n")
    info("Comandos úteis:\n")
    info("  pingall       - Testa conectividade entre todos os nós\n")
    info("  iperf sta1 sta2 - Mede largura de banda entre estações\n")
    info("  sta1 ifconfig - Mostra configuração de rede da sta1\n")
    info("  sta1 ping sta2 - Ping entre estações específicas\n")
    info("  exit          - Encerra a simulação\n")
    
    # Inicia interface de linha de comando interativa
    CLI(net)
    
    info("*** Parando a rede\n")
    # Encerra a rede e limpa as configurações
    net.stop()

if __name__ == '__main__':
    # Define o nível de logging para informações detalhadas
    setLogLevel('info')
    
    # Executa a função de criação da topologia
    topologia_simples()