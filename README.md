# donbass_bot
## What do you need to run this
- Add donbass bot token to the <nolink>config.py</nolink> file  
`bot_token = 'YOUR TOKEN HERE'`  
- Set up a database on mongodb named 'donbass' containing these collections  
    - giveaways
    - members
    - role_expirations
    > You can get the members and role_expirations data [here](https://github.com/denborg/donbass_data)  
    
    and add mongodb url to the <nolink>config.py</nolink> file  
    `mongodb_url = 'MONGODB URL HERE'`

and then run the <nolink>main.py</nolink> file