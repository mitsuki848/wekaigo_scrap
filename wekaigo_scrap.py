import sys
import os
import re
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
# from tqdm.notebook import tqdm
from tqdm import tqdm


# ===================================
# ===実施回・問題番号・タイトルパターン確認　関数===
def impla_pattern_check(driver):
    elems_h1 = driver.find_elements(By.XPATH,
                                    '/html/body/div[1]/div[1]/div/main/div/h1')
    if len(elems_h1) == 0:
        # print(f'{sys._getframe().f_code.co_name}エラー')
        print(f'len(elems_h1) = {len(elems_h1)}')
        print(driver.current_url)
        driver.quit()
        sys.exit()

    inner_elems_h1 = elems_h1[0].find_elements(By.XPATH, '*')
    tag_list = []
    for i in range(len(inner_elems_h1)):
        tag_list.append(inner_elems_h1[i].tag_name)

    if tag_list == ['span', 'span']:
        impla_pattern = 'I-A'
    else:
        # print(f'{sys._getframe().f_code.co_name}エラー')
        print(f'新しいパターン {tag_list}')
        print(driver.current_url)
        driver.quit()
        sys.exit()

    return impla_pattern


# ===質問内容パターン確認　関数===
def question_pattern_check(driver):
    elems_section = driver.find_elements(By.TAG_NAME, 'section')
    if len(elems_section) == 0:
        # print(f'{sys._getframe().f_code.co_name}エラー')
        print(f'len(elems_section) = {len(elems_section)}')
        print(driver.current_url)
        driver.quit()
        sys.exit()

    inner_section_elems = elems_section[0].find_elements(By.XPATH, '*')
    tag_list = []
    for i in range(len(inner_section_elems)):
        tag_list.append(inner_section_elems[i].tag_name)

    if tag_list == ['p', 'ol', 'span', 'div']:
        question_pattern = 'Q-A'
    elif tag_list == ['p', 'ol', 'p', 'span', 'div']:
        question_pattern = 'Q-A'
    elif tag_list == ['p', 'p', 'p', 'ol', 'span', 'div']:
        question_pattern = 'Q-A'
    elif tag_list == ['p', 'p', 'br', 'img', 'p', 'ol', 'span', 'div']:
        question_pattern = 'Q-A'

    elif tag_list == ['span', 'p', 'p', 'p', 'p', 'ol', 'span', 'div']:
        question_pattern = 'Q-B'
    elif tag_list == ['span', 'p', 'p', 'ol', 'span', 'div']:
        question_pattern = 'Q-B'
    elif tag_list == ['span', 'p', 'p', 'ol', 'p', 'span', 'div']:
        question_pattern = 'Q-B'

    else:
        # print(f'{sys._getframe().f_code.co_name}エラー')
        print(f'新しいパターン {tag_list}')
        print(driver.current_url)
        driver.quit()
        sys.exit()

    return question_pattern


# ===質問画像URLパターン確認　関数===
def question_img_url_pattern_check(driver):
    elems_section = driver.find_elements(By.TAG_NAME, 'section')
    if len(elems_section) == 0:
        # print(f'{sys._getframe().f_code.co_name}エラー')
        print(f'len(elems_section) = {len(elems_section)}')
        print(driver.current_url)
        driver.quit()
        sys.exit()

    first_inner_section_elems = elems_section[0].find_elements(By.XPATH, '*')
    first_tag_list = []
    for i in range(len(first_inner_section_elems)):
        first_tag_name = first_inner_section_elems[i].tag_name
        first_tag_list.append(first_tag_name)

    second_inner_section_elems = elems_section[0].find_elements(By.XPATH, '*/*')
    second_tag_list = []
    for j in range(len(second_inner_section_elems)):
        second_tag_name = second_inner_section_elems[j].tag_name
        second_tag_list.append(second_tag_name)

    tag_list = first_tag_list + second_tag_list

    if tag_list.count('img') == 0:
        question_img_url_pattern = 'QI_0'
    elif tag_list.count('img') == 1:
        question_img_url_pattern = 'QI_1'
    else:
        # print(f'{sys._getframe().f_code.co_name}エラー')
        print(f'新しいパターン {tag_list.count}')
        print(driver.current_url)
        driver.quit()
        sys.exit()

    return question_img_url_pattern


