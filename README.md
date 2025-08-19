# vidtodoc - Converts videos to Word Documents

This uses OpenAI Whisper which is not sanctioned by Wex, so don't use proprietary data.  
<br/><br/>
## Prerequisites
You must install [FFmpeg](https://ffmpeg.org/download.html) to extract audio from video files.  
After downloading and extracting the file, make sure `ffmpeg\bin` folder is available in your system PATH.

If you are creating PDF files, you will need to install [Libre Office](https://www.libreoffice.org/download/download-libreoffice/), and SOffice.exe must be in your PATH.  Soffice.exe is usually found in C:\Program Files\LibreOffice\program in Windows.

You also need to install the following Python packages (make sure you're at the root of this project's folder):
```bash
pip install -r requirements.txt
```
Also, make sure you have LibreOffice installed and accessible in the system's PATH for viewing docx files.

```bash
usage: vidtodoc.py [-h] --infile INFILE --outfile OUTFILE
                   [--verbose VERBOSE]
```
