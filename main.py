from dataclasses import dataclass
from pprint import pprint

from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
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


def scrape_course_category(driver: WebDriver, select_tag_id: str, select_idx: int, btn_name: str) -> list[Course]:
    """This is for scraping either 'thematic language courses' or 'courses in languages other than English'"""
    courses = []
    select_element = driver.find_elements(By.ID, select_tag_id)[select_idx]
    select = Select(select_element)

    n_languages = len(select.options)
    for idx in range(1, n_languages):  # idx 0 is a filler
        select_element = driver.find_elements(By.ID, select_tag_id)[select_idx]
        select = Select(select_element)
        select.select_by_index(idx)

        button = driver.find_element(By.NAME, btn_name)
        button.click()

        table_rows = [
            *driver.find_elements(By.CLASS_NAME, "even"),
            *driver.find_elements(By.CLASS_NAME, "odd"),
        ]
        courses.extend([process_row(row) for row in table_rows])

        driver.back()

    return courses


def scrape_course_list(driver: WebDriver, page_url: str) -> list[Course]:
    driver.get(page_url)
    select_tag_id = "Jezyki_ID_JEZYKA"
    all_courses = [
        *scrape_course_category(driver, select_tag_id, 0, "yt0"),
        *scrape_course_category(driver, select_tag_id, 1, "yt1"),
    ]

    return all_courses


def main():
    driver = webdriver.Chrome()
    all_courses = scrape_course_list(driver, SJO_URL)

    print(f"Collected {len(all_courses)} in total")
    pprint(all_courses)

    driver.quit()


if __name__ == '__main__':
    main()