# ===選択肢パターン確認　関数===
def choice_pattern_check(driver):
    elems_licence = driver.find_elements(By.CSS_SELECTOR,
                                         '.box-licence.font-sm')
    if len(elems_licence) != 1:
        # print(f'{sys._getframe().f_code.co_name}エラー')
        print(f'len(elems_licence) = {len(elems_licence)}')
        print(driver.current_url)
        driver.quit()
        sys.exit()

    inner_licence_elems = elems_licence[0].find_elements(By.XPATH, '*')

    tag_list = []
    for i in range(len(inner_licence_elems)):
        tag_list.append(inner_licence_elems[i].tag_name)

    if tag_list == ['li', 'li', 'li', 'li', 'li']:
        choice_pattern = 'CH-A'
    else:
        # print(f'{sys._getframe().f_code.co_name}エラー')
        print(f'新しいパターン {tag_list}')
        print(driver.current_url)
        driver.quit()
        sys.exit()

    return choice_pattern


# ===解答パターン確認　関数===
def answer_pattern_check(driver):
    elem_answer_box = driver.find_elements(By.CLASS_NAME, 'answer-box')
    if len(elem_answer_box) != 1:
        # print(f'{sys._getframe().f_code.co_name}エラー')
        print(f'len(elem_answer_box) = {len(elem_answer_box)}')
        print(driver.current_url)
        driver.quit()
        sys.exit()

    elem_answer_box_div = elem_answer_box[0].find_elements(By.CSS_SELECTOR,
                                                           '.bg-danger-light.radius-xl-top.p-lg')
    inner_div_elems = elem_answer_box_div[0].find_elements(By.XPATH, '*')
    tag_list = []
    for i in range(len(inner_div_elems)):
        tag_list.append(inner_div_elems[i].tag_name)

    if tag_list == ['p', 'p']:
        answer_pattern = 'A-A'
    elif tag_list == ['p', 'p', 'p']:
        answer_pattern = 'A-A'
    else:
        # print(f'{sys._getframe().f_code.co_name}エラー')
        print(f'新しいパターン {tag_list}')
        print(driver.current_url)
        driver.quit()
        sys.exit()

    return answer_pattern


# ===解説パターン確認　関数===
def commentary_pattern_check(driver):
    elem_bg_licence = driver.find_elements(By.CLASS_NAME, 'bg-licence')
    if len(elem_bg_licence) != 1:
        # print(f'{sys._getframe().f_code.co_name}エラー')
        print(f'len(elem_answer_box) = {len(elem_bg_licence)}')
        print(driver.current_url)
        driver.quit()
        sys.exit()
    inner_licence_elems = elem_bg_licence[0].find_elements(By.XPATH, '*')
    tag_list = []
    for i in range(len(inner_licence_elems)):
        tag_list.append(inner_licence_elems[i].tag_name)

    if tag_list == ['div', 'div', 'div', 'div', 'div']:
        commentary_pattern = 'C-A'
    elif tag_list == ['p', 'p', 'br', 'br', 'p']:
        commentary_pattern = 'C-B'
    elif tag_list == ['p', 'p', 'br', 'p']:
        commentary_pattern = 'C-B'
    elif tag_list == ['p']:
        commentary_pattern = 'C-B'
    else:
        # print(f'{sys._getframe().f_code.co_name}エラー')
        print(f'新しいパターン {tag_list}')
        print(driver.current_url)
        driver.quit()
        sys.exit()
    return commentary_pattern


# ----------------------------------

# ===実施回・問題番号・タイトル取得　関数===
def impla_pattern_i_a(driver):
    elems_h1 = driver.find_elements(By.XPATH,
                                    '/html/body/div[1]/div[1]/div/main/div/h1')
    impla_txt = elems_h1[0].find_element(By.XPATH, 'span[1]').get_attribute(
        'textContent')
    # 取得文字列の空白削除
    impla_txt = re.sub(r'\s', '', impla_txt)

    elems_inner_span = elems_h1[0].find_element(By.XPATH, 'span[2]')
    question_number = elems_inner_span.find_element(By.XPATH,
                                                    'span[1]').get_attribute(
        'textContent')
    # 取得文字列の空白削除
    question_number = re.sub(r'\s', '', question_number)

    question_title = elems_inner_span.find_element(By.XPATH,
                                                   'span[2]').get_attribute(
        'textContent')
    # 取得文字列の空白削除
    question_title = re.sub(r'\s', '', question_title)

    number_title = f'{question_number} {question_title}'

    return impla_txt, number_title


