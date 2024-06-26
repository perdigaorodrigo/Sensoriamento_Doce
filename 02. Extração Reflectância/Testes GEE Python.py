import ee
import csv
import datetime
import pandas as pd
# Inicializar a API do Earth Engine
ee.Authenticate()
ee.Initialize()

# Função para extrair valores de pixels para cada ponto
def extrair_valores_pontos(ponto):
    # Converter a tupla de entrada em um ee.Geometry.Point
    ponto_gee = ee.Geometry.Point([ponto[2], ponto[1]])
    
    # Converter a data para um formato aceitável pelo Earth Engine
    data = ee.Date(ponto[3])
    
    # Definir uma janela de tempo para a imagem (por exemplo, 1 dia antes e depois da data)
    janela_tempo = ee.DateRange(data.advance(-2, 'day'), data.advance(2, 'day'))
    
    # Filtrar a coleção de imagens para a janela de tempo e ponto de interesse
    colecao_imagens = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
                        .filterBounds(ponto_gee) \
                        .filterDate(janela_tempo)
    
    # Verificar se a coleção de imagens filtrada contém alguma imagem
    num_imagens = colecao_imagens.size().getInfo()
    if num_imagens == 0:
        return (ponto[0], None, None, None)  # Retorna None se nenhuma imagem for encontrada
    
    # Se houver imagens, use a primeira imagem na coleção
    imagem = colecao_imagens.first()
    
    # Extrair o valor do pixel para o ponto de interesse
    valor_pixel = imagem.reduceRegion(reducer=ee.Reducer.first(), geometry=ponto_gee, scale=10)
    
    # Extrair a data e hora da imagem
    data_imagem = ee.Date(imagem.get('system:time_start'))
    data_imagem_string = data_imagem.format('Y-M-d-hh-mm-ss').getInfo()
    return (ponto[0], valor_pixel.select(['B3', 'B4', 'B5', 'B6', 'B8']), data_imagem_string)  

# Caminho para o arquivo CSV
caminho_arquivo_csv = r'C:\Users\rodri\Desktop\pontos.csv'

# Lista para armazenar os pontos do arquivo CSV
lista_de_pontos = []

# Ler o arquivo CSV e extrair os pontos
with open(caminho_arquivo_csv, 'r') as arquivo_csv:
    leitor_csv = csv.reader(arquivo_csv)
    # Pule o cabeçalho se houver
    next(leitor_csv, None)
    for linha in leitor_csv:
        # Extrair id, latitude, longitude e data
        ponto = (linha[0], float(linha[1]), float(linha[2]), linha[3])
        lista_de_pontos.append(ponto)

# Iterar sobre a lista de pontos e extrair os valores dos pixels
valores_dos_pixels = [extrair_valores_pontos(ponto) for ponto in lista_de_pontos]

# Criar um dicionário para armazenar os resultados
resultados = {'ID': [], 'B3': [], 'B4': [], 'B5': [], 'B6': [], 'B8': [], 'Data_Hora_Imagem': []}

# Preencher o dicionário com os valores dos pixels e a data e hora da imagem
for id_ponto, valor_pixel, data_hora_imagem in valores_dos_pixels:
    resultados['ID'].append(id_ponto)
    if valor_pixel is not None:
        resultados['B3'].append(valor_pixel.get('B3').getInfo())
        resultados['B4'].append(valor_pixel.get('B4').getInfo())
        resultados['B5'].append(valor_pixel.get('B5').getInfo())
        resultados['B6'].append(valor_pixel.get('B6').getInfo())
        resultados['B8'].append(valor_pixel.get('B8').getInfo())
    else:
        resultados['B3'].append(None)
        resultados['B4'].append(None)
        resultados['B5'].append(None)
        resultados['B6'].append(None)
        resultados['B8'].append(None)
    resultados['Data_Hora_Imagem'].append(data_hora_imagem)

# Criar um DataFrame pandas com os resultados
df = pd.DataFrame(resultados)

# Salvar o DataFrame em um arquivo CSV
df.to_csv('valores_pixels_datahora.csv', index=False)

print("Tabela salva com sucesso!")