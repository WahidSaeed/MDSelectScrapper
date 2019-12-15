from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

headings = list()

def add_headings(heading):
    if heading not in headings:
        headings.append(heading)

def get_heading_index(heading):
    return headings.index(heading)

def get_comma_seperated_placeholder():
    return ','.join(['{'+ str(index) +'}' for index, g in enumerate(headings)])

def get_comma_seperated_value(tuple_array):
    comma_seperated_placeholder = get_comma_seperated_placeholder()
    for _tuple in tuple_array:
        heading, value = _tuple
        heading_index = get_heading_index(heading)
        if heading_index > -1:
            comma_seperated_placeholder = comma_seperated_placeholder.replace('{'+ str(heading_index) + '}', '"' + value.replace('"', '""') + '"')
    return re.sub('{[0-9]*}', '', comma_seperated_placeholder)


def md_select_scrapper():
    driver = webdriver.Chrome('C:\\chromedriver.exe')

    driver.get('https://www.mdselect.ca/MDSelectGold/login.aspx?ReturnUrl=%2fmdselectgold%2fSearchDesigner.aspx')
    driver.find_element_by_id('ContentPlaceHolder1_Login1_UserName').send_keys('XXX@XXX.com')
    driver.find_element_by_id ('ContentPlaceHolder1_Login1_Password').send_keys('XXXX')
    login = driver.find_element_by_id('ContentPlaceHolder1_Login1_LoginButton')
    login.click()

    WebDriverWait(driver, 100).until(EC.staleness_of(login))

    print('INFO: Login Successfull\n')
    
    print('INFO: File profileDetials.csv has been accessed\n')

    driver.get('https://www.mdselect.ca/mdselectgold/searchcheckbox.aspx?id=3')
    driver.find_element_by_id('ContentPlaceHolder1_cblSearchItems_0').click()
    driver.find_element_by_id('ContentPlaceHolder1_cblSearchItems_1').click()
    driver.find_element_by_id('ContentPlaceHolder1_cblSearchItems_2').click()
    Search = driver.find_element_by_id('ContentPlaceHolder1_lnkBtnSearch')
    Search.click()

    WebDriverWait(driver, 100).until(EC.staleness_of(Search))

    table = driver.find_element_by_class_name('l_TableLines')
    td = table.find_elements_by_tag_name('td')
    a_Tag = td[1].find_element_by_tag_name('a')
    a_Tag.click()

    WebDriverWait(driver, 10).until(EC.staleness_of(a_Tag))

    print('INFO: Data Extraction Begins\n')

    record_no = 1
    notLastPage = True
    final_value = ''
    while notLastPage:
        table = driver.find_element_by_id('ContentPlaceHolder1_ScDetail1')
        trs = table.find_elements_by_tag_name('tr')
        _headings = table.find_elements_by_class_name('l_ColumnHead')
        for heading in _headings:
            if heading.text:
                add_headings(heading.text)
        row_value = []
        address = ''
        for tr in trs:
            tds = tr.find_elements_by_tag_name('td')
            if len(tds) == 4:
                heading_1 = tds[0]
                value_1 = tds[1]

                heading_2 = tds[2]
                value_2 = tds[3]

                if heading_1.text == '' or heading_1.text == 'Address:':
                    address = address + ' ' + value_1.text 
                else:
                    row_value.append((heading_1.text, value_1.text))

                if heading_2.text and value_2.text:
                    row_value.append((heading_2.text, value_2.text))

            elif len(tds) == 2:
                heading_1 = tds[0]
                value_1 = tds[1]

                if heading_1.text and value_1.text:
                    row_value.append((heading_1.text, value_1.text))

        row_value.append(('Address:', address))
        extracted_data = get_comma_seperated_value(row_value) + '\n'
        final_value = final_value + extracted_data
        print(extracted_data)
        print('INFO: ' + str(record_no) + ' record(s) has been extracted \n')
            
        nextPage = driver.find_element_by_id('ContentPlaceHolder1_imgNext')
        if nextPage:
            nextPage.click()
            WebDriverWait(driver, 20).until(EC.staleness_of(nextPage))
            record_no = record_no + 1
        else:
            notLastPage = False

    f= open("profileDetails.csv","w+")
    f.write(','.join([heading for heading in headings]) + '\n')
    f.write(final_value)
    f.close()


if __name__ == "__main__":
    md_select_scrapper()
