# aws-rss-discord-bot
A serverless discord bot implemented using AWS API Gateway HTTP REST API endpoints integrated with AWS Lambda Function for verifying the request and running the slash commands submitted from the discord bot.
This bot fetches all the recently posted AWS blogs (Big Data, Compute, Developer, etc. this can be expanded via SAM Template) and posts them into Discord as an embed.

## How to get started ?
### Registering Commands 
- To start deploying with the bot, you need to have a bot application created in the discord. If you are new to this, how to create a bot application in discord can be reffered from [here](https://discord.com/developers/applications).
- Upon creation of bot on discord developer portal, you will be able to see the details like `APPLICATION_ID` and `PUBLIC_KEY` (also known as `CLIENT_KEY`) from within `General Information` tab and `TOKEN` from `Bot` tab.
- Invite the bot to your discord server. Invitation URL can be created from `Oauth2 > URL Generator` tab. By selecting scope `bot` and `applications.commands` and permissions as `administrator` (if you are testing it out) otherwise only `Send Messages` and `Manage Messages permissions` are required for bot.
- Once you have these details handy with, put these information in `manage_commands/register.py`
- Install dependencies to run this.
    > pip3 install requirements.txt
- Run `manage_commands/register.py`
    > python3 manage_commands/register.py
- On successful run of python script, you will be able to see the 2 slash commands create in discord i.e. `/hello` and `/fetch`

### Deploying API Gateway and Lambda Functions to verify and execute commands
- Before start with the deployment in AWS using `sam-cli`. There are a few things that need to be updated in SAM Template `src/template.yaml`.
    ```yaml
        BOT_TOKEN: TOKEN
        DISCORD_CLIENT_KEY: BOT_PUBLIC_KEY
        LAST_UPDATED_S3_BUCKET: BUCKET_NAME # An existing S3 Bucket where Lambda will read/write into.
        Resource: arn:aws:s3:::BUCKET_NAME/* 
    ```
    **Note**: **It's HIGHLY RECOMMENDED to store and read `BOT_TOKEN` and `DISCORD_CLIENT_KEY` from AWS Secrets Manager if you are planning to use this bot for Production use or Public use. As both of these are secrets for bit and if anyone get their hands on these, you bot can be spammed with malicious things which we don't expect or want.** 
    - I have kept it in template here as I am just using this for my very personal and testing purposes.  
- Once template.yaml is updated, use `sam-cli` to run:
    > sam build -t src/template.yaml

    > sam validate
- Once validation shows everything is good to go. We can run `sam deploy` to deploy everything in AWS.
- Sam deploy on completion will give output like:
```bash
CloudFormation outputs from deployed stack
------------------------------------------------------------------------------------------------------------------------
Outputs                                                                                                                
------------------------------------------------------------------------------------------------------------------------
Key                 ExecuteCommandFunction                                                                             
Description         Execute Command Lambda Function ARN                                                                
Value               arn:aws:lambda:region:xxxxxx:function:aws-rss-discord-bot-                               
ExecuteCommandFunction-xxxxxx                                                                                    

Key                 VerifyRequestIamRole                                                                               
Description         Implicit IAM Role created for Verify Request function                                                 
Value               arn:aws:iam::xxxxxxx:role/aws-rss-discord-bot-VerifyRequestFunctionRole-xxxxxx          

Key                 VerifyRequestFunction                                                                              
Description         Verify Request Lambda Function ARN                                                                 
Value               arn:aws:lambda:region:xxxxxx:function:aws-rss-discord-bot-VerifyRequestFunction-         
xxxxxx                                                                                                           

Key                 ExecuteCommandFunctionIamRole                                                                      
Description         Implicit IAM Role created for Execute Command Lambda function                                      
Value               arn:aws:iam::xxxxx:role/aws-rss-discord-bot-ExecuteCommandFunctionRole-xxxxx        

Key                 VerifyRequestApi                                                                                   
Description         API Gateway endpoint URL for Prod stage for Verify Request function                                
Value               https://xxxxx.execute-api.xxxxx.amazonaws.com/Prod/                                      
------------------------------------------------------------------------------------------------------------------------
```

### Integrating AWS API Gateway endpoint url with Discord bot.
- To integrate the AWS API Gateway with Discord bot. Go to discord bot developer portal where the bot was created. Select the application that you have created initially.
- Take the API Gateway endpoint URL mentioned from SAM Deploy output `https://xxxxx.execute-api.xxxxx.amazonaws.com/Prod/`
- Put this URL in the `INTERACTIONS ENDPOINT URL` in discord bot General Information Page.
- Click Save. Discord will send a sample request and if that is verified it will save the interaction end point.
- BOOM..!! your discord bot is ready to use..!!!!

### Executing command on discord
- To test it out if your bot is functioning. Run `/hello` on discord and output returned will be `Hello World`
- To fetch AWS blogs into your discord channel. Run `/fetch BLOG_NAME`
    - `BLOG_NAME` will be the name that we have mentioned in the `src/template.yaml` without `_URL` i.e. `BLOG_NAME` can be either one of these `big_data, developer, architecture, compute, news, train_cert, startup`
    - This blog fetching list can be expanded or reduced by adding or removing more URLs in the SAM Template.
