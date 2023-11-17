import csv
import json
from dataclasses import dataclass, asdict, fields

from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.select import Select

SJO_URL = "https://ssl.sjo.pw.edu.pl/index.php/oferta"
OUT_CSV = "courses.csv"
OUT_JSON = "courses.json"


@dataclass
class Course:
    usos_code: str
    symbol: str
    language: str
    level: str
    module: str
    type: str
    title: str
    teacher: str
    time: str


def dataclass_from_dict(class_name, data_dict: dict):
    field_set = {f.name for f in fields(class_name) if f.init}
    filtered_args = {k: v for k, v in data_dict.items() if k in field_set}
    return class_name(**filtered_args)


def process_row(tr_element: WebElement, language_name: str) -> Course:
    cells = tr_element.find_elements(By.TAG_NAME, "td")
    values = [cell.text for cell in cells]
    return Course(
        language=language_name,
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
        language_name = extract_name(select, idx)

        button = driver.find_element(By.NAME, btn_name)
        button.click()

        table_rows = [
            *driver.find_elements(By.CLASS_NAME, "even"),
            *driver.find_elements(By.CLASS_NAME, "odd"),
        ]
        courses.extend([process_row(row, language_name) for row in table_rows])

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


def extract_name(select: Select, idx: int) -> str:
    name = select.options[idx].accessible_name
    return name.split()[0]


def save_to_csv(filename: str, courses: list[Course]):
    with open(filename, mode="w", encoding="utf-8") as out_file:
        fieldnames = list(asdict(courses[0]).keys())
        writer = csv.DictWriter(out_file, fieldnames=fieldnames)
        writer.writeheader()
        for course in courses:
            writer.writerow(asdict(course))


def read_from_csv(filename: str) -> list[Course]:
    with open(filename, mode="r", encoding="utf-8") as in_file:
        reader = csv.DictReader(in_file)
        return [dataclass_from_dict(Course, row_dict) for row_dict in reader]


def save_to_json(filename: str, courses):
    with open(filename, mode="w", encoding="utf-8") as out_file:
        dict_courses = [asdict(course) for course in courses]
        json.dump(dict_courses, out_file)


def read_from_json(filename: str) -> list[Course]:
    with open(filename, mode="r", encoding="utf-8") as in_file:
        course_dicts = json.load(in_file)
        return [dataclass_from_dict(Course, cd) for cd in course_dicts]


def main():
    driver = webdriver.Chrome()
    print(f"Scraping {SJO_URL} for language course data")
    all_courses = scrape_course_list(driver, SJO_URL)
    print(f"Collected {len(all_courses)} courses in total")
    driver.quit()

    print(f"Saving result to {OUT_CSV}")
    save_to_csv(OUT_CSV, all_courses)
    print(f"Saved result to {OUT_CSV}")

    print(f"Saving result to {OUT_JSON}")
    save_to_json(OUT_JSON, all_courses)
    print(f"Saved result to {OUT_JSON}")


if __name__ == '__main__':
    main()
