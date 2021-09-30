'''
Работа парсера происходит следующим образом:
1. Отправляем закодированный .pdf файл в YandexVision;
2. Принимаем ответ в виде данных .json;
3. Находим первую строку с биомаркером;
4. Собираем все строки в промежуточный массив (result);
5. Приводим промежуточный массив в требуемый вид;
6. В массив - final_array записываем результат;
    Первым элементом final_array является переданные пользователем данные: sex, age, number, store_tag.

1) IAM_TOKEN для авторизации;
2) Имя файла;
3) Пол;
4) Возраст;
5) Номер телефона;
6) Тег магазина.
'''

import requests as req
import json
import base64
from sys import argv, exit
import string
import re
import math
import time
import random

class Text_Recognition:
    def __init__(self, token, file):
        self.token = token
        self.req_url = 'https://vision.api.cloud.yandex.net/vision/v1/batchAnalyze'
        self.headers = {'Authorization': 'Bearer ' + self.token, 'Content-Type': 'application/json'}
        self.inp_file = file

    def create_json(self):
        '''
        Формируем header для запроса.
        :return: объект вида .json.
        '''

        # Кодируем файл для отправки в YandexVision
        file = open(self.inp_file, 'rb').read()  #Файл должен быть: .pfd
        self.encoded_file = base64.b64encode(file)

        # Создаем шаблон для json
        self.json_template = {
            'analyze_specs': [{'content': str(self.encoded_file).replace('\'', '')[1:],
                               'mime_type': 'application/pdf',
                               'features': [{
                                   'type': 'TEXT_DETECTION',
                                   'text_detection_config': {
                                       'language_codes': ['*']
                                   }
                               }]}]
        }
        return json.dumps(self.json_template)


    def make_req(self, json_file):
        '''
        Посылаем запрос в YandexVision.
        :param json_file: Сформированный json файл
        :return: ответ запроса.
        '''
        self.requests_result = req.post(self.req_url, data=json_file, headers=self.headers)
        return self.requests_result



