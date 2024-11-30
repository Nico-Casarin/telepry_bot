# TelePry Bot 🤖

TelePry Bot is a Telegram bot designed for regulated press releases and regulated documents for an italian company.

## Features 🌟

- **Scheduled Job**: each 30 minutes the bot will collect new data and push to a Telegram group 
- **User-Friendly**: Lightweight, intuitive, and efficient.
- **Extensible**: Easy to customize and add new features leveraging telegram APIs.

## Installation 🔧

Follow these steps to set up the bot:

1. **Clone the Repository**  
   Clone the repository to your local machine:
   ```bash
   git clone https://github.com/Nico-Casarin/telepry_bot.git
   cd telepry_bot
   ```

2. **Set Up Dependencies**  
   Install the required Python packages using `pip`:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Your Bot**  
   - Obtain a Telegram bot token from [BotFather](https://core.telegram.org/bots#botfather).

4. **Run the Bot**  
   Start the bot with the following command:
   ```bash
   python bot.py -t API_TOKEN -g GROUP_ID -a ALLOWED_USER
   ```

## Usage 🚀

- **Interact with the Bot**:  
  Add the Bot to the choosen group and /star it. If you passed allowed users ids, the bot will interact only with those users.

## License 📜

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

## Disclaimer ⚠️

I do not own any of the registered names or trademarks mentioned in this repository. Any scraping must be performed politely and in compliance with the website owner’s terms, conditions, and requests. Additionally, no material accessed or consulted from the Teleborsa website may be shared or used for commercial purposes.


---

Enjoy using **TelePry Bot** and feel free to contribute to its development! 🚀
