# Development Hints

This is a very AI-centric codebase. However, humans need to know things too. 

## DevContainers

DevContainers are the truth, the light, and the way. Feel free to be an animal and do it raw, but I've never tried. 

## All the AI Coding Assistants

I'm our AI lead, so I experiment a bit with coding assistants. This DevContainer has Claude, Gemini and Codex installed as defaults. First time you use one you'll need to authenticate it. Enjoy!

## Running the server

To run the server, you can use the following command:
```bash
DEBUG=true python app.py
```

This will start the server on port 8080 in debug mode which means your code changes will be reloaded automatically.


## Ngrok

I've used Ngrok https://ngrok.com/ to test things. There are other ways to do it, but I like how Ngrok allows you to replay POSTS.

First time you setup the DevContainer, you need to authenticate with Ngrok. You can do this by running the following command:
```bash
ngrok config add-authtoken <your_ngrok_authtoken>
```

You can get your authtoken from https://dashboard.ngrok.com/get-started/your-authtoken

Then, you can start Ngrok by running the following command:
```bash
ngrok http --url=example.ngrok.io 8080
```

At which point the very useful ngrok UI will also be available in your browser at something like http://127.0.0.1:4040/inspect/http

Then, you can use the URL to test the webhook. 

You'll want something like this https://<ngrok_url>/services/<something_from_config.yml>