# ===質問内容取得　関数===
def question_pattern_q_a(driver):
    elems_section = driver.find_elements(By.TAG_NAME, 'section')
    inner_section_elems = elems_section[0].find_elements(By.XPATH, '*')

    # テキスト取得
    question_txt = inner_section_elems[0].get_attribute('textContent')
    # 取得文字列の空白削除
    question_txt = re.sub(r'\s', '', question_txt)

    # 取得確認
    if question_txt == '':
        # print(f'{sys._getframe().f_code.co_name}エラー')
        print(driver.current_url)
        driver.quit()
        sys.exit()

    return question_txt


def question_pattern_q_b(driver):
    elems_section = driver.find_elements(By.TAG_NAME, 'section')
    inner_section_elems = elems_section[0].find_elements(By.XPATH, '*')

    # olタグ位置確認
    tag_list = []
    for i in range(len(inner_section_elems)):
        tag_list.append(inner_section_elems[i].tag_name)
    ol_tag_index = tag_list.index('ol')

    # テキスト取得
    question_txt = ''
    for j in range(ol_tag_index):
        txt = inner_section_elems[j].get_attribute('textContent')
        # 取得文字列の空白削除
        txt = re.sub(r'\s', '', txt)
        if txt != '':
            question_txt += f'{txt}, '

    # 取得確認
    if question_txt == '':
        # print(f'{sys._getframe().f_code.co_name}エラー')
        print(driver.current_url)
        driver.quit()
        sys.exit()

    question_txt = question_txt[:-2]

    return question_txt


# ===質問画像URL取得　関数===
def question_img_url_qi_1(driver):
    elems_section = driver.find_elements(By.TAG_NAME, 'section')
    if len(elems_section) == 0:
        # print(f'{sys._getframe().f_code.co_name}エラー')
        print(f'len(elems_section) = {len(elems_section)}')
        print(driver.current_url)
        driver.quit()
        sys.exit()

    img_url = ''
    first_inner_section_elems = elems_section[0].find_elements(By.XPATH, '*')
    for i in range(len(first_inner_section_elems)):
        first_tag_name = first_inner_section_elems[i].tag_name

        if first_tag_name == 'img':
            img_url = first_inner_section_elems[i].get_attribute('src')

    second_inner_section_elems = elems_section[0].find_elements(By.XPATH, '*/*')
    for j in range(len(second_inner_section_elems)):
        second_tag_name = second_inner_section_elems[j].tag_name

        if second_tag_name == 'img':
            img_url = second_inner_section_elems[j].get_attribute('src')

    return img_url


# ===選択肢取得　関数===
def choice_pattern_ch_a(driver):
    elems_licence = driver.find_elements(By.CSS_SELECTOR,
                                         '.box-licence.font-sm')
    inner_licence_elems = elems_licence[0].find_elements(By.XPATH, '*')

    choice_number_list = []
    choice_text_list = []
    for i in range(len(inner_licence_elems)):
        choice_txt = inner_licence_elems[i].get_attribute('textContent')
        # 取得文字列の空白削除
        choice_txt = re.sub(r'\s', '', choice_txt)

        if choice_txt == '':
            # print(f'{sys._getframe().f_code.co_name}エラー')
            print(driver.current_url)
            driver.quit()
            sys.exit()

        choice_number = choice_txt[0]
        choice_number_list.append(choice_number)
        choice_text = choice_txt[1:]
        choice_text_list.append(choice_text)

    return choice_number_list, choice_text_list


# ===解答(番号)取得　関数===
def answer_pattern_a_a(driver):
    elem_answer_box = driver.find_elements(By.CLASS_NAME, 'answer-box')
    elem_answer_box_div = elem_answer_box[0].find_elements(By.CSS_SELECTOR,
                                                           '.bg-danger-light.radius-xl-top.p-lg')

    answer_title_elem = elem_answer_box_div[0].find_element(By.CLASS_NAME,
                                                            'answer-title')

    title_span_elems = answer_title_elem.find_elements(By.TAG_NAME, 'span')

    answer_number_list = []
    for i in range(len(title_span_elems)):
        answer_number = title_span_elems[i].get_attribute('textContent')
        # 取得文字列の空白削除
        answer_number = re.sub(r'\s', '', answer_number)

        if answer_number == '':
            # print(f'{sys._getframe().f_code.co_name}エラー')
            print(driver.current_url)
            driver.quit()
            sys.exit()

        answer_number_list.append(answer_number)

    return answer_number_list  # リスト型にしてリストに含まれているかで判断


