import time
import os
import json
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class LookfyCloner:
    def __init__(self, headless=False):
        """
        Inicializa o cloner da Lookfy
        
        Args:
            headless (bool): Se True, executa sem interface (não recomendado para login)
        """
        self.options = Options()
        if headless:
            self.options.add_argument("--headless")
        
        # Configurações para melhor captura
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--window-size=1920,1080")
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = None
        self.url = "https://app.lookfy.com.br/dashboard/looks"
        self.output_dir = "lookfy_clone"
        
    def start_driver(self):
        """Inicia o driver do Chrome"""
        try:
            self.driver = webdriver.Chrome(options=self.options)
            # Remove indicadores de automação
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            print("✅ Driver do Chrome iniciado")
            return True
        except Exception as e:
            print(f"❌ Erro ao iniciar driver: {e}")
            return False
    
    def close_driver(self):
        """Fecha o driver"""
        if self.driver:
            self.driver.quit()
            print("🔒 Driver fechado")
    
    def create_output_directory(self):
        """Cria diretório de saída"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            os.makedirs(f"{self.output_dir}/assets")
            os.makedirs(f"{self.output_dir}/css")
            os.makedirs(f"{self.output_dir}/js")
            print(f"📁 Diretório criado: {self.output_dir}")
    
    def manual_login(self):
        """
        Permite login manual do usuário
        """
        try:
            print("🌐 Navegando para a página de login...")
            self.driver.get(self.url)
            
            print("\n" + "="*60)
            print("🔐 FAÇA LOGIN MANUALMENTE")
            print("="*60)
            print("1. Complete o login na janela do navegador")
            print("2. Navegue até a página que deseja capturar")
            print("3. Aguarde tudo carregar completamente")
            print("4. Pressione ENTER aqui para continuar a captura")
            print("="*60)
            
            # Aguarda input do usuário
            input("\n⏳ Pressione ENTER após fazer login e carregar a página...")
            
            # Verifica se ainda está na URL correta
            current_url = self.driver.current_url
            print(f"📍 URL atual: {current_url}")
            
            # Aguarda um pouco mais para garantir carregamento completo
            print("⏳ Aguardando carregamento completo...")
            time.sleep(5)
            
            return True
            
        except Exception as e:
            print(f"❌ Erro durante login: {e}")
            return False
    
    def capture_page_source(self):
        """
        Captura o HTML completo da página após carregamento
        """
        try:
            print("📝 Capturando HTML da página...")
            
            # Aguarda elementos carregarem
            wait = WebDriverWait(self.driver, 30)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Scroll para garantir que todo conteúdo dinâmico carregue
            print("📜 Fazendo scroll para carregar conteúdo dinâmico...")
            self.driver.execute_script("""
                var scrollHeight = Math.max(
                    document.body.scrollHeight, 
                    document.documentElement.scrollHeight
                );
                window.scrollTo(0, scrollHeight);
            """)
            time.sleep(3)
            
            # Volta para o topo
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(2)
            
            # Captura HTML completo
            html_content = self.driver.page_source
            
            # Salva HTML
            with open(f"{self.output_dir}/index.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            
            print(f"✅ HTML salvo em: {self.output_dir}/index.html")
            return html_content
            
        except Exception as e:
            print(f"❌ Erro ao capturar HTML: {e}")
            return None
    
    def capture_screenshots(self):
        """
        Captura screenshots da página
        """
        try:
            print("📸 Capturando screenshots...")
            
            # Screenshot da viewport atual
            self.driver.save_screenshot(f"{self.output_dir}/screenshot_viewport.png")
            
            # Screenshot da página completa
            # Primeiro define tamanho da janela para capturar tudo
            total_width = self.driver.execute_script("return document.body.scrollWidth")
            total_height = self.driver.execute_script("return Math.max(document.body.scrollHeight, document.documentElement.scrollHeight);")
            
            self.driver.set_window_size(total_width, total_height)
            time.sleep(2)
            
            self.driver.save_screenshot(f"{self.output_dir}/screenshot_full_page.png")
            
            print("✅ Screenshots salvas:")
            print(f"   • {self.output_dir}/screenshot_viewport.png")
            print(f"   • {self.output_dir}/screenshot_full_page.png")
            
        except Exception as e:
            print(f"❌ Erro ao capturar screenshots: {e}")
    
    def extract_resources(self, html_content):
        """
        Extrai URLs de recursos (CSS, JS, imagens) do HTML usando regex
        
        Args:
            html_content (str): Conteúdo HTML da página
        """
        try:
            print("🔍 Extraindo recursos da página...")
            
            resources = {
                'css': [],
                'js': [],
                'images': [],
                'other': []
            }
            
            # CSS files - busca por link href com rel stylesheet
            css_pattern = r'<link[^>]+rel=["\']stylesheet["\'][^>]*href=["\']([^"\']+)["\']'
            css_matches = re.findall(css_pattern, html_content, re.IGNORECASE)
            resources['css'] = list(set(css_matches))  # Remove duplicatas
            
            # JavaScript files - busca por script src
            js_pattern = r'<script[^>]+src=["\']([^"\']+)["\']'
            js_matches = re.findall(js_pattern, html_content, re.IGNORECASE)
            resources['js'] = list(set(js_matches))
            
            # Images - busca por img src
            img_pattern = r'<img[^>]+src=["\']([^"\']+)["\']'
            img_matches = re.findall(img_pattern, html_content, re.IGNORECASE)
            resources['images'] = list(set(img_matches))
            
            # Background images em CSS inline
            bg_pattern = r'background-image:\s*url\(["\']?([^"\')]+)["\']?\)'
            bg_matches = re.findall(bg_pattern, html_content, re.IGNORECASE)
            resources['images'].extend(bg_matches)
            
            # Remove duplicatas das imagens
            resources['images'] = list(set(resources['images']))
            
            # Salva lista de recursos
            with open(f"{self.output_dir}/resources.json", "w", encoding="utf-8") as f:
                json.dump(resources, f, indent=2, ensure_ascii=False)
            
            print(f"📋 Recursos encontrados:")
            print(f"   • CSS: {len(resources['css'])} arquivos")
            print(f"   • JS: {len(resources['js'])} arquivos")
            print(f"   • Imagens: {len(resources['images'])} arquivos")
            
            return resources
            
        except Exception as e:
            print(f"❌ Erro ao extrair recursos: {e}")
            return None
    
    def capture_network_requests(self):
        """
        Captura requisições de rede para entender APIs
        """
        try:
            print("🌐 Capturando informações de rede...")
            
            # Executa JavaScript para capturar dados de performance
            performance_data = self.driver.execute_script("""
                var perfData = performance.getEntriesByType("navigation")[0];
                var resources = performance.getEntriesByType("resource");
                
                return {
                    navigation: {
                        loadComplete: perfData.loadEventEnd - perfData.navigationStart,
                        domContentLoaded: perfData.domContentLoadedEventEnd - perfData.navigationStart
                    },
                    resources: resources.map(function(r) {
                        return {
                            name: r.name,
                            type: r.initiatorType,
                            duration: r.duration,
                            size: r.transferSize || 0
                        };
                    })
                };
            """)
            
            # Salva dados de performance
            with open(f"{self.output_dir}/network_data.json", "w", encoding="utf-8") as f:
                json.dump(performance_data, f, indent=2, ensure_ascii=False)
            
            print("✅ Dados de rede salvos em: network_data.json")
            
        except Exception as e:
            print(f"❌ Erro ao capturar dados de rede: {e}")
    
    def create_offline_version(self, html_content):
        """
        Cria uma versão offline da página
        """
        try:
            print("🔧 Criando versão offline...")
            
            # Modifica HTML para versão offline
            modified_html = html_content
            
            # Remove scripts que podem causar erros
            modified_html = modified_html.replace('</head>', '''
    <style>
        /* Estilos para página offline */
        body::before {
            content: "⚠️ VERSÃO OFFLINE - Alguns recursos podem não funcionar";
            display: block;
            background: #ff6b6b;
            color: white;
            text-align: center;
            padding: 10px;
            font-weight: bold;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 99999;
        }
        body {
            padding-top: 50px;
        }
    </style>
</head>''')
            
            # Salva versão offline
            with open(f"{self.output_dir}/index_offline.html", "w", encoding="utf-8") as f:
                f.write(modified_html)
            
            print("✅ Versão offline criada: index_offline.html")
            
        except Exception as e:
            print(f"❌ Erro ao criar versão offline: {e}")
    
    def run(self):
        """
        Executa o processo completo de clonagem
        """
        try:
            print("🚀 Iniciando clonagem da página Lookfy...")
            print("="*60)
            
            # Preparação
            self.create_output_directory()
            
            if not self.start_driver():
                return False
            
            # Login manual
            if not self.manual_login():
                return False
            
            # Captura dados
            print("\n📊 Capturando dados da página...")
            html_content = self.capture_page_source()
            
            if html_content:
                self.capture_screenshots()
                self.extract_resources(html_content)
                self.capture_network_requests()
                self.create_offline_version(html_content)
                
                print("\n🎉 CLONAGEM CONCLUÍDA!")
                print("="*60)
                print(f"📁 Arquivos salvos em: {self.output_dir}/")
                print("📋 Arquivos criados:")
                print("   • index.html - HTML completo")
                print("   • index_offline.html - Versão offline")
                print("   • screenshot_viewport.png - Screenshot da tela")
                print("   • screenshot_full_page.png - Screenshot completo")
                print("   • resources.json - Lista de recursos")
                print("   • network_data.json - Dados de rede")
                print("="*60)
                
                return True
            else:
                print("❌ Falha na captura do HTML")
                return False
                
        except Exception as e:
            print(f"❌ Erro geral: {e}")
            return False
        finally:
            self.close_driver()

def main():
    """Função principal"""
    print("🎯 CLONADOR DE PÁGINA LOOKFY")
    print("📍 URL: https://app.lookfy.com.br/dashboard/looks")
    print("⚠️  IMPORTANTE: Você precisará fazer login manualmente!")
    print("-" * 60)
    
    # Pergunta se quer continuar
    response = input("Deseja continuar? (s/n): ").lower().strip()
    if response != 's':
        print("❌ Operação cancelada")
        return
    
    # Executa clonagem
    cloner = LookfyCloner(headless=False)  # Nunca headless para login manual
    success = cloner.run()
    
    if success:
        print("\n✅ Clonagem realizada com sucesso!")
        print("💡 Dica: Abra o arquivo 'index_offline.html' para ver a versão capturada")
    else:
        print("\n❌ Falha na clonagem")

if __name__ == "__main__":
    # Dependências necessárias:
    # pip install selenium beautifulsoup4
    main()