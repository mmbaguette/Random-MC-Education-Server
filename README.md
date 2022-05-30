# Random Minecraft Education Servers

**Disclaimer:** This project was not made to harm Mojang, Minecraft Education Edition or any of its users. 
Rather, I made this for something I can code on my own time.

## Introduction

Join random Minecraft Education Servers in your school board, by brute-forcing every possible combination of server codes!

Using as many threads as possible, this program will go through 73440 different combinations of server codes, finds which codes exist, and returns the IP address and code for that server, along with its description and server owner stored in a `codes.json` file.

Fastest time on my gaming PC: **21 minutes** (all code combinations!)

![Choosing codes](https://i.stack.imgur.com/vMz19.png)

## How to use
 - Use [mitmproxy](https://mitmproxy.org/) to intercept your access token, and paste it alone in a file called `mc token.txt` in your current working directory (the folder or file path where you run the script). 
 - Intercept the access token using mitmweb, using a search filter with `~u https://discovery.minecrafteduservices.com/joininfo`.
 - After signing in to MC Education Edition, click on Join World, enter a random code, and wait for mitmproxy to intercept the search request to this URL. 
 - Click on the request, and inside the request payload, look for the `accessToken` value. Copy everything without the quotes (`"`).

**Note: You'll only find codes that you can join from your organization/school board.**