# ===成否判断　関数===
def success_or_failure(choice_number_list, answer_number_list):
    success_or_failure_list = []
    for choice in choice_number_list:
        if choice in answer_number_list:
            answer = f'{choice} 正解'
        else:
            answer = f'{choice} 不正解'
        success_or_failure_list.append(answer)

    return success_or_failure_list


# ===解説取得　関数===
def commentary_pattern_c_a(driver):
    elem_bg_licence = driver.find_elements(By.CLASS_NAME, 'bg-licence')
    inner_licence_elems = elem_bg_licence[0].find_elements(By.XPATH, '*')

    commentary_list = []
    for i in range(len(inner_licence_elems)):
        commentary_content = inner_licence_elems[i].find_element(By.XPATH,
                                                                 'li[3]').get_attribute(
            'textContent')
        # 取得文字列の空白削除
        commentary_content = re.sub(r'\s', '', commentary_content)
        if commentary_content == '':
            # print(f'{sys._getframe().f_code.co_name}エラー')
            print(driver.current_url)
            driver.quit()
            sys.exit()

        commentary_list.append(commentary_content)

    return commentary_list


def commentary_pattern_c_b(driver):
    elem_bg_licence = driver.find_elements(By.CLASS_NAME, 'bg-licence')
    commentary_txt = elem_bg_licence[0].get_attribute('textContent')
    # 取得文字列の空白削除
    commentary_txt = re.sub(r'\s', '', commentary_txt)
    if commentary_txt == '':
        # print(f'{sys._getframe().f_code.co_name}エラー')
        print(driver.current_url)
        driver.quit()
        sys.exit()

    return commentary_txt


# ===================================



col_list = ['実施回', '問題とタイトル', '質問内容', '成否（各アンサー）', '選択肢', '解説',
            '画像URL']
df = pd.DataFrame(columns=col_list)

# このファイルと同じディレクトリに.wdmフォルダを作成し、
# そこにchromedriverが保存されるようにする
os.environ['WDM_LOCAL'] = '1'
# ------------------------------

options = Options()
# options.set_capability("pageLoadStrategy", "eager")
options.add_argument('--headless')

# # 対象サイトアクセス
# driver = webdriver.Chrome(
#     service=Service(ChromeDriverManager().install()),
#     options=options)
# driver.implicitly_wait(10)
# driver.get('https://kaigo.ten-navi.com/licence-kaigo/')

# 対象サイトアクセス
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
driver.implicitly_wait(10)
driver.get('https://kaigo.ten-navi.com/licence-kaigo/')

# 　過去問URL取得
zisshikai_a_list = driver.find_elements(By.XPATH,
                                        '/html/body/div[1]/div[1]/div/aside/div/ol[1]/a')
if len(zisshikai_a_list) == 0:
    print('「過去問URL取得」zisshikai_a_listを正しく取得出来ていない')
    driver.quit()
    sys.exit()

zisshikai_url_list = []
for i in range(len(zisshikai_a_list)):
    zisshikai_url = zisshikai_a_list[i].get_attribute('href')
    zisshikai_url_list.append(zisshikai_url)

driver.quit()
time.sleep(3)

