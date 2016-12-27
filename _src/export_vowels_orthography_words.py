# -*- coding: utf-8 -*-

import pandas as pd
from bs4 import BeautifulSoup


df_wb = pd.read_csv('../data/coca20k_WB_speech.csv')
df_nn = df_wb[df_wb.phonetic.notnull()]
mm_columns='rank words mac_phonetic coca_speech phonetic WB_speech'.split()


def find_phonetic(data):
    bsObj = BeautifulSoup(data, "lxml")
    mylist = bsObj.find_all('font', {'color':'#21887d'})
    lst = [i.get_text() for i in mylist]
    return '\n'.join(lst)


def get_macmillan_words():
    """To get Mac Millan COCA words and Phonetic."""
    mm_html_path = "../data/DicMacmillan/coca20k_macm.html"
    mm_csv_path = "../data/DicMacmillan/coca20k_macm.csv"
    with open(mm_html_path) as file:
        data = file.read()

    df_html = pd.DataFrame({'all': data.split('\n            \n             <tr>')[1:]})
    df_csv = pd.read_csv(mm_csv_path).ix[:, 1:]
    df_csv.rename(columns={'单词': 'words', '解释': 'des',}, inplace=True)
    df_c = pd.concat([df_csv.ix[:, ['words']], df_html], axis=1 )
    df_c['mac_phonetic'] = df_c['all'].map(find_phonetic)
    df_mm = pd.merge(df_nn, df_c.ix[:, ['words', 'mac_phonetic']], on='words', how='right')
    df_mm = df_mm[df_mm['mac_phonetic'].notnull()]

    return df_mm


def export_AW(filename, num):
    """Export Macmillian words with 'ɔ' sound.

    Args:
        filename: Output filename.
        num: The highest coca number.
    """
    df_mm = get_macmillan_words()
    df_mm_num = df_mm[df_mm['rank'] <= num]
    df_mm_num_aw = df_mm_num[df_mm_num.mac_phonetic.str.contains('ɔ')]
    df_wb_ah = df_nn[df_nn.phonetic.str.contains('ɑː')]
    df_aw = pd.merge(df_mm_num_aw.ix[:, 'mac_phonetic words'.split()],
                     df_wb_ah, on='words', how='left')
    df_aw.sort_values(['rank'], inplace=True)
    df_aw.drop_duplicates('phonetic').to_excel(
        filename + '_ɔ' + '.xlsx', index=False, columns=mm_columns)


def export_other_vowel_words(filename, num):
    """Retrun a COCA words file with vowels_list."""
    vowels_list = "æ eı ɑ e ɑː oɚ ə ı eə aʊ ɛ ɚ iɚ i oʊ iːˌɑː ijoʊ ijə ju aı oı wɑ ʊ ʌ u jɚ w wı uːwə juwə eɚ ejə iˈeı iːjə owə oʊˈeı oʊˈɛ oʊˌɛ owı jə juːwə jəˈwɛ uˈI iˌI eıˈo iˈoʊ iˈæ iˈɑ iˈaʊ juː aıˈɛ iˈiː iˈe jeı wʌ əˈwɑː oʊˈɚ wajɚ oʊˈoɚ uːjə".split()
    for i in vowels_list:
        df_vowel_words = df_nn[df_nn.phonetic.str.contains(i)].ix[:num, :]
        df_vowel_words = df_vowel_words.drop_duplicates('phonetic')
        df_vowel_words.to_excel(filename + '_' + i + '.xlsx', index=False)


if __name__ == '__main__':
    export_AW('../data/COCA10kVowels/coca10k', 10000)
    export_other_vowel_words('../data/COCA10kVowels/coca10k', 10000)
