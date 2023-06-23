import xml.etree.ElementTree as ET
import glob
import csv
import os
import re
import spacy
import numpy as np

"""
xml -> csv

参考リンク
https://qiita.com/Robot-Inventor/items/2264590f392a1a9e8831
"""


def pattern_match(text):
    regex = r"((〇|一|二|三|四|五|六|七|八|九)*(・)*(〇|一|二|三|四|五|六|七|八|九|十|千|百|万)+(円|枚|人|名|件|団体|代|店舗|週間|年間|日間|回|波|か月|年度|％|倍|兆|億|月|日|歳|年|時|分|秒|つ|割|社|問|棟))"
    matches = re.finditer(regex, text, re.MULTILINE)
    for match in matches:
        text = text.replace(match.group(), converter(match.group()))
    text = text.replace('・', '.')
    return text

def split_sentences(text):
    sentences = text.split('。')
    sentences = [s.strip() + '。' for s in sentences if s.strip()] 
    return sentences
    


def converter(string):
    """
    change kansuji to arabic letters
    """

    result = string.translate(str.maketrans("〇一二三四五六七八九", "0123456789", ""))
    convert_table = {"十": "0", "百": "00", "千": "000"}

    for unit in convert_table.keys():
        zeros = convert_table[unit]
        for numbers in re.findall(f"(\d+){unit}(\d+)", result):
            result = result.replace(
                numbers[0] + unit + numbers[1], numbers[0] + zeros[len(numbers[1]):len(zeros)] + numbers[1])
        for number in re.findall(f"(\d+){unit}", result):
            result = result.replace(number + unit, number + zeros)
        for number in re.findall(f"{unit}(\d+)", result):
            result = result.replace(
                unit + number, "1" + zeros[len(number):len(zeros)] + number)
        result = result.replace(unit, "1" + zeros)
    return result

def main():
    """
    rangeの日付は適宜変更
    6-15: 2023年版をやってみた
    """
    for i in range(2022, 2023):
        file_paths: list = glob.glob('./xml_data/' + str(i) + '_data/' + str(i) + '_*.xml', recursive=True)
        #sort a pile of files
        sorted_files = sorted(file_paths, key=lambda x: tuple(map(int, re.findall(r'\d+', x))))

        for file in sorted_files:
            tree = ET.parse(file)
            root = tree.getroot()

            try:
                make_dir = './csv_data/' + str(i) + '_data'
                if not os.path.exists(make_dir):
                    os.makedirs(make_dir)
            except Exception as e:
                continue

            try:
                make_dir = './title_data/' + str(i) + '_data'
                if not os.path.exists(make_dir):
                    os.makedirs(make_dir)
            except Exception as e:
                continue            

            for record in root.iter(tag='speechRecord'):
                speech_list = []
                title_list = []
                speaker = record.find('speaker').text
                speaker_yomi = record.find('speakerYomi').text
                speech = record.find('speech').text   
                speech = re.sub(r"○(.*)　|(〔.*〕)|（.*）|(─+)|(―+)|◇", "", speech).replace('　', '')
                speech = pattern_match(speech)
                date = record.find('date').text
                speaker_group = record.find('speakerGroup').text
                name_of_house = record.find('nameOfHouse').text
                name_of_meeting = record.find('nameOfMeeting').text
                
                # if sentences is matched, they are removed.
                if re.search(r'((―+)\◇(―+))|(―+)|((午前|午後)(\d*|零)(時)(\d*|零)(分)*(開会|休憩|閉会|散会|開議))', speech):
                    pattern = r'(○)*本日の会議に付した案件\n([\s\S]*)'
                    match = re.search(pattern, speech)

                    # get the title
                    if match:
                        result = match.group()
                        result = re.sub('○|本日の会議に付した案件\n', '', result).replace(r'((午前|午後)(\d*|零)(時)(\d*|零)(分)*(開会|休憩|閉会|散会|開議))', '')

                        title_list.append([
                            date,
                            name_of_house,
                            name_of_meeting,
                            speaker,
                            speaker_yomi,
                            speaker_group,
                            '',
                            '',
                            result
                        ])
                        with open('./title_data/' + str(i) + '_data/' + str(date) + '.csv', mode='a') as f:
                            writer = csv.writer(f)
                            for title in title_list:
                                writer.writerow(title)
                            
                    continue

                speech_list.append([
                    date,
                    name_of_house,
                    name_of_meeting,
                    speaker,
                    speaker_yomi,
                    speaker_group,
                    '',     # title
                    '',     # label about pro, on or others
                    speech
                ])
                with open('./csv_data/' + str(i) + '_data/' + str(date) + '.csv', mode='a') as f:
                    writer = csv.writer(f)
                    for speech in speech_list:
                        writer.writerow(speech)


if __name__ == "__main__":
    main()