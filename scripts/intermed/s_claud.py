#!/usr/bin/python

"""
Topologia Mininet-WiFi: Rede com múltiplos APs e switch central
Autor: Script gerado para simulação de rede sem fio distribuída
Componentes:
- 4 estações sem fio (sta1, sta2, sta3, sta4)
- 2 pontos de acesso (ap1, ap2)
- 1 switch central (s1) interligando os APs
- 1 controlador SDN (c0)
Topologia: sta1,sta2 -> ap1 -> s1 <- ap2 <- sta3,sta4
"""

# Importações necessárias do Mininet-WiFi
from mininet.node import Controller, OVSKernelSwitch
from mininet.log import setLogLevel, info
from mn_wifi.net import Mininet_wifi
from mn_wifi.node import OVSKernelAP
from mn_wifi.cli import CLI
from mn_wifi.link import wmediumd
from mn_wifi.wmediumdConnector import interference

def topologia_multi_ap():
    """Função principal que cria topologia com múltiplos APs"""
    
    info("*** Criando rede Mininet-WiFi\n")
    # Inicializa a rede com controlador e tipos de nós especificados
    net = Mininet_wifi(controller=Controller, 
                       accessPoint=OVSKernelAP,
                       switch=OVSKernelSwitch)
    
    info("*** Adicionando controlador SDN\n")
    # Cria controlador SDN padrão
    c0 = net.addController('c0', controller=Controller, port=6653)
    
    info("*** Adicionando switch central\n")
    # Switch que interliga os dois pontos de acesso
    s1 = net.addSwitch('s1', protocols='OpenFlow13')
    
    info("*** Adicionando pontos de acesso\n")
    # Primeiro ponto de acesso (lado esquerdo da rede)
    ap1 = net.addAccessPoint('ap1',
                             ssid='rede-ap1',
                             mode='g',
                             channel='1',
                             position='30,50,0',
                             range=25)
    
    # Segundo ponto de acesso (lado direito da rede)
    ap2 = net.addAccessPoint('ap2',
                             ssid='rede-ap2',
                             mode='g',
                             channel='6',
                             position='70,50,0',
                             range=25)
    
    info("*** Adicionando estações sem fio\n")
    # Estações conectadas ao ap1
    sta1 = net.addStation('sta1',
                          ip='10.0.0.1/24',
                          mac='00:00:00:00:00:01',
                          position='20,40,0')
    
    sta2 = net.addStation('sta2',
                          ip='10.0.0.2/24',
                          mac='00:00:00:00:00:02',
                          position='20,60,0')
    
    # Estações conectadas ao ap2
    sta3 = net.addStation('sta3',
                          ip='10.0.0.3/24',
                          mac='00:00:00:00:00:03',
                          position='80,40,0')
    
    sta4 = net.addStation('sta4',
                          ip='10.0.0.4/24',
                          mac='00:00:00:00:00:04',
                          position='80,60,0')
    
    info("*** Configurando modelo de propagação\n")
    # Define modelo de propagação para simulação realista do sinal
    net.setPropagationModel(model="logDistance", exp=4)
    
    info("*** Configurando parâmetros Wi-Fi dos nós\n")
    # Habilita e configura os parâmetros sem fio
    net.configureWifiNodes()
    
    info("*** Criando links cabeados entre APs e switch\n")
    # Conecta ap1 ao switch central
    net.addLink(ap1, s1)
    
    # Conecta ap2 ao switch central
    net.addLink(ap2, s1)
    
    info("*** Associando estações aos pontos de acesso\n")
    # As estações se conectam automaticamente aos APs mais próximos
    # sta1 e sta2 -> ap1 (baseado na proximidade)
    # sta3 e sta4 -> ap2 (baseado na proximidade)
    
    info("*** Iniciando a rede\n")
    # Constrói a topologia
    net.build()
    
    # Inicia o controlador
    c0.start()
    
    # Inicia o switch central
    s1.start([c0])
    
    # Inicia os pontos de acesso e os conecta ao controlador
    ap1.start([c0])
    ap2.start([c0])
    
    info("*** Aguardando estabilização da rede\n")
    # Pausa para garantir que todas as conexões sejam estabelecidas
    import time
    time.sleep(2)
    
    info("*** Testando conectividade entre todas as estações\n")
    # Executa teste de ping entre todos os nós
    net.pingAll()
    
    info("*** Executando testes de desempenho inter-AP\n")
    # Teste de largura de banda entre estações de APs diferentes
    info("Teste entre sta1 (ap1) e sta3 (ap2):\n")
    net.iperf((sta1, sta3))
    
    info("\n*** Executando testes de desempenho intra-AP\n")
    # Teste de largura de banda entre estações do mesmo AP
    info("Teste entre sta1 e sta2 (mesmo AP):\n")
    net.iperf((sta1, sta2))
    
    info("\n*** Iniciando CLI do Mininet-WiFi\n")
    info("=" * 60 + "\n")
    info("Topologia criada com sucesso!\n")
    info("=" * 60 + "\n")
    info("Estrutura da rede:\n")
    info("  sta1, sta2 -> ap1 (SSID: rede-ap1, canal 1)\n")
    info("  sta3, sta4 -> ap2 (SSID: rede-ap2, canal 6)\n")
    info("  ap1, ap2 -> s1 (switch central)\n")
    info("=" * 60 + "\n")
    info("Comandos úteis:\n")
    info("  pingall              - Testa conectividade entre todos os nós\n")
    info("  sta1 ping sta3       - Ping entre estações de APs diferentes\n")
    info("  iperf sta1 sta4      - Mede largura de banda inter-AP\n")
    info("  sta1 ifconfig        - Mostra configuração de rede\n")
    info("  nodes                - Lista todos os nós da rede\n")
    info("  links                - Mostra todas as conexões\n")
    info("  dump                 - Exibe informações detalhadas dos nós\n")
    info("  exit                 - Encerra a simulação\n")
    info("=" * 60 + "\n")
    
    # Inicia interface de linha de comando interativa
    CLI(net)
    
    info("*** Parando a rede\n")
    # Encerra a rede e limpa as configurações
    net.stop()

if __name__ == '__main__':
    # Define o nível de logging para informações detalhadas
    setLogLevel('info')
    
    # Executa a função de criação da topologia
    topologia_multi_ap()