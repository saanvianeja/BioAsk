# BioAsk: An Interactive Biology Q&A App

BioAsk is a smart, interactive study tool designed to help students master biology concepts. Powered by Large Language Models (LLMs), this app provides clear, conversational answers to biology questions, generates helpful diagrams, and suggests new topics for exploration.

## Core Features

- **Conversational Q&A:** Ask any biology question and get a clear, accurate answer.
- **Adjustable Difficulty:** Use the "Explain it Like I'm..." feature to tailor the complexity of the explanation to your level of understanding (e.g., Middle School, High School, Undergraduate).
- **Confidence Scores:** Each answer comes with a confidence score, teaching critical thinking about AI-generated content.
- **Related Topic Suggestions:** Discover new areas of study with suggestions for related topics that follow each answer.
- **Dynamic Diagram Generation:** Ask for a diagram of a biological process or structure (e.g., "draw a diagram of a neuron"), and the app will generate it on the fly.

## Technical Stack

- **Frontend:** Streamlit
- **Backend:** Python
- **LLM Integration:** Designed to work with local, open-source models via Ollama or LM Studio for cost-effective and private usage. It can also be configured to use APIs like OpenAI. 