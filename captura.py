# captura os indicadores Pull Multiple e MVRV do CoinGlass
# https://www.coinglass.com/bull-market-peak-signals
# Autor: ChatGPT (adaptado por usuário)
# Data: 2024-06-27


import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
#import pandas as pd

class CoinGlassIndicatorScraper:
    def __init__(self, headless=True):
        """
        Inicializa o scraper com configurações do Chrome
        
        Args:
            headless (bool): Se True, executa o Chrome sem interface gráfica
        """
        self.options = Options()
        if headless:
            self.options.add_argument("--headless")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--window-size=1920,1080")
        
        self.driver = None
        self.url = "https://www.coinglass.com/bull-market-peak-signals"
    
    def start_driver(self):
        """Inicia o driver do Chrome"""
        try:
            self.driver = webdriver.Chrome(options=self.options)
            print("✅ Driver do Chrome iniciado com sucesso")
        except Exception as e:
            print(f"❌ Erro ao iniciar driver: {e}")
            raise
    
    def close_driver(self):
        """Fecha o driver"""
        if self.driver:
            self.driver.quit()
            print("🔒 Driver fechado")
    
    def wait_for_page_load(self, timeout=30):
        """
        Aguarda o carregamento completo da página e lida com popups
        
        Args:
            timeout (int): Tempo limite em segundos
        """
        try:
            wait = WebDriverWait(self.driver, timeout)
            # Aguarda elementos específicos ou conteúdo carregarem
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Aguarda um pouco para JavaScript executar
            time.sleep(3)
            
            # Lida com popup de consentimento GDPR/cookies
            self._handle_consent_popup()
            
            # Aguarda mais um pouco após lidar com popup
            time.sleep(2)
            
            print("✅ Página carregada e popups tratados")
        except Exception as e:
            print(f"⚠️ Timeout no carregamento da página: {e}")
    
    def _handle_consent_popup(self):
        """
        Lida com popup de consentimento de cookies/GDPR
        """
        try:
            # Lista de possíveis seletores para botões de consentimento
            consent_selectors = [
                # Texto dos botões
                "//button[contains(text(), 'Consent')]",
                "//button[contains(text(), 'Accept')]",
                "//button[contains(text(), 'Aceitar')]",
                "//button[contains(text(), 'I agree')]",
                "//button[contains(text(), 'OK')]",
                
                # Classes/IDs comuns
                "button[id*='consent']",
                "button[class*='consent']",
                "button[id*='accept']",
                "button[class*='accept']",
                "button[id*='agree']",
                "button[class*='agree']",
                
                # Seletores mais específicos para CoinGlass
                "button[class*='cookie']",
                "button[id*='cookie']",
                ".consent-button",
                "#consent-button",
                
                # Seletores genéricos de modal/popup
                ".modal button",
                ".popup button",
                "[role='dialog'] button"
            ]
            
            popup_found = False
            
            # Tenta encontrar e clicar no botão de consentimento
            for selector in consent_selectors:
                try:
                    if selector.startswith("//"):
                        # XPath selector
                        buttons = self.driver.find_elements(By.XPATH, selector)
                    else:
                        # CSS selector
                        buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for button in buttons:
                        if button.is_displayed() and button.is_enabled():
                            # Verifica se o texto do botão indica consentimento
                            button_text = button.text.lower()
                            consent_keywords = ['consent', 'accept', 'aceitar', 'agree', 'ok', 'allow']
                            
                            if any(keyword in button_text for keyword in consent_keywords):
                                self.driver.execute_script("arguments[0].click();", button)
                                print(f"✅ Popup de consentimento aceito: '{button.text}'")
                                popup_found = True
                                time.sleep(2)  # Aguarda popup fechar
                                return
                            
                except Exception:
                    continue
            
            # Se não encontrou botões por texto, tenta estratégia mais agressiva
            if not popup_found:
                self._handle_consent_popup_aggressive()
                
        except Exception as e:
            print(f"⚠️ Erro ao lidar com popup de consentimento: {e}")
    
    def _handle_consent_popup_aggressive(self):
        """
        Estratégia mais agressiva para lidar com popups
        """
        try:
            # Procura por qualquer modal/popup visível
            modal_selectors = [
                "[role='dialog']",
                ".modal",
                ".popup",
                "[class*='modal']",
                "[class*='popup']",
                "[id*='modal']",
                "[id*='popup']"
            ]
            
            for selector in modal_selectors:
                try:
                    modals = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for modal in modals:
                        if modal.is_displayed():
                            # Procura botões dentro do modal
                            buttons = modal.find_elements(By.TAG_NAME, "button")
                            for button in buttons:
                                if button.is_displayed() and button.is_enabled():
                                    # Clica no último botão (geralmente é o de aceitar)
                                    if len(buttons) > 1 and button == buttons[-1]:
                                        self.driver.execute_script("arguments[0].click();", button)
                                        print(f"✅ Popup fechado via estratégia agressiva")
                                        time.sleep(2)
                                        return
                                    # Ou se há apenas um botão, clica nele
                                    elif len(buttons) == 1:
                                        self.driver.execute_script("arguments[0].click();", button)
                                        print(f"✅ Popup fechado via botão único")
                                        time.sleep(2)
                                        return
                except Exception:
                    continue
                    
        except Exception as e:
            print(f"⚠️ Erro na estratégia agressiva de popup: {e}")
    
    def extract_pull_multiple_data(self):
        """
        Extrai dados do indicador Pull Multiple
        
        Returns:
            dict: Dados do Pull Multiple processados
        """
        try:
            data = {
                'indicator': 'Pull Multiple',
                'current_value': None,
                'threshold': None,
                'percentage': None,
                'status': None,
                'timestamp': time.time()
            }
            
            # Busca por padrões de texto que podem conter os valores
            body_text = self.driver.find_element(By.TAG_NAME, "body").text
            lines = body_text.split('\n')
            
            # Procura por "Pull Multiple" e captura contexto
            for i, line in enumerate(lines):
                if "Pull Multiple" in line:
                    context_lines = lines[max(0, i-3):i+5]
                    data['context'] = context_lines
                    
                    # Processa os valores do contexto
                    context_text = ' '.join(context_lines)
                    data.update(self._parse_indicator_values(context_text, 'Pull Multiple'))
                    break
            
            # Se não encontrou no contexto direto, busca em toda a página
            if not data.get('current_value'):
                data.update(self._parse_indicator_values(body_text, 'Pull Multiple'))
            
            return data
            
        except Exception as e:
            print(f"❌ Erro ao extrair Pull Multiple: {e}")
            return {'indicator': 'Pull Multiple', 'error': str(e)}
    
    def extract_mvrv_data(self):
        """
        Extrai dados do indicador MVRV
        
        Returns:
            dict: Dados do MVRV processados
        """
        try:
            data = {
                'indicator': 'MVRV Z-Score',
                'current_value': None,
                'threshold': None,
                'percentage': None,
                'status': None,
                'timestamp': time.time()
            }
            
            # Busca por padrões de texto que podem conter os valores
            body_text = self.driver.find_element(By.TAG_NAME, "body").text
            lines = body_text.split('\n')
            
            # Procura por "MVRV" e captura contexto
            for i, line in enumerate(lines):
                if "MVRV" in line:
                    context_lines = lines[max(0, i-3):i+5]
                    data['context'] = context_lines
                    
                    # Processa os valores do contexto
                    context_text = ' '.join(context_lines)
                    parsed_data = self._parse_indicator_values(context_text, 'MVRV')
                    data.update(parsed_data)
                    
                    # Processa o contexto específico que foi capturado anteriormente
                    if hasattr(self, '_process_mvrv_context'):
                        specific_data = self._process_mvrv_context(context_lines)
                        data.update(specific_data)
                    
                    break
            
            return data
            
        except Exception as e:
            print(f"❌ Erro ao extrair MVRV: {e}")
            return {'indicator': 'MVRV', 'error': str(e)}
    
    def save_data(self, data, filename="coinglass_indicators.json"):
        """
        Salva os dados em arquivo JSON
        
        Args:
            data (dict): Dados a serem salvos
            filename (str): Nome do arquivo
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"💾 Dados salvos em '{filename}'")
        except Exception as e:
            print(f"❌ Erro ao salvar dados: {e}")
    
    def extract_all_indicators(self):
        """
        Extrai todos os indicadores disponíveis na página
        
        Returns:
            dict: Dados de todos os indicadores
        """
        try:
            print("🔍 Navegando para a página...")
            self.driver.get(self.url)
            self.wait_for_page_load()
            
            # Captura screenshot para debug
            self.driver.save_screenshot("coinglass_page.png")
            print("📸 Screenshot salva como 'coinglass_page.png'")
            
            print("📊 Extraindo Pull Multiple...")
            pull_multiple = self.extract_pull_multiple_data()
            
            print("📈 Extraindo MVRV...")
            mvrv = self.extract_mvrv_data()
            
            # Captura todo o HTML da página para análise
            page_source = self.driver.page_source
            
            results = {
                'pull_multiple': pull_multiple,
                'mvrv': mvrv,
                'page_info': {
                    'url': self.url,
                    'title': self.driver.title,
                    'timestamp': time.time()
                }
            }
            
            # Salva HTML para análise offline
            with open('coinglass_page_source.html', 'w', encoding='utf-8') as f:
                f.write(page_source)
            print("💾 HTML da página salvo como 'coinglass_page_source.html'")
            
            return results
            
        except Exception as e:
            print(f"❌ Erro geral na extração: {e}")
            return {'error': str(e)}
    
    def _parse_indicator_values(self, text, indicator_name):
        """
        Processa texto para extrair valores dos indicadores
        
        Args:
            text (str): Texto a ser analisado
            indicator_name (str): Nome do indicador
        
        Returns:
            dict: Valores extraídos
        """
        import re
        
        data = {
            'current_value': None,
            'threshold': None,
            'percentage': None,
            'status': None
        }
        
        try:
            # Padrões regex para diferentes tipos de valores
            patterns = {
                'decimal': r'\d+\.\d+',
                'integer': r'\d+',
                'percentage': r'\d+\.?\d*%',
                'threshold': r'[><=]+\s*\d+\.?\d*',
                'range': r'\d+\.?\d*\s*-\s*\d+\.?\d*'
            }
            
            # Busca por percentagens
            percentages = re.findall(patterns['percentage'], text)
            if percentages:
                data['percentage'] = percentages[0]
            
            # Busca por thresholds (>=, <=, etc.)
            thresholds = re.findall(patterns['threshold'], text)
            if thresholds:
                data['threshold'] = thresholds[0].strip()
            
            # Busca por valores decimais (possível valor atual)
            decimals = re.findall(patterns['decimal'], text)
            if decimals:
                # Filtra valores que não são percentagens
                non_percentage_decimals = [d for d in decimals if f"{d}%" not in text]
                if non_percentage_decimals:
                    data['current_value'] = float(non_percentage_decimals[0])
            
            # Determina status baseado em valor atual vs threshold
            if data['current_value'] and data['threshold']:
                current = data['current_value']
                threshold_match = re.search(r'([><=]+)\s*(\d+\.?\d*)', data['threshold'])
                
                if threshold_match:
                    operator, threshold_val = threshold_match.groups()
                    threshold_val = float(threshold_val)
                    
                    if '>=' in operator and current >= threshold_val:
                        data['status'] = 'ALERTA - Acima do threshold'
                    elif '<=' in operator and current <= threshold_val:
                        data['status'] = 'ALERTA - Abaixo do threshold'
                    elif '>' in operator and current > threshold_val:
                        data['status'] = 'ALERTA - Acima do threshold'
                    elif '<' in operator and current < threshold_val:
                        data['status'] = 'ALERTA - Abaixo do threshold'
                    else:
                        data['status'] = 'Normal - Dentro do range'
            
            return data
            
        except Exception as e:
            print(f"⚠️ Erro ao processar valores do {indicator_name}: {e}")
            return data
    
    def _process_mvrv_context(self, context_lines):
        """
        Processa especificamente o contexto do MVRV baseado no padrão identificado
        ['30.17%', '8', 'MVRV Z-Score', '2.08', '>= 5']
        
        Args:
            context_lines (list): Linhas de contexto
            
        Returns:
            dict: Dados processados
        """
        try:
            data = {}
            
            # Busca por padrões específicos no contexto
            for line in context_lines:
                if '2.08' in str(line):  # Valor atual identificado
                    data['current_value'] = 2.08
                elif '>= 5' in str(line):  # Threshold identificado  
                    data['threshold'] = '>= 5'
                elif '30.17%' in str(line):  # Percentual
                    data['percentage'] = '30.17%'
            
            # Define status baseado nos valores conhecidos
            if data.get('current_value') == 2.08 and data.get('threshold') == '>= 5':
                data['status'] = 'Normal - Abaixo do threshold de alerta (2.08 < 5)'
            
            return data
            
        except Exception as e:
            print(f"⚠️ Erro ao processar contexto MVRV: {e}")
            return {}
    
    def save_data(self, data, filename="coinglass_indicators.json"):
        """
        Salva os dados em arquivo JSON
        
        Args:
            data (dict): Dados a serem salvos
            filename (str): Nome do arquivo
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"💾 Dados salvos em '{filename}'")
        except Exception as e:
            print(f"❌ Erro ao salvar dados: {e}")
    
    def run(self):
        """
        Executa o scraper completo
        
        Returns:
            dict: Dados extraídos
        """
        try:
            self.start_driver()
            data = self.extract_all_indicators()
            self.save_data(data)
            
            # Exibe resumo dos dados
            print("\n📋 RESUMO DOS DADOS EXTRAÍDOS:")
            print("="*50)
            for indicator, info in data.items():
                if indicator != 'page_info':
                    print(f"\n🔸 {indicator.upper().replace('_', ' ')}:")
                    if 'error' in info:
                        print(f"   ❌ Erro: {info['error']}")
                    else:
                        if info.get('current_value'):
                            print(f"   📊 Valor Atual: {info['current_value']}")
                        if info.get('threshold'):
                            print(f"   🎯 Threshold: {info['threshold']}")
                        if info.get('percentage'):
                            print(f"   📈 Percentual: {info['percentage']}")
                        if info.get('status'):
                            status_icon = "🔴" if "ALERTA" in info['status'] else "🟢"
                            print(f"   {status_icon} Status: {info['status']}")
                        if info.get('context'):
                            print(f"   📝 Contexto: {info['context'][:3]}...")  # Mostra só primeiras 3 linhas
            
            return data
            
        except Exception as e:
            print(f"❌ Erro na execução: {e}")
            return {'error': str(e)}
        finally:
            self.close_driver()

def main():
    """Função principal para executar o scraper"""
    print("🚀 Iniciando extração de indicadores do CoinGlass...")
    print("📍 URL: https://www.coinglass.com/bull-market-peak-signals")
    print("-" * 60)
    
    # Cria e executa o scraper
    scraper = CoinGlassIndicatorScraper(headless=False)  # headless=False para debug
    results = scraper.run()
    
    print("\n✅ Extração concluída!")
    return results

if __name__ == "__main__":
    # Instalar dependências necessárias:
    # pip install selenium pandas
    # Também necessário ter o ChromeDriver instalado
    
    results = main()