


# Run
To run the program once installed 
>> python BitLit_decoder.py HiBitLit.pmdl

This will start snowboy listening for the phrase "Hi BitLit". Then it will ask for seed phrases for a poem.

# Setup

- clone the repositry

Requirements:
-	Python2, pip
- for mac
  - Brew (mac: sudo apt-get install linuxbrew-wrapper)
  - PIP (sudo apt-get install python-pip)
  - PortAudio (mac: brew install portaudio)
- for ubuntu:
  - PortAudio (sudo apt install portaudio19-dev)
- python package `pip install -r requirements.txt`
- snowboy v1.1.1 
  - either get
    - a precompiled version for you platform and python version here (http://docs.kitt.ai/snowboy/#downloads) 
    - or compile it yourself by cloning the repo, then going into swig/python and running make
  - Copy the resources folder and the compiled files into the snowboy subdirectory.


API Keys:
- `cp secrets.template.json to secrets.json`
- get an API key for google cloud
  - make a project or use an existing project
  - download a credentials json for that project (using edit, create key) https://console.cloud.google.com/apis/api/speech.googleapis.com/credentials
  - enable the speech recognition api for that project (make sure you've selected your project) https://console.cloud.google.com/apis/api/speech.googleapis.com/overview
  - place the credientials json at this path `./secrets/google_cloud_credintials.json`
  - never commit this file!