# Класс для форматирования массива
class Formate_respond:
    def __init__(self, file_name):
        data_dict = file_name
        self.templates_for_units = r'([0-9%°*\'~^]+[%°*\'~]*[\^]?[0-9]?[\/][а-яa-z]{1,5}|[г][і][л]|[%]|[А-Яа-я]+[\/][0-9]+|[А-Яа-я]{1,5}[\/][а-я]{1,5}|[пф][гл])'    # Шаблон для поиска биомаркеров
        self.list_of_blocks = data_dict['results'][0]['results'][0]['textDetection']['pages'][0]['blocks'] # Блоки по которым был прочитан текст
        self.biomarkers = ['25-oh', 'витамин d', 'кальций общий', 'ca total', 'хлор', 'cl', 'chloride',
                          'медь в крови', 'cu', 'магний', 'mg', 'magnesium', 'фосфор', 'phosphor-b', 'phosphorus',
                          'калий', 'k', 'potassium', 'натрий', 'na', 'sodium', 'цинк в крови', 'zn', 'активный b12',
                          'active-b12', 'алт', 'alt', 'альбумин', 'albumin', 'альфа-амилаза', 'amyl', 'аст', 'ast',
                          'asat',
                          'базофилы %', 'bas', 'билирубин непрямой', 'id-bil', 'билирубин общий', 'bil-t',
                          'билирубин прямой',
                          'd-bil', 'биологически доступный тестостерон', 'batc', 'витамин b6', 'vitamin b6',
                          'витамин b12',
                          'vitamin b12', 'ггт', 'гамма-глутамилтрансфераза', 'ggt', 'гематокрит', 'htc', 'гемоглобин',
                          'hb',
                          'hgd', 'гликированный гемоглобин', 'hba1c', 'глюкоза в крови натощак', 'glu', 'гомоцистеин',
                          'homocysteine', 'гспг', 'gspg', 'дгэа-с', 'железо — концентрация', 'fe',
                          'индекс свободных андрогенов',
                          'иса', 'инсулин натощак', 'insulin', 'йод в волосах', 'йод в моче',
                          'йод в моче - разовая порция',
                          'коэффициент атерогенности', 'ка', 'catr', 'кальций ионизированный', 'ca free',
                          'креатинин в крови',
                          'crea', 'лейкоциты', 'wbc', 'лептин', 'lep', 'лимфоциты', 'lymph', 'лпвп', 'hdl', 'лпнп',
                          'ldl',
                          'лпонп', 'vldl', 'моноциты', 'mo', 'мочевая кислота', 'ua', 'мочевина', 'ua',
                          'насыщение трансферрина % железом', 'нейтрофилы', 'neu', 'белок общий', 'total protein',
                          'холестерин общий', 'chol', 'ожсс', 'ширина распределения эритроцитов по объёму', 'rdw-cv',
                          'панкреатическая амилаза', 'pancreatic aml', 'прогестерон', 'oh', 'пролактин', 'prl',
                          'реверсивный т3', 't3 serum', 'кортизол в моче', 'hydrocortisone', 'свободный тестостерон',
                          'testosterone free', 'соотношение медь/цинк', 'cu/zn', 'соэ', 'с-пептид', 'cp',
                          'с-реактивный белок', 'crp', 'среднее содержание гемоглобина в эритроците', 'mch',
                          'средний объём тромбоцитов', 'mpv', 'средний объём эритроцитов', 'mcv',
                          'средняя концентрация гемоглобина в эритроцитах', 'mchc', 'т3 свободный', 'free t3',
                          'т4 свободный',
                          'тестостерон общий', 'testosterone total', 'трансферрин', 'transferrin', 'tf', 'триглицериды',
                          'trig', 'тромбоциты', 'plt', 'ттг', 'tsh', 'ферритин', 'ferritin', 's-fer', 'фибриноген',
                          'qfa',
                          'витамин b9', 'фолиевая кислота', 'vitamin b9', 'фолиевая кислота в эритроцитах',
                          'церулоплазмин',
                          'ceruloplasmin', 'щелочная фосфатаза', 'alp', 'эозинофилы', 'eos',
                          'эозинофильный катионный белок',
                          'ecp', 'эритроцит', 'rbc', 'эстрадиол', 'e2', 'estradiol', 'моноциты', 'mo', 'лимфоциты',
                           'lymph',
                          'базофилы', 'bas', 'эозинофилы', 'eos', 'нейтрофилы', 'neu', 'эритроцитов'
                          ] # Все возможные биомаркеры

    def find_position(self, biomarkers):
        '''
        Находим первый биомаркер и забираем его данные.
        :param biomarkers: набор всех возможных биомаркеров;
        :return: объект, первого найденного биомаркера.
        '''
        for block in self.list_of_blocks:
            block_lines = block['lines']
            for block_line in block_lines:
                words_inline = block_line['words']
                for word_line in words_inline:
                    if word_line['text'].lower() in biomarkers:
                        return word_line


    def gather_biomarkers(self, y1, y2):
        '''
        Собираем все строки.
        :param y1: левая нижняя координата слова
        :param y2: правая нижняя координата слова
        :return: n - строку, word_y1 - левая верхняя координата слова, word_y2 - левая нижняя координата слова
        '''
        n = []
        word_y1 = word_y2 = 0
        for block in self.list_of_blocks:
            block_lines = block['lines']
            for block_line in block_lines:
                words_inline = block_line['words']
                for word_line in words_inline:
                    enum = range(len(words_inline))
                    if int(word_line['boundingBox']['vertices'][0]['y']) >= y1 - 10 and \
                            int(word_line['boundingBox']['vertices'][1]['y']) <= y2 + 10:
                        n.append(word_line['text'])
                        if enum[0] == 0:
                            word_y1 = int(word_line['boundingBox']['vertices'][0]['y'])
                            word_y2 = int(word_line['boundingBox']['vertices'][1]['y'])
        return n, word_y1, word_y2


    def find_new_y1_y2(self, inp_y2):
        '''
        Метод находит ближайшую координату 'y' для следующей строки
        :param inp_y2: правая нижняя координата пердыдущего слова
        :return: word_y1 - левая нижняя координата нового слова
            word_y2 - правая нижняя координата нового слова
        '''
        res = 30
        out_y1 = out_y2 = 0
        for block in self.list_of_blocks:
            block_lines = block['lines']
            for block_line in block_lines:
                words_inline = block_line['words']
                for word_line in words_inline:
                    if math.fabs(int(word_line['boundingBox']['vertices'][0]['y']) - inp_y2) < res:
                        out_y1 = int(word_line['boundingBox']['vertices'][0]['y'])
                        out_y2 = int(word_line['boundingBox']['vertices'][1]['y'])
                        res = math.fabs(int(word_line['boundingBox']['vertices'][0]['y']) - inp_y2)
        return out_y1, out_y2

    # !!!! Переделать логику !!!!
    def concatenate_floats(self, array):
        '''
        Соединяем десятичные числа. Пример [..., '90.', '20', ...] -> [..., '90.20', ...].
        :param array: передаем промежуточный массив result;
        :return: Массив, в котором части десятичных чисел соединены в единое число.
        '''
        n = []
        for strr in array:
            for word in range(len(strr) - 1):
                if strr[word][-1] == '.' or strr[word][-1] == ',':
                    res = strr[word] + strr[word + 1]
                    strr[word] = res
                    strr[word + 1] = ' '
            n.append(strr)
        for strr in n:
            if ' ' in strr: strr.remove(' ')
        return n


    def replace_comma_and_brackets(self, array):
        '''
        Заменяем запятые на точки для десятичных значений и убираем скобки у элементов.
            Это нужно для того, чтобы метод checker() правильно возвращал результат.
        :param array: передаем промежуточный массив result;
        :return: возвращаем массив, в котором всё ',' заменено на '.' и в которых отсутствуют скобки.
        '''
        n = []
        for strr in array:
            for word in range(len(strr)):
                if ',' in strr[word]:
                    strr[word] = strr[word].replace(',', '.')
                if '(' in strr[word]:
                    strr[word] = strr[word].replace('(', '')
                if ')' in strr[word]:
                    strr[word] = strr[word].replace(')', '')
            n.append(strr)
        return n


    def concatenate_biomarkers(self, array):
        '''
        Предполагаем, что элементы биомаркера идут до первого числа и
            соединяем первые элементы биомаркеров в единое слово. Пример: ['Лейкоциты', 'WBC'] -> ['Лейкоциты WBC']
        :param array: передаем промежуточный массив result;
        :return: массив, где первые элементы биомаркера собраны в единое слово.
        '''
        n = []
        # Проверяем является ли строка числом или словом
        def checker(element):
            try:
                float(element)
                return True
            except ValueError:
                return False

        for element in array:
            first_part = element[0]
            new_arr = element[1:]
            while True:
                if not new_arr:
                    break
                elif not checker(new_arr[0]):
                    first_part += ' ' + new_arr[0]
                    new_arr = new_arr[1:]
                else:
                    break
            temp = [first_part]
            temp.extend(new_arr)
            if len(temp) > 4: n.append(temp)
        return n


    def find_biomarkers_value(self, array):
        '''
        Формируем массив со всеми результатами.
        :param array: передаем промежуточный массив result;
        :return: возвращаем массив значений биомаркера (результат).
        '''
        n = []
        for sttr in array:
            try:
                n.append(sttr[1])
            except Exception:
                n.append('0')
        return n


    def find_bottom_and_upper_lines(self, array):
        '''
        Если значение слева от '-': нижняя граница, если справа от '-': верхняя.
        :param array: передаем промежуточный массив result;
        :return: n_bottom - массив с нижними границами, n_upper = массив с верхними границами.
        '''
        n_bottom = []
        n_upper = []
        for strr in array:
            flag = False
            for word in range(len(strr)):
                if strr[word] == '-':
                    n_bottom.append(strr[word - 1])
                    n_upper.append(strr[word + 1])
                    flag = True
            if flag == False:
                n_bottom.append('отсутствует')
                n_upper.append('отсутствует')
        return n_bottom, n_upper

    def delete_excess_strings(self, array):
        '''
        Удаляем строки которые состоят из одной строки и т.д.
        :param array: Промежуточный массив result;
        :return:
        '''
        n = []
        for strr in array:
            if len(strr) < 2: continue
            n.append(strr)
        return n

    def find_units(self, array):
        '''
        Находим единицы измерения для каждого биомаркера, если его нет, то присваеваем None.
        :param array: Промежуточный массив result.
        :return: Возвращаем массив с единицами измерения
        '''
        def is_biom_units(temp):
            try:
                return temp[0]
            except Exception:
                return 'None'

        n = []
        for strr in array:
            temp = ''
            for element, item in enumerate(strr):
                temp = re.findall(self.templates_for_units, item)
                if temp: break
            n.append(is_biom_units(temp))
        return n

    def recognition_accuracy(self):
        '''
        Определяем точность распознавания;
        :return: точность распознавания.
        '''
        n = []
        for block in self.list_of_blocks:
            block_lines = block['lines']
            for block_line in block_lines:
                words_inline = block_line['words']
                for word_line in words_inline:
                  n.append(float(word_line['confidence']))
        return sum(n) / len(n)




