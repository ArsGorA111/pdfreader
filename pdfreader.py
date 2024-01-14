#всё одним файлом
import tkinter as tk
from tkinter import filedialog
import PyPDF2
from googletrans import Translator
import requests

#APIs
url = "https://tldrthis.p.rapidapi.com/v1/model/abstractive/summarize-text/"
urlr= "https://open-ai21.p.rapidapi.com/conversationgpt35"
headers = {
	"content-type": "application/json",
	"X-RapidAPI-Key": "a47e066245msh9ef77b0ae647911p102cfcjsnb6f4e3ddf513",
	"X-RapidAPI-Host": "tldrthis.p.rapidapi.com"
}
headersr = {
	"content-type": "application/json",
	"X-RapidAPI-Key": "a47e066245msh9ef77b0ae647911p102cfcjsnb6f4e3ddf513",
	"X-RapidAPI-Host": "open-ai21.p.rapidapi.com"
}

#Открытие файла и вывод текста
def on_open():
    opened_file = filedialog.askopenfilename(initialdir="/",
                                             title="Open file")

    # вывод текста
    text_output.delete("1.0", tk.END)
    reader = PyPDF2.PdfReader(opened_file)
    for i in range(len(reader.pages)):
        current_text = reader.pages[i].extract_text()
        text_output.insert(tk.END, current_text)

#Выделенный текст
def choose():
    # захват выделенного текста
    global selected
    if text_output.selection_get():
        selected = text_output.selection_get()
        print(selected)

#Переводчик
def do_translate():
    global matches
    global selected
    global lang
    global translated_en
    global translated_ru
    translator = Translator()
    lang = translator.detect(selected)
    selectedx=selected

    #замена ентера на пробел
    enters = [i for i in range(len(selectedx)) if selectedx[i] == "\n"]
    print(enters)
    for i in range(len(enters)):
        selectedx = selectedx[:enters[i]] + selectedx[enters[i]+1:]




    #перевод
    translated_ru = translator.translate(selectedx, dest="ru")
    translated_en = translator.translate(translated_ru.text, dest="en")
    print(translated_ru.text)
    print(translated_en.text)

    #выход в окно
    translation_result_window()

#окно под перевод
def translation_result_window():
    global en
    result_window = tk.Toplevel()
    lang_list = ["en", "ru"]

    l1 = tk.Label(text="Оригинальный текст")
    l2 = tk.Label(text="Текст на английском")
    l3 = tk.Label(text="Текст на русском")

    if lang.lang not in lang_list:
        origin_text = tk.Text(result_window)
        origin_text.insert(tk.END, selected)
        l1.pack()
        origin_text.pack()

    en_text = tk.Text(result_window)
    en = translated_en.text
    en_text.insert(tk.END, en)

    ru_text = tk.Text(result_window)
    ru = translated_ru.text
    ru_text.insert(tk.END, ru)

    l2.pack()
    en_text.pack()
    l3.pack()
    ru_text.pack()

#cаммари
def do_summary():
    #перевод потому что саммари на английском
    translator = Translator()
    translated_ru = translator.translate(selected, dest="ru")
    translated_en = translator.translate(translated_ru.text, dest="en")
    en = translated_en.text


    #Запрос а API
    payload = {
        "text": en,
        "min_length": 20,
        "max_length": int(len(list(selected))/5)
    }
    response = requests.post(url, json=payload, headers=headers)
    summarized_en = response.json()['summary']
    #Обратный перевод и контрольный принт
    summarized_ru = translator.translate(summarized_en, dest="ru").text
    print(summarized_ru)

    #выход в окно
    text_window(summarized_ru)

def do_rephrase():
    translator = Translator()
    translated_ru = translator.translate(selected, dest="ru")
    translated_en = translator.translate(translated_ru.text, dest="en")
    en = translated_en.text

    # Запрос а API
    payloadr = {
        "messages": [
            {
                "role": "user",
                "content": "Rephrase the following text. Your answer should not contain anything, except paraphrased version of this text: {0}".format(en)
            }
        ],
        "web_access": False,
        "system_prompt": "",
        "temperature": 0.9,
        "top_k": 5,
        "top_p": 0.9,
        "max_tokens": 256
    }
    response = requests.post(urlr, json=payloadr, headers=headersr)
    refrased_en = response.json()['result']
    # Обратный перевод и контрольный принт
    refrased_ru = translator.translate(refrased_en, dest="ru").text


    #выход в окно
    text_window(refrased_ru)


#окошко для саммари и перефраз
def text_window(thingtowrite):
    text_window = tk.Toplevel()
    l1 = tk.Label(text_window, text="Результат")
    text = tk.Text(text_window)
    text.insert(tk.END, thingtowrite)
    l1.pack()
    text.pack()





# создание окна
x = 1000
y = 600
main_win = tk.Tk()
main_win.geometry('{0}x{1}'.format(x, y))
main_win.title("PDF Text Reader")

# полоска сверху (меню)
menu_bar = tk.Menu(main_win)

# кнопки на меню
menu_bar.add_command(label='Открыть файл', command=on_open)
menu_bar.add_command(label='Выбрать текст', command=choose)
menu_bar.add_command(label='Перевести', command=do_translate)
menu_bar.add_command(label='Саммари', command=do_summary)
menu_bar.add_command(label='Перефраз', command=do_rephrase)
# конфиг меню
main_win.config(menu=menu_bar)

# поле для текста
text_output = tk.Text(main_win, width=150, height=150)
text_output.pack()

main_win.mainloop()
