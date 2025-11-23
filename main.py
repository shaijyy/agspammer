import FreeSimpleGUI as sg
import requests
import time
import threading
from datetime import datetime

class PostRequesterApp:
    def __init__(self):
        self.is_running = False
        self.sent_requests = 0

        layout = [
            [sg.Text("AnswerGarden Spammer",
                     font=("Helvetica", 16),
                     justification='center',
                     text_color='black',
                     background_color='white')],
            [sg.Text("This software may violate AnswerGarden's ToS, and may lead to temporary IP Blockage",
                     font=("Helvetica", 12),
                     justification='center',
                     text_color='black',
                     background_color='white')],
            [sg.Text("BUT WHO CARES!!!!!!",
                     font=("Helvetica", 12),
                     justification='center',
                     text_color='black',
                     background_color='white')],
            [
                sg.Multiline(size=(50, 20),
                             key='response_log',
                             disabled=True,  
                             autoscroll=True,   
                             text_color='green',
                             background_color='white'),
                sg.VSeparator(),
                sg.Column([
                    [sg.Text("Enter ID:", background_color='white', text_color='black'),
                     sg.InputText(key='id_input', background_color='white', text_color='black')],
                    [sg.Text("Frequency (seconds, 2 is recommended):", background_color='white', text_color='black'),
                     sg.InputText("2", key='frequency_input', background_color='white', text_color='black')],
                    [sg.Text("Answer 1:", background_color='white', text_color='black'),
                     sg.InputText(key='answer_1', background_color='white', text_color='black')],
                    [sg.Text("Answer 2 (optional):", background_color='white', text_color='black'),
                     sg.InputText(key='answer_2', background_color='white', text_color='black')],
                    [sg.Text("Answer 3 (optional):", background_color='white', text_color='black'),
                     sg.InputText(key='answer_3', background_color='white', text_color='black')],
                    [sg.Checkbox("Verify SSL", default=True, key='verify_ssl',
                                 background_color='white', text_color='black')],
                    [sg.Text("Max Requests (0 = unlimited):",
                             background_color='white',
                             text_color='black'),
                     sg.InputText("0", key='max_requests', size=(6, 1),
                                  background_color='white', text_color='black'),
                     sg.Button("Start"),
                     sg.Button("Stop")]
                ], background_color='white')
            ]
        ]

        self.window = sg.Window("AnswerGarden Spammer",
                                layout,
                                background_color='white',
                                titlebar_background_color='white')

    def run(self):
        while True:
            event, values = self.window.read()
            if event == sg.WINDOW_CLOSED:
                break
            elif event == "Start":
                if not self.is_running:
                    self.is_running = True
                    self.sent_requests = 0
                    self.log("Starting requests...")
                    threading.Thread(target=self.send_post_requests,
                                     args=(values,),
                                     daemon=True).start()
            elif event == "Stop":
                self.is_running = False
                self.log("Stopping requests...")

        self.window.close()

    def send_post_requests(self, values):
        url_template = "https://answergarden.ch/{}"
        id_value = values['id_input']
        verify_ssl = values['verify_ssl']

        answers = [values['answer_1'], values['answer_2'], values['answer_3']]
        answers = [a for a in answers if a]

        try:
            frequency = int(values['frequency_input'])
        except ValueError:
            frequency = 4

        try:
            max_requests = int(values['max_requests'])
        except ValueError:
            max_requests = 0

        while self.is_running:
            for answer in answers:
                if not self.is_running:
                    break
                if max_requests and self.sent_requests >= max_requests:
                    self.log("Reached max request limit; stopping.")
                    self.is_running = False
                    break

                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                                  "Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
                              "image/avif,image/webp,image/apng,*/*;q=0.8,"
                              "application/signed-exchange;v=b3;q=0.7",
                    "Accept-Encoding": "gzip, deflate, br, zstd",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Cache-Control": "max-age=0",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Origin": "https://answergarden.ch",
                    "Referer": f"https://answergarden.ch/{id_value}",
                }

                form_data = {
                    "answer": answer,
                    "action": "websubmit",
                    "id": id_value,
                    "output": "html",
                    "submit.x": "1063",
                    "submit.y": "135"
                }

                try:
                    response = requests.post(
                        url_template.format(id_value),
                        headers=headers,
                        data=form_data,
                        verify=verify_ssl,
                        timeout=10
                    )
                    self.log(f"Answer: {answer} | Response: {response.status_code}")
                except Exception as e:
                    self.log(f"Error: {e}")

                self.sent_requests += 1
                time.sleep(frequency)

    def log(self, message):
        timestamped = f"[{self.timestamp()}] {message}\n"
        self.window['response_log'].update(timestamped, append=True)

    def timestamp(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    app = PostRequesterApp()
    app.run()
