from dataclasses import dataclass
from pprint import pprint

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.select import Select

SJO_URL = "https://ssl.sjo.pw.edu.pl/index.php/oferta"


@dataclass
class Course:
    usos_code: str
    symbol: str
    level: str
    module: str
    type: str
    title: str
    teacher: str
    time: str


def process_row(tr_element: WebElement) -> Course:
    cells = tr_element.find_elements(By.TAG_NAME, "td")
    values = [cell.text for cell in cells]
    return Course(
        usos_code=values[0],
        symbol=values[1],
        level=values[2],
        module=values[3],
        type=values[4],
        title=values[5],
        teacher=values[6],
        time=values[7]
    )


def main():
    all_courses = []

    driver = webdriver.Chrome()
    driver.get(SJO_URL)

    select_element = driver.find_elements(By.ID, "Jezyki_ID_JEZYKA")[0]
    select = Select(select_element)

    n_languages = len(select.options)
    for idx in range(1, n_languages):
        select_element = driver.find_elements(By.ID, "Jezyki_ID_JEZYKA")[0]
        select = Select(select_element)
        select.select_by_index(idx)
        button = driver.find_element(By.NAME, "yt0")
        button.click()

        table_rows = driver.find_elements(By.CLASS_NAME, "even") + driver.find_elements(By.CLASS_NAME, "odd")
        language_courses = [process_row(row) for row in table_rows]
        all_courses.extend(language_courses)

        driver.back()

    ##########################
    select_element = driver.find_elements(By.ID, "Jezyki_ID_JEZYKA")[1]
    select = Select(select_element)

    n_languages = len(select.options)
    for idx in range(1, n_languages):
        select_element = driver.find_elements(By.ID, "Jezyki_ID_JEZYKA")[1]
        select = Select(select_element)
        select.select_by_index(idx)
        button = driver.find_element(By.NAME, "yt1")
        button.click()

        table_rows = driver.find_elements(By.CLASS_NAME, "even") + driver.find_elements(By.CLASS_NAME, "odd")
        language_courses = [process_row(row) for row in table_rows]
        all_courses.extend(language_courses)

        driver.back()

    print(f"Collected {len(all_courses)} in total")
    pprint(all_courses)

    driver.quit()


if __name__ == '__main__':
    main()
