# imap2kafka

A small producer to send email messages from a imap account to a kafka broker.

You'll need to set up the environment variables, you can create an env.sh script like this:: 

```bash
export I2K_KAFKA_SERVERS='<broker ip>:<port>' # Comma separated list of kafka brokers
export I2K_USERNAME=alerts@example.com #imap username 
read -sp 'password' pass
export I2K_PASSWORD=$pass # imap password
export I2K_IMAP_SERVER=imap.example.com  # imap server
export I2K_FOLDER=<email_folder_to_process> # if it is not set, it will process the INBOX
export I2K_TOPIC=the_kafka_topic
```
once you have the env.sh script you can create an virtual environment and run it for the first time:

```bash 
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
source env.sh
python src/imap2kafka.py
```

### Notes:
- To work with gmail accounts you need to "enable less secure apps" in the security settings. Outlook accounts works out the box. 
- If you need to setup a kafka standalone, maybe this [gist](https://gist.github.com/cronosnull/59101eb96f71093b0c7619a66b0c4ca1) can be useful.
