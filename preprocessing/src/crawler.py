import requests
import urllib.parse
import xml.etree.ElementTree as ET
import datetime
import os


"""
参考リンク
https://qiita.com/kenta1984/items/1acfddb3d920a11e6c8b


国会議事録APIを用いて全議会録をクローリングする

2023/4/1時点で使う必要はないはず
6/15に2023年のものをクローリング。
"""

def main(year:int) -> None:
    # １月、２月、３月、…と月毎に収集
    for month in range(1, 13):
        # クエリパラメータの設定
        q_maximumRecords = 100
        q_from = str(datetime.date(year, month, 1))
        if month != 12:
            q_until = str(datetime.date(year, month+1, 1) - datetime.timedelta(days=1))
        else:
            q_until = str(datetime.date(year+1, 1, 1) - datetime.timedelta(days=1))

        # 一回当たりの抽出件数が最大100件のため、全体のレコード数から必要なループ回数を決定
        payload = 'from=' + q_from + '&until=' + q_until + '&maximumRecords=' + str(q_maximumRecords) + '&startRecord=1'
        payload_encoded = urllib.parse.quote(payload)
        r = requests.get(base_url + payload_encoded)
        root = ET.fromstring(r.text)
        loop_num = int(root[0].text) // q_maximumRecords + 1

        try:
            make_dir = './xml_data/' + str(year) + '_data'
            if not os.path.exists(make_dir):
                os.makedirs(make_dir)
        except Exception as e:
            print(e)
            return 

        # ループを回し、APIでデータ収集
        i = 0
        while i < loop_num:
            q_startRecord = 1 + i * q_maximumRecords
            payload = 'from=' + q_from + '&until=' + q_until + '&maximumRecords=' + str(q_maximumRecords) + '&startRecord=' + str(q_startRecord)
            payload_encoded = urllib.parse.quote(payload)
            r = requests.get(base_url + payload_encoded)

            with open('./xml_data/' + str(year) + '_data/' + str(year) + '_' + str(month) + '_' + str(i) + '.xml', mode='w') as f:
                f.write(r.text)

            i += 1


if __name__ == "__main__":
    base_url = 'http://kokkai.ndl.go.jp/api/1.0/speech?'
    # 1947-2022年まで拾える
    #main(year)でひろう
    for year in range(2022, 2023):
        main(year)   