def check_argvs(argvs):
    '''
    Проверяем, входные аргументы модуля.
    :param argvs: входные аргументы модуля;
    :return:
        flags - массив флагов, ошибка есть - True, иначе - False;
        message - Формируем сообщение об ошибках
    '''
    # Проверяем, а введены ли все 6 аргументов
    len_argvs = len(argvs[1:])
    if len_argvs < 6:
        return [True], 'Ошибка! Вы пропустили {0} {1}!\n'.format(6 - len_argvs, 'аргумент' if 6 - len_argvs == 1 else 'аргумента')
    elif len_argvs > 6:
        return [True], 'Ошибка! Вы ввели {0} {1} {2}!\n'.format(('лишний' if len_argvs - 6 == 1 else 'лишние'),
                                                                len_argvs - 6, 'аргумент' if len_argvs - 6 == 1 else 'аргумента')

    token, file_name, sex, age, number, store_tag = argvs[1:]
    is_error = False
    message = ('-' * 35) + '\n| Ошибка при вводе входных данных |\n' + ('-' * 35) + '\n'

    # Проверка имени токена не пусто ли
    if not token:
        is_error = True
        message += '- Некорректно введено название файла!\n'

    # Проверка имени файла на .pdf
    if file_name[-4:] != '.pdf':
        is_error = True
        message += '- Некорректно введено название файла!\n'

    # Проверка строки - пол
    try:
        float(sex)
        is_error = True
        message += '- Некорректно введен пол! \n'
    except ValueError: pass

    # Проверка возраста на число
    try:
        float(age)
    except ValueError:
        is_error = True
        message += '- Некорректно введен возраст!\n'

    # Проверка телефона
    if number[0] not in ['+', '7', '8', '9'] and len(number) > 10:
        is_error = True
        message += '- Некорректно введен номер телефона!\n'

    # Проверка тэга магазина на число
    try:
        float(store_tag)
    except ValueError:
        is_error = True
        message += '- Некорректно введен тэг-магазина! \n'

    return is_error, message





