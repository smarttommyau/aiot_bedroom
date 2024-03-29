# aiot_bedroom
Project that aims to provide the best bedroom environment with AI and IoT
> Image from V1
<p float="left" align="middle">
<img width="32%" src="img/not_moving.png"/>
<img width="32%" src="img/not_moving_end.png"/>
<img width="32%" src="img/sleeping_and_lyingbed_end.png"/>
</p>

> Image from V2
<img src="https://github.com/smarttommyau/aiot_bedroom/assets/75346987/248e7118-f15e-4265-b0e2-5e18948149e4"/>
<img src="https://github.com/smarttommyau/aiot_bedroom/assets/75346987/98e1614c-e6c9-4acd-ac10-ca90d5e3f3bc"/>
<img src="https://github.com/smarttommyau/aiot_bedroom/assets/75346987/63dfb274-fd5f-46d7-b135-64768435950b"/>

# Some Details
**!!!** Please look at the **[project documents](./project_documents)**
- [Poster](./project_documents/P21_Poster.pdf)
    - [Demo Video(Long)](https://youtu.be/l8e21IzSXhs)
    - [Product Video(Short)](https://youtu.be/VZf5DOBUzaY)
- [Poster(For Elderly Update)(More specific feature about elderly based)](./project_documents/Elderly_Poster.pdf)
- [Pitch deck](./project_documents/P21_pitching_deck_AIoT%20Bedroom.pptx)
- [Learning Summary](./project_documents/P21_Learning_Summary.docx)

# Code
## 2 part 
- [AI analysis](./ai_analysis)
- [Camera Connector](./flir-cam-connect/FLIROneSDKBundle)
## AI analysis V1
- use the [**live_analysis.ipynb**](./ai_analysis/live_analysis.ipynb) as the main program(For pc)
## AI analysis V2
- use the [**live_analysis.py**](./ai_analysis/live_analysis.py) as the main program(For pc)
> Huge performance increase and huge improve in stability. Also, a better UI. 
### IoT
> [**IoT Main Page**](./ai_analysis/IoT)
Adurino project devices(ESP8266)
- [**IoT/esp8826**](./ai_analysis/IoT/esp8826/esp8826.ino) is the code for the board
## Camera Connector
- [**live_connection.py**](./ai_analysis/live_connection.py) as the server(For pc)
- [**flir-cam-connect**](./flir-cam-connect/FLIROneSDKBundle) as the client source code(For Cat S60)

## Hardware
Current using **Cat S60**(built-in flir camera), can accept more hardware in the future\
**ESP8826** as the IoT chipset to control some small IoT devices(lights, fans, buzzer)

# Awards
<p float="left" align="middle">
<img width="100%" src="https://user-images.githubusercontent.com/75346987/224349819-0299458f-4f7e-4143-8ce3-11d59ca62608.jpg"/>
<img width="100%" src="https://user-images.githubusercontent.com/75346987/224350779-c88bb661-896e-452f-ae3e-d69c218e267a.jpg"/>

</p>

- **Champion** of GEF AIoT coding, Engineering, Entrepreneurial skills
- **First in vote** of GEF AIoT coding, Engineering, Entrepreneurial skills
# License
We offer 2 LICENSES:
- GPL-3.0 License: See [LICENSE](./LICENSE) file for details.
- Enterprise License: You can get more freedom for commercial development, you may contact me to negotiate for the License.

# TODO
- [x] Optimize performance
    - [x] FPS improvement
    - [x] analysis efficiency
    - [x] Ping improvement(Not dropping extra frames)(5000ms)
    - [x] stability on pc
    - [x] stability on camera side(OOM problems)(auto drop extra frames)
- [x] Update for Elderly edition
    - [x] Not sleeping well
    - [x] Care service
    - [ ] ...
