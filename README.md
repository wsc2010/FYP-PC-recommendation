# FYP-PC-recommendation
A PC recommendation chatbot that utilizes genetic algorithm to recommend suitable PC components based on provided budget and use case

# How it works
PC hardware data and user builds is scraped from PC Part Picker. Each hardware model contains information about its rating and price.

User provides a budget and a use case, the AI then uses genetic algorithm to create multiple random builds that evolves and prioritizes maximizing based on ratings, budget and performace and how suitable it is for a given budget build based on other existing builds.



The AI is implemented as a chatbot using DialogFlow for user to interface. Core genetic algorithm code is inside algorithm folder
