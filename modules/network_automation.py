"""
Network and Web Automation Module

Handles web searches, data scraping, API interactions, and network management.
"""

import requests
import logging
import json
import time
import urllib.parse
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from bs4 import BeautifulSoup
import subprocess
import platform

class NetworkAutomation:
    """Handles network and web automation tasks"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.driver = None
    
    def web_search(self, query: str, num_results: int = 10, search_engine: str = "google") -> List[Dict[str, str]]:
        """
        Perform a web search and return results
        
        Args:
            query: Search query
            num_results: Number of results to return
            search_engine: Search engine to use (google, bing, duckduckgo)
        """
        try:
            if search_engine.lower() == "google":
                return self._google_search(query, num_results)
            elif search_engine.lower() == "bing":
                return self._bing_search(query, num_results)
            elif search_engine.lower() == "duckduckgo":
                return self._duckduckgo_search(query, num_results)
            else:
                self.logger.error(f"Unsupported search engine: {search_engine}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error performing web search: {e}")
            return []
    
    def _google_search(self, query: str, num_results: int) -> List[Dict[str, str]]:
        """Perform Google search using web scraping"""
        try:
            # Use DuckDuckGo as it's more scraping-friendly
            return self._duckduckgo_search(query, num_results)
        except Exception as e:
            self.logger.error(f"Error in Google search: {e}")
            return []
    
    def _bing_search(self, query: str, num_results: int) -> List[Dict[str, str]]:
        """Perform Bing search"""
        try:
            url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}"
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            results = []
            
            # Parse Bing search results
            for result in soup.find_all('li', class_='b_algo')[:num_results]:
                try:
                    title_elem = result.find('h2')
                    link_elem = result.find('a')
                    desc_elem = result.find('p')
                    
                    if title_elem and link_elem:
                        results.append({
                            'title': title_elem.get_text().strip(),
                            'url': link_elem.get('href', ''),
                            'description': desc_elem.get_text().strip() if desc_elem else '',
                            'source': 'Bing'
                        })
                except Exception as e:
                    self.logger.warning(f"Error parsing Bing result: {e}")
                    continue
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in Bing search: {e}")
            return []
    
    def _duckduckgo_search(self, query: str, num_results: int) -> List[Dict[str, str]]:
        """Perform DuckDuckGo search"""
        try:
            url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            results = []
            
            # Parse DuckDuckGo search results
            for result in soup.find_all('div', class_='result')[:num_results]:
                try:
                    title_elem = result.find('a', class_='result__a')
                    desc_elem = result.find('a', class_='result__snippet')
                    
                    if title_elem:
                        results.append({
                            'title': title_elem.get_text().strip(),
                            'url': title_elem.get('href', ''),
                            'description': desc_elem.get_text().strip() if desc_elem else '',
                            'source': 'DuckDuckGo'
                        })
                except Exception as e:
                    self.logger.warning(f"Error parsing DuckDuckGo result: {e}")
                    continue
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in DuckDuckGo search: {e}")
            return []
    
    def scrape_website(self, url: str, selectors: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Scrape data from a website
        
        Args:
            url: Website URL to scrape
            selectors: CSS selectors for different data elements
        """
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            if selectors:
                data = {}
                for key, selector in selectors.items():
                    elements = soup.select(selector)
                    if elements:
                        data[key] = [elem.get_text().strip() for elem in elements]
                    else:
                        data[key] = []
                return data
            else:
                # Return basic page information
                return {
                    'title': soup.title.string if soup.title else '',
                    'headings': [h.get_text().strip() for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])],
                    'links': [{'text': a.get_text().strip(), 'url': a.get('href', '')} for a in soup.find_all('a', href=True)],
                    'images': [img.get('src', '') for img in soup.find_all('img', src=True)],
                    'text': soup.get_text().strip()
                }
                
        except Exception as e:
            self.logger.error(f"Error scraping website {url}: {e}")
            return {}
    
    def api_request(self, url: str, method: str = "GET", headers: Dict[str, str] = None, 
                   data: Dict[str, Any] = None, params: Dict[str, str] = None) -> Tuple[bool, Dict[str, Any]]:
        """
        Make an API request
        
        Args:
            url: API endpoint URL
            method: HTTP method (GET, POST, PUT, DELETE)
            headers: Additional headers
            data: Request body data
            params: URL parameters
        """
        try:
            request_headers = self.session.headers.copy()
            if headers:
                request_headers.update(headers)
            
            if method.upper() == "GET":
                response = self.session.get(url, headers=request_headers, params=params)
            elif method.upper() == "POST":
                response = self.session.post(url, headers=request_headers, json=data, params=params)
            elif method.upper() == "PUT":
                response = self.session.put(url, headers=request_headers, json=data, params=params)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=request_headers, params=params)
            else:
                self.logger.error(f"Unsupported HTTP method: {method}")
                return False, {}
            
            response.raise_for_status()
            
            # Try to parse JSON response
            try:
                return True, response.json()
            except json.JSONDecodeError:
                return True, {'text': response.text}
                
        except Exception as e:
            self.logger.error(f"Error making API request to {url}: {e}")
            return False, {'error': str(e)}
    
    def setup_selenium_driver(self, browser: str = "chrome", headless: bool = True) -> bool:
        """Setup Selenium WebDriver"""
        try:
            if browser.lower() == "chrome":
                options = Options()
                if headless:
                    options.add_argument("--headless")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-gpu")
                
                self.driver = webdriver.Chrome(options=options)
                
            elif browser.lower() == "firefox":
                options = FirefoxOptions()
                if headless:
                    options.add_argument("--headless")
                
                self.driver = webdriver.Firefox(options=options)
                
            else:
                self.logger.error(f"Unsupported browser: {browser}")
                return False
            
            self.logger.info(f"Setup {browser} WebDriver successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting up WebDriver: {e}")
            return False
    
    def close_selenium_driver(self):
        """Close Selenium WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.logger.info("Closed WebDriver")
    
    def automate_web_interaction(self, url: str, actions: List[Dict[str, Any]]) -> bool:
        """
        Automate web interactions using Selenium
        
        Args:
            url: Website URL
            actions: List of actions to perform
        """
        try:
            if not self.driver:
                if not self.setup_selenium_driver():
                    return False
            
            self.driver.get(url)
            
            for action in actions:
                action_type = action.get('type')
                
                if action_type == 'click':
                    element = self.driver.find_element(By.CSS_SELECTOR, action['selector'])
                    element.click()
                    
                elif action_type == 'type':
                    element = self.driver.find_element(By.CSS_SELECTOR, action['selector'])
                    element.clear()
                    element.send_keys(action['text'])
                    
                elif action_type == 'wait':
                    time.sleep(action.get('seconds', 1))
                    
                elif action_type == 'wait_for_element':
                    WebDriverWait(self.driver, action.get('timeout', 10)).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, action['selector']))
                    )
                
                elif action_type == 'scroll':
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                
                elif action_type == 'screenshot':
                    self.driver.save_screenshot(action.get('filename', 'screenshot.png'))
                
                time.sleep(0.5)  # Small delay between actions
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error automating web interaction: {e}")
            return False
    
    def get_network_info(self) -> Dict[str, Any]:
        """Get network configuration information"""
        try:
            import socket
            import subprocess
            
            info = {
                'hostname': socket.gethostname(),
                'local_ip': socket.gethostbyname(socket.gethostname()),
            }
            
            # Get public IP
            try:
                response = self.session.get('https://api.ipify.org', timeout=5)
                info['public_ip'] = response.text.strip()
            except:
                info['public_ip'] = 'Unable to determine'
            
            # Get network interfaces (platform specific)
            if platform.system().lower() == "windows":
                try:
                    result = subprocess.run(['ipconfig'], capture_output=True, text=True)
                    info['interfaces'] = result.stdout
                except:
                    pass
            else:
                try:
                    result = subprocess.run(['ifconfig'], capture_output=True, text=True)
                    info['interfaces'] = result.stdout
                except:
                    pass
            
            return info
            
        except Exception as e:
            self.logger.error(f"Error getting network info: {e}")
            return {}
    
    def test_connectivity(self, host: str, port: int = None, timeout: int = 5) -> bool:
        """Test network connectivity to a host"""
        try:
            import socket
            
            if port:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                result = sock.connect_ex((host, port))
                sock.close()
                return result == 0
            else:
                # Test DNS resolution
                socket.gethostbyname(host)
                return True
                
        except Exception as e:
            self.logger.error(f"Error testing connectivity to {host}: {e}")
            return False
    
    def download_file(self, url: str, filename: str = None, chunk_size: int = 8192) -> bool:
        """Download a file from URL"""
        try:
            response = self.session.get(url, stream=True)
            response.raise_for_status()
            
            if not filename:
                filename = url.split('/')[-1]
            
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    f.write(chunk)
            
            self.logger.info(f"Downloaded file: {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error downloading file from {url}: {e}")
            return False
    
    def get_weather_info(self, city: str, api_key: str = None) -> Dict[str, Any]:
        """Get weather information for a city"""
        try:
            if not api_key:
                # Use a free weather API (you might want to get your own API key)
                url = f"https://wttr.in/{urllib.parse.quote(city)}?format=j1"
                response = self.session.get(url)
                response.raise_for_status()
                return response.json()
            else:
                # Use OpenWeatherMap API
                url = f"http://api.openweathermap.org/data/2.5/weather"
                params = {
                    'q': city,
                    'appid': api_key,
                    'units': 'metric'
                }
                success, data = self.api_request(url, params=params)
                return data if success else {}
                
        except Exception as e:
            self.logger.error(f"Error getting weather info for {city}: {e}")
            return {}
    
    def monitor_website(self, url: str, check_interval: int = 300) -> bool:
        """Monitor a website for changes (basic implementation)"""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            # Simple content hash check
            content_hash = hash(response.text)
            
            # In a real implementation, you would store this hash and compare
            # with previous checks to detect changes
            self.logger.info(f"Website {url} monitored - Content hash: {content_hash}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error monitoring website {url}: {e}")
            return False
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.close_selenium_driver()
