import re
import time
from bs4 import BeautifulSoup
from selenium import webdriver 
from selenium.webdriver.support.ui import Select


def get_exp_id(url):
    browser = webdriver.Chrome()
    browser.get(url)
    time.sleep(3)
    try:
        view_all = browser.find_element_by_xpath('//*[@id="content"]/div/div[3]/div/div/div[2]/table/tfoot/tr/td/div/a')
        view_all.click()
        time.sleep(3)
        html = browser.page_source
        browser.close()

        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find_all('p',attrs={'class': re.compile("^type$")})

        info = []
        for i in table:
            if re.search('ENCSR',i.string) != None:
                info.append(i.string.strip())
        return info
    
    except:
        html = browser.page_source
        browser.close()
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find_all('a')

        info = []
        info2 = []
        for i in table:
            info.append(i.get('href'))
        for j in info:
            if re.search('experiments',j) != None:
                j = j.split('/')
                info2.append(j[2])
        return info2


def get_bamfile_ID(experiment_ID):
    browser2 = webdriver.Chrome()
    browser2.get("https://www.encodeproject.org/experiments/" + experiment_ID)
    time.sleep(5)
    page2 = browser2.page_source
    soup2 = BeautifulSoup(page2, 'html.parser')
    biosamples = []
    biosam = soup2.find_all('a',attrs={"href":re.compile(r'^\/biosamples')})
    for i in biosam:
        biosamples.append(i.string)
    tmp = []
    for num in range(1,len(biosamples)+1):
        bio_num = browser2.find_element_by_xpath('//*[@id="content"]/div/div[2]/div[2]/table/tbody/tr[' + str(num) + ']/td[4]/a')
        bio_num.click()
        time.sleep(5)
        page3 = browser2.page_source
        soup3 = BeautifulSoup(page3, 'html.parser')
        donor_re = soup3.find_all('a',attrs={"href":re.compile(r'^\/human')})
        for i in donor_re:
            if i.string == donor:
                tmp.append(num)
        browser2.back()
        time.sleep(3)
        
    file_details = browser2.find_element_by_xpath("//li[@class='active']/following::*")
    file_details.click()
    time.sleep(1)

    select = Select(browser2.find_element_by_class_name('form-control--select'))
    select.select_by_value("1") 
    time.sleep(1)

    page4 = browser2.page_source
    browser2.close()
        
    soup4 = BeautifulSoup(page4, 'html.parser')
    span = soup4.find_all('span',{'class':'file-table-accession'})

    tr = []
    for i in span:
        new = str(i.previous_element.previous_element)
        tr.append(new)
    bam_ids = []
    for i in tr:
        if re.search('bam',i) != None:
            if re.search('unfiltered',i) == None:
                for t in tmp:
                    if re.search('<td>'+ str(tmp) + '</td>',i) != None:
                        new_i = i.split('/')
                        for j in new_i:
                            if re.search('^ENCFF\w{6}$',j) != None:
                                if j not in bam_ids:
                                    bam_ids.append(j)
    return bam_ids


def main(donor_ID):
    experiment_ID = get_exp_id('https://www.encodeproject.org/human-donors/' + donor_ID)
    bam_ids = []
    for ids in experiment_ID:
        try:
            list_bam = get_bamfile_ID(ids)
        except:
            list_bam = ['']            
        for i in list_bam:
            print(i)
        
with open('/Users/liying/Desktop/question.txt') as file:
    for donor in file:
        donor = donor.replace('\n','')
        print(donor)
        main(donor)
        print("=====================================================")
