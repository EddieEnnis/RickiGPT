**RickiGPT**  
**(Offline AI Assistant)**

RickiGPT is a fully offline, local AI assistant built using **Qwen2.5-7B-Instruct** running through LM Studio.  
It is designed as a real-time voice \+ text AI system with document analysis, file ingestion, and multimodal interaction—all running locally with no cloud or external API dependencies.

---

## **Key Features**

* 100% offline AI assistant (no API or internet required for inference)  
* Real-time chat interface built with Python (Tkinter UI)  
* Voice output using Edge TTS with local playback  
* PDF, DOCX, and text file ingestion for AI analysis    
* Persistent conversation memory during runtime  
* WebSocket integration for external trigger systems (VNYAN support)  
* Modular system prompt-driven architecture (“Ricki” identity system)

---

## **What RickiGPT Can Do**

* Summarize documents (PDF, DOCX, TXT)  
* Extract key insights from uploaded files  
* Answer questions based on loaded documents  
* Provide structured reasoning and analysis  
* Act as a conversational AI assistant with voice output  

---

## **System Requirements**

* Python 3.10+  
* Windows (recommended for LM Studio \+ audio stack)  
* Local model runtime via LM Studio

---

## **Model Used**

* Qwen2.5-7B-Instruct (GGUF via LM Studio)

Performance depends on local hardware (CPU/GPU/RAM).

---

## **Python Dependencies**

Install required packages:

pip install requests edge-tts pygame PyPDF2 python-docx pillow websockets

---

## **Optional Dependencies**

Used for extended features:

* `Pillow` → image handling  
* `websockets` → external trigger integration  
* `pygame` → audio playback system

---

## **File Handling Capabilities**

RickiGPT can ingest and process:

* **PDF files** → extracts full text for analysis  
* **Word documents (.docx)** → parses paragraph content  
* **Text files (.txt)** → direct reading  
* **Images (optional)** → base64 encoded for AI vision-capable models

Once uploaded, files are stored in session memory and can be referenced in conversation.

---

## **Architecture Overview**

RickiGPT operates as a **local AI orchestration system**:

1. User input (text or voice-triggered request)  
2. File ingestion (optional document upload)  
3. Prompt construction with system memory  
4. Local LLM call via LM Studio API  
5. Response generation (structured reasoning mode)  
6. Voice synthesis output (Edge TTS)  
7. Optional external triggers (VNYAN/WebSocket integration)

---

## **Privacy & Offline Design**

* Runs entirely on local machine  
* No cloud APIs required for AI inference  
* All documents remain local to the system  
* Designed for private AI workflows and research use

---

## **Notes**

* Performance varies depending on hardware and model quantization  
* Larger documents may require higher RAM systems  
* Designed as a modular AI framework, not a fixed chatbot

---

## **Project Goal**

RickiGPT demonstrates how modern LLMs can be deployed as a **fully offline, private AI assistant system** with voice interaction, document intelligence, and extensible architecture using local inference tools.

---