img_url_list = []
# 実施回アクセス
for zisshikai_i in tqdm(range(len(zisshikai_url_list))):
# for zisshikai_i in tqdm(range(3)):
    # driver = webdriver.Chrome(
    #     service=Service(ChromeDriverManager().install()),
    #     options=options)
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    driver.implicitly_wait(10)
    driver.get(zisshikai_url_list[zisshikai_i])

    # 問題のURL取得
    mondai_li_list = driver.find_elements(By.XPATH,
                                          '/html/body/div[1]/div[1]/div/main/div/section/ol/li')
    if len(mondai_li_list) == 0:
        print('「問題のURL取得」mondai_li_listを正しく取得出来ていない')
        print(driver.current_url)
        driver.quit()
        sys.exit()

    mondai_url_list = []
    for mondai_li_i in range(len(mondai_li_list)):
        mondai_a = mondai_li_list[mondai_li_i].find_elements(By.XPATH, 'a')
        if len(mondai_a) != 1:
            print('「問題のURL取得」mondai_aを正しく取得出来ていない')
            print(driver.current_url)
            driver.quit()
            sys.exit()
        mondai_url = mondai_a[0].get_attribute('href')
        if 'http' not in mondai_url:
            print('「問題のURL取得」mondai_urlを正しく取得出来ていない')
            print(driver.current_url)
            driver.quit()
            sys.exit()
        mondai_url_list.append(mondai_url)

    driver.quit()
    time.sleep(3)

    # 各問題アクセス
    for mondai_i in tqdm(range(len(mondai_url_list))):
    # for mondai_i in tqdm(range(3)):
        # driver = webdriver.Chrome(
        #     service=Service(ChromeDriverManager().install()),
        #     options=options)
        driver = webdriver.Chrome(ChromeDriverManager().install(),
                                  options=options)

        driver.implicitly_wait(10)
        mondai_access_url = mondai_url_list[mondai_i]
        driver.get(mondai_access_url)

        # ===各パターン確認===
        impla_pattern = impla_pattern_check(driver)
        question_pattern = question_pattern_check(driver)
        question_img_url_pattern = question_img_url_pattern_check(driver)
        choice_pattern = choice_pattern_check(driver)
        answer_pattern = answer_pattern_check(driver)
        commentary_pattern = commentary_pattern_check(driver)

        # ===実施回・問題番号・タイトル取得===
        if impla_pattern == 'I-A':
            zissikai = impla_pattern_i_a(driver)[0]
            mondai = impla_pattern_i_a(driver)[1]
        else:
            print('impla_pattern認識エラー')
            print(driver.current_url)
            driver.quit()
            sys.exit()

        # ===質問内容取得===
        if question_pattern == 'Q-A':
            situmon = question_pattern_q_a(driver)
        elif question_pattern == 'Q-B':
            situmon = question_pattern_q_b(driver)
        else:
            print('question_pattern認識エラー')
            print(driver.current_url)
            driver.quit()
            sys.exit()

        # ===画像URL取得===
        if question_img_url_pattern == 'QI_0':
            img_url = ''
        elif question_img_url_pattern == 'QI_1':
            img_url = question_img_url_qi_1(driver)
            img_url_list.append(img_url)
        else:
            print('question_img_url_pattern認識エラー')
            print(driver.current_url)
            driver.quit()
            sys.exit()

        # ===選択肢取得===
        if choice_pattern == 'CH-A':
            choice_number_list, choice_text_list = choice_pattern_ch_a(driver)
        else:
            print('choice_pattern認識エラー')
            print(driver.current_url)
            driver.quit()
            sys.exit()

        # ===解答取得===
        if answer_pattern == 'A-A':
            answer_number_list = answer_pattern_a_a(driver)
        else:
            print('answer_pattern認識エラー')
            print(driver.current_url)
            driver.quit()
            sys.exit()

        seihi = success_or_failure(choice_number_list,
                                   answer_number_list)

        # ===解説取得===
        if commentary_pattern == 'C-A':
            kaisetu = commentary_pattern_c_a(driver)
        elif commentary_pattern == 'C-B':
            kaisetu = commentary_pattern_c_b(driver)
        else:
            print('commentary_pattern認識エラー')
            print(driver.current_url)
            driver.quit()
            sys.exit()

        driver.quit()
        time.sleep(3)

        dic = {'実施回': zissikai, '問題とタイトル': mondai, '質問内容': situmon,
               '成否（各アンサー）': seihi, '選択肢': choice_text_list,
               '解説': kaisetu, '画像URL': img_url}

        df_ = pd.DataFrame(dic)
        df = pd.concat([df, df_]).reset_index(drop=True)

# csv保存
if not os.path.exists('csv'):
    os.mkdir('csv')
df.to_csv('csv/wekaigo.csv', encoding='UTF-8', errors='replace', index=False)


# ===画像保存　関数===
def save_file(path, file_name, data):
    # ファイルを保存するためのディレクトリを作成
    os.makedirs(path, exist_ok=True)

    # ファイルパスを生成
    file_paht = os.path.join(path, file_name)

    # 指定したフォルダに保存
    with open(file_paht, "wb") as f:
        f.write(data.content)


# ===画像保存===
# if not os.path.exists('img'):
#     os.mkdir('img')
for i in img_url_list:
    req_data = requests.get(i)
    file_name = i.split('/')[-1]

    # ファイルを保存する
    save_file(path='img/', file_name=file_name, data=req_data)

print('取得完了しました')
