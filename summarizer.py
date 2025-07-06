import os
import sys
import requests
import argparse
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

def resumir_texto(modelo, texto, idioma):
    """
    Envia o texto para o modelo Gemini e retorna o resumo no idioma especificado.
    """
    if not texto:
        return "Não foi possível extrair texto para resumir."
        
    print(f"Enviando texto para a IA para sumarização em {idioma}... Isso pode levar um momento.")
    
    prompt = f"Resuma o seguinte artigo de forma concisa e em {idioma}, focando nos pontos principais:\n\n{texto}"
    
    try:
        response = modelo.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Ocorreu um erro durante a sumarização: {e}"

def main():
    """
    Função principal que orquestra o processo de sumarização.
    """
    parser = argparse.ArgumentParser(description="Sumarizador de Artigos com IA usando Google Gemini.")
    parser.add_argument("url", help="A URL do artigo a ser resumido.")
    parser.add_argument("--language", default="português", help="O idioma do resumo (ex: 'inglês', 'espanhol'). O padrão é 'português'.")
    
    args = parser.parse_args()
    
    try:
        modelo = configurar_api()
        texto_artigo = extrair_texto_do_artigo(args.url)
        
        if texto_artigo:
            resumo = resumir_texto(modelo, texto_artigo, args.language)
            print(f"\n--- Resumo do Artigo (em {args.language.capitalize()}) ---")
            print(resumo)
            print("----------------------------------------------------\n")
            
    except ValueError as e:
        print(f"Erro de configuração: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()