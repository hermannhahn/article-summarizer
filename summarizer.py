import os
import sys
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from dotenv import load_dotenv

def configurar_api():
    """Carrega a chave da API do arquivo .env e configura o SDK do Gemini."""
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("A chave da API do Google não foi encontrada. Verifique seu arquivo .env.")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash')

def extrair_texto_do_artigo(url):
    """
    Acessa uma URL, baixa o conteúdo HTML e extrai o texto dos parágrafos.
    """
    print(f"Acessando o artigo em: {url}")
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()  # Lança um erro para respostas ruins (4xx ou 5xx)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extrai o texto de todas as tags <p>
        paragrafos = soup.find_all('p')
        texto_artigo = '\n'.join([p.get_text() for p in paragrafos])
        
        if not texto_artigo:
            print("Aviso: Nenhum texto de parágrafo (<p>) encontrado na página.")
            # Tenta uma abordagem mais genérica se <p> falhar
            return soup.get_text(separator='\n', strip=True)

        return texto_artigo
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar a URL: {e}")
        return None

def resumir_texto(modelo, texto):
    """
    Envia o texto para o modelo Gemini e retorna o resumo.
    """
    if not texto:
        return "Não foi possível extrair texto para resumir."
        
    print("Enviando texto para a IA para sumarização... Isso pode levar um momento.")
    
    prompt = "Resuma o seguinte artigo de forma concisa e em português, focando nos pontos principais:\n\n" + texto
    
    try:
        response = modelo.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Ocorreu um erro durante a sumarização: {e}"

def main():
    """
    Função principal que orquestra o processo de sumarização.
    """
    if len(sys.argv) < 2:
        print("Uso: python summarizer.py <URL_DO_ARTIGO>")
        sys.exit(1)
        
    url_artigo = sys.argv[1]
    
    try:
        modelo = configurar_api()
        texto_artigo = extrair_texto_do_artigo(url_artigo)
        
        if texto_artigo:
            resumo = resumir_texto(modelo, texto_artigo)
            print("\n--- Resumo do Artigo ---")
            print(resumo)
            print("------------------------\n")
            
    except ValueError as e:
        print(f"Erro de configuração: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()