"""Genera las seis capturas de la rubrica con Selenium y Chrome."""

import time
from pathlib import Path
from urllib.request import urlopen

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as conditions
from selenium.webdriver.support.ui import Select, WebDriverWait


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "evidencias"
FRONTEND_URL = "http://localhost:5500"
HEALTH_URL = "http://localhost:8400/api/health"


def ensure_services() -> None:
    try:
        with urlopen(HEALTH_URL, timeout=3) as response:
            if response.status != 200:
                raise RuntimeError("Health check no exitoso")
        with urlopen(FRONTEND_URL, timeout=3) as response:
            if response.status != 200:
                raise RuntimeError("Frontend no exitoso")
    except Exception as error:
        raise SystemExit(
            "Inicie Uvicorn en :8400 y 'python -m http.server 5500' en frontend."
        ) from error


def capture(driver: webdriver.Chrome, filename: str) -> None:
    driver.execute_script("document.getElementById('toast').className = 'toast'")
    width = driver.execute_script("return document.documentElement.scrollWidth")
    height = driver.execute_script("return document.documentElement.scrollHeight")
    driver.set_window_size(max(1440, width), max(1000, height + 260))
    driver.save_screenshot(str(OUTPUT / filename))
    print(f"Creada: docs/evidencias/{filename}")


def main() -> None:
    ensure_services()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1440,1000")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 12)
    try:
        driver.get(FRONTEND_URL)
        wait.until(conditions.text_to_be_present_in_element((By.ID, "backendStatus"), "conectada"))
        capture(driver, "01_inicio.png")

        Select(driver.find_element(By.ID, "exampleSelect")).select_by_value("4")
        driver.find_element(By.ID, "loadExampleBtn").click()
        wait.until(conditions.text_to_be_present_in_element((By.ID, "mazeTitle"), "Trampa para DFS"))
        capture(driver, "02_laberinto_predefinido.png")

        driver.find_element(By.ID, "bfsBtn").click()
        wait.until(conditions.text_to_be_present_in_element((By.ID, "resultState"), "Ruta encontrada"))
        time.sleep(0.9)
        capture(driver, "03_bfs_resultado.png")

        driver.find_element(By.ID, "dfsBtn").click()
        wait.until(conditions.text_to_be_present_in_element((By.ID, "metricAlgorithm"), "DFS"))
        time.sleep(0.9)
        capture(driver, "04_dfs_resultado.png")

        driver.find_element(By.ID, "compareBtn").click()
        wait.until(conditions.visibility_of_element_located((By.ID, "comparisonBlock")))
        time.sleep(0.9)
        capture(driver, "05_comparacion.png")

        Select(driver.find_element(By.ID, "exampleSelect")).select_by_value("5")
        driver.find_element(By.ID, "loadExampleBtn").click()
        driver.find_element(By.ID, "compareBtn").click()
        wait.until(conditions.text_to_be_present_in_element((By.ID, "resultState"), "Sin ruta"))
        time.sleep(0.9)
        capture(driver, "06_sin_ruta.png")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
