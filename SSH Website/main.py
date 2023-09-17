from flask import Flask, render_template, request
from data_preprocessing import preprocess_text, predict_cluster
from bs4 import BeautifulSoup
import requests
import re
from urllib.parse import urljoin

def scrape_mitre_attack(technique_id):
    technique_name = []
    technique_description = []
    tactic_name = []
    tactic_description = []
    tactic_url = []
    tech_url = []
    
    for index in technique_id:
        Subtechnique = index.split('.')[0]
        print(Subtechnique)
        url = f'https://attack.mitre.org/techniques/{Subtechnique}/'
        response = requests.get(url)
        tech_url.append(url)
        print("urllllllllllllllllllllllllllllllllllllllllllllllllllllll",url)
        if response.status_code == 200:
            print(response.status_code)
            soup = BeautifulSoup(response.text, 'html.parser')

            #technique & description
            name = soup.find('title').text
            technique_name.append(name)

            description = soup.find('div', class_='description-body').text
            technique_description.append(description)

            tab_content_div = soup.find('div', id='v-tabContent')  # 找到具有指定 id 的 div 元素
            if tab_content_div:
                tactics_link = tab_content_div.find('a', href=re.compile(r'/tactics/'))  # 在这个 div 元素中找到 Tactics 链接
                if tactics_link:
                    tactics_url = tactics_link['href']  # 获取 Tactics 链接的相对 URL
                    
                    if tactics_url.startswith('https://attack.mitre.org/'):
                        full_url = tactics_url  # 已经是完整 URL，不需要添加前缀

                    else:
                        full_url = f'https://attack.mitre.org/{tactics_url}/'
                    tactic_url.append(full_url)
                    print(full_url)
                    tactics_response = requests.get(full_url)
                    if tactics_response.status_code == 200:
                        tactics_soup = BeautifulSoup(tactics_response.text, 'html.parser')
                        
                        # tactics
                        name = tactics_soup.find('title').text
                        tactic_name.append(name)
                        description = tactics_soup.find('div', class_='description-body').text if tactics_soup.find('div', class_='description-body') else "N/A"
                        tactic_description.append(description)
                        # 返回提取的信息
                        
        else:
            return None, None, None, None
        
        num_list = list(range(len(technique_name))) 
        
        
    return technique_name, technique_description, tactic_name, tactic_description,tech_url,tactic_url,num_list
num_mapping = {
    1: ['T1120.000'],
    2: ['T1087.001', 'T1059.004', 'T1485.000', 'T1190.000'],
    3: ['T1059.004'],
    4: ['T1087.001'],
    5: ['T1059.004'],
    6: ['T1087.001', 'T1059.004', 'T1485.000', 'T1190.000'],
    7: ['T1087.001'],
    8: ['T1059.004','T1485.000','T1190.000'],
    9: ['T1059.004'],
    10: ['T1120.000'],
    11: ['T1059.004'],
    12: ['T1087.001'],
    13: ['T1059.004', 'T1485.000', 'T1190.000'],
    14: ['T1059.004', 'T1485.000', 'T1190.000'],
    15: ['T1059.004'],
    16: ['T1059.004'],
    17: ['T1059.004'],
    18: ['T1059.004'],
    19: ['T1059.004'],
    20: ['T1059.004'],
    21: ['T1087.001', 'T1059.004', 'T1485.000', 'T1190.000'],
    22: ['T1190.000','T1059.004'],
    23: ['T1059.004'],
    24: ['T1059.004'],
    25: ['T1190.000'],
    26: ['T1087.001', 'T1059.004', 'T1485.000', 'T1190.000']
}


app = Flask(__name__, static_url_path='/static')

@app.route('/')
def home():
    return render_template('index.html', result=None)
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/tools')
def tools():
    return render_template('tools.html')

@app.route('/process_text', methods=['POST'])
def process_text():

    input_text = request.form['input-text']
    predicted_label = predict_cluster(input_text)
    group_name = num_mapping.get(predicted_label+1, "['T1110.000']")
    # 获取技术或子技术的信息
    print(predicted_label+1)
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> group name:",group_name)
    print(type(group_name))
    technique_name, technique_description, tactic_name,tactic_description,tech_url,tactic_url,num_list = scrape_mitre_attack(group_name)
    print(technique_name)
    print(technique_description)
    print(tactic_name)
    print(tactic_description)
    print(tech_url,tactic_url)
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~:",num_list)
    return render_template('index.html',
                            result=group_name,
                            clusters=predicted_label + 1,
                            input_text=input_text,
                            technique_name=technique_name,
                            technique_description=technique_description,
                            tactic_name = tactic_name,
                            tactic_description= tactic_description,
                            tech_url = tech_url,
                            tactic_url = tactic_url,
                            num_list = num_list)

if __name__ == '__main__':
    app.run(debug=True)