if __name__ == '__main__':
    # argv = script_name IAMTOKEN filename sex age number store_tag

    # Проверяем верно ли введены аргументы скрипта
    err_status, err_message = check_argvs(argv)
    if err_status:
        print(err_message)
        exit()


    print('-' * 39)
    print('|', f'{argv[0]} launched', '|')    # Передаем имя скрипта
    print('-' * 39)
    print(f'Пол (gender): {argv[3:][0]}', f'Возраст (age): {argv[3:][1]}', f'Номер телефона (Tel. number): {argv[3:][2]}',
          f'Тег-магазина (Store-tag): {argv[3:][3]}', sep='\n')

    print('\nОтправляем в YandexVision...')

    # Делаем запрос в YandexVision
    text_rec = Text_Recognition(argv[1], argv[2])
    req_results = text_rec.make_req(text_rec.create_json())


    # Сохраняем координаты первого биомаркера, координаты начала поиска
    format_resp = Formate_respond(req_results.json())

    # Если точность распознавания меньше 0.8, то остановить скрипт
    req_acc = format_resp.recognition_accuracy()
    if req_acc <= 0.86:
        print('-' * 106)
        print('|', f'Ошибка! Точность распознавания = {req_acc}%. Меньше допустимого значения 0.86%, дальнейший анализ невозможен!' ,'|')
        print('-' * 106)
        exit()

    start_pos_obj = format_resp.find_position(format_resp.biomarkers)     # Ищем координаты для начала поиска
    start_y1 = int(start_pos_obj['boundingBox']['vertices'][0]['y'])    # Левая верхняя координата слова
    start_y2 = int(start_pos_obj['boundingBox']['vertices'][1]['y'])    # Правая верхняя координата слова

    result = []    # Промежуточные результаты
    last_res = []    # Записываем сюда предыдущюю строку, чтобы проверить, завершить ли цикл

    # Сбор всех строк в массив - result
    while True:
        res, y1, y2 = format_resp.gather_biomarkers(start_y1, start_y2)  # Формируем строку
        if last_res == res: break  # Останавливаем цикл если элемент повторяется
        if res:  # Если строка возвращается пустая, то мы ее не сохраняем. Если меньше 4-х предполагаем, что строка не содержит нужных значений
            result.append(res)
        last_res = res
        start_y1, start_y2 = format_resp.find_new_y1_y2(y2)

    # Форматирование данных
    result = format_resp.replace_comma_and_brackets(result)
    result = format_resp.concatenate_floats(result)
    result = format_resp.concatenate_biomarkers(result)
    result = format_resp.delete_excess_strings(result)

    # Формирование элементов массива: 1. Биомаркер, 2. Значение биомаркера, 3. нижняя граница, 4. верхняя граница
    name_biomarkers = [el[0] for el in result]  # 1) Достаем все имена биомаркеров
    biomarkers_value = format_resp.find_biomarkers_value(result)  # 2) Достаем все значения биомаркеров
    bottom_line, upper_bound = format_resp.find_bottom_and_upper_lines(result)  # 3) Нижняя граница; 4) Верхняя границы
    biomarker_units = format_resp.find_units(result)    # 5) Находим все единицы измерения

    # Собираем финальный массив
    final_array = [argv[3:]]
    for element in range(len(name_biomarkers)):
        final_array.append(
            [name_biomarkers[element], biomarkers_value[element],
             bottom_line[element], upper_bound[element], biomarker_units[element]])
    format_resp.final_array = final_array

    # Принтуем массив
    print()
    print('----------Result----------')
    print()
    for el in final_array:
        print(el)

    print()
    print(f'Точность распознавания = {round(req_acc, 4)} %')

    # Уведомление, что скрипт отработал
    print('-' * 13)
    print('|', 'Work done', '|')
    print('-' * 13)

