# VRChat Standalone Bot

A fully autonomous VRChat chatbot that can run without human intervention. This bot uses the VRChat API to interact with users and respond to commands.

## Features

- **Standalone Operation**: Runs completely autonomously without requiring human intervention
- **Rate Limiting**: Respects VRChat API limits (1 request per minute)
- **Auto-Reconnect**: Automatically reconnects if connection is lost
- **Command System**: Built-in commands for user interaction
- **Chat Responses**: Responds to greetings and farewells
- **Logging**: Comprehensive logging with colored console output
- **Configuration**: Flexible configuration via YAML and environment variables

## Requirements

- Python 3.7+
- A VRChat account (recommended to use a separate bot account)
- VRChat username and password
- 2FA code if enabled on the account

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

4. Edit `.env` with your VRChat credentials:
   ```env
   VRCHAT_USERNAME=your_bot_username
   VRCHAT_PASSWORD=your_bot_password
   VRCHAT_2FA_CODE=your_2fa_code_if_enabled
   ```

## Usage

Run the bot:
```bash
python main.py
```

The bot will:
1. Authenticate with VRChat
2. Set its status message
3. Start monitoring for friend activities
4. Respond to commands and chat messages

## Commands

The bot responds to the following commands (default prefix: `!`):

- `!help` - Show available commands
- `!info` - Show bot information
- `!status` - Show current bot status
- `!ping` - Test bot responsiveness
- `!time` - Show current time

## Configuration

### Environment Variables (.env)

- `VRCHAT_USERNAME` - Your VRChat username
- `VRCHAT_PASSWORD` - Your VRChat password
- `VRCHAT_2FA_CODE` - 2FA code if enabled
- `BOT_NAME` - Bot display name
- `BOT_PREFIX` - Command prefix (default: `!`)
- `BOT_STATUS` - Initial status message
- `MAX_REQUESTS_PER_MINUTE` - API rate limit (default: 1)
- `AUTO_RECONNECT` - Enable auto-reconnect (default: true)
- `RESPONSE_DELAY` - Delay between responses in seconds

### YAML Configuration (config.yaml)

The `config.yaml` file contains additional settings for:
- Response patterns
- Command definitions
- Logging configuration
- Feature toggles

## Important Notes

⚠️ **API Usage Guidelines**:
- This bot uses the unofficial VRChat API
- VRChat does not provide official support for API usage
- Do not make more than 1 request per minute to avoid account termination
- API endpoints may break without warning
- Use at your own risk

🔒 **Security**:
- Never commit your `.env` file to version control
- Use a separate bot account, not your main account
- Keep your credentials secure

🤖 **Bot Account**:
- It's recommended to create a separate VRChat account for the bot
- This prevents any risk to your main account
- The bot account should have appropriate permissions

## Troubleshooting

### Authentication Issues
- Verify your username and password are correct
- If 2FA is enabled, provide the correct 2FA code
- Check that your account has API access

### Rate Limiting
- The bot automatically respects rate limits
- If you get rate limited, the bot will wait automatically
- Adjust `MAX_REQUESTS_PER_MINUTE` if needed

### Connection Issues
- Enable `AUTO_RECONNECT` for automatic reconnection
- Check your internet connection
- Verify VRChat API status at https://status.vrchat.com/

## Development

To extend the bot:

1. Add new commands in the `handle_command` method
2. Modify response patterns in `config.yaml`
3. Add new features in the `monitor_friends` method
4. Update logging configuration as needed

## License

This project is provided as-is for educational purposes. Use responsibly and in accordance with VRChat's terms of service.

## Support

For issues with:
- **VRChat API**: Check VRChat's official channels
- **This bot**: Create an issue in the repository

Remember that VRChat does not officially support API usage, so support may be limited.
