# Lambda-SQL Query-Slack 

This project is an AWS Lambda Function, which has a PYODBC Lambda layer. The PYODBC layer provides a way for lambda to
interact with your AWS hosted SQL servers. The final piece of the project may still require a bit of customization is 
the slack component. You'll need to tailor the output of the message to your liking/use case. 

# Layout
```
.
├── layers                      <-- Source code for a lambda function
│   └── pyodbc                  <-- Source folder for PYODBC layer 
├── template.yaml               <-- SAM Template
├── lambda_function             <-- Resource function files
|   └── __init__.py
|   └── lambda_function.py
|   └── requirements.py
├── README.md                   <-- Instructions file
```


## Getting Started

Use the instructions below to create a local environment of a lambda function, with a PYODBC layer, which then sends 
results to a slack channel.

### Prerequisites

* [Python 3 installed](https://www.python.org/downloads/)
* [Docker installed](https://www.docker.com/community-edition)
* [AWS CLI configured](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install-mac.html)
* [PYODBC Source Files](https://github.com/aaronsr/lambda-pyodbc-layer)


### Pycharm customization

1. Start off by installing Pycharm. I used the Community Edition, and this project was built using 2019.2.5.
2. Install the AWS-Tools add-on for Pycharm.
3. Make sure you have your AWS credential setup. Please see the Pycharm website for more information on this. 
4. As you can see above, in the layout section, you need to ensure the PYODBC layer is setup correctly. Unzip the
contents of the PYODBC Source Files into this pyodbc layer folder. 
5. Environment variables you need to either add within the code or within the Pycharm environments section. 
    ```
    slack_webhook_url = 'The URL of your slack webhook'
    slack_channel = '#SLACK CHANNEL'
    slack_user_name = 'Slack webhook username'
    ```
6. Basic text for the event template (Pycharm) & event.json
    ```
    {
        "server": "IP or DNS name of the server you query",
        "database": "name of the database",
        "username": "Username with confirmed perms to your DB",
        "password": "PWD",
        "type": "message",
        "user": "Slack User ID"
    }
    ```


### Local development
**Invoke function locally, with pycharm**
```
In Pycharm, click Run -> Run'[Local] lambda_function.lambda_handler**
```
## Authors

* **Aaron LeMoine**

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
