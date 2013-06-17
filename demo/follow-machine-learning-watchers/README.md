# Follow Machine Learning Watchers on coursegraph

<http://coursegraph.com/machine-learning-coursera-ml-stanford-university>

## DO It!

```
$wget http://coursegraph.com/machine-learning-coursera-ml-stanford-university
...
$less machine-learning-coursera-ml-stanford-university
```

Find this piece:

```
...
<a href="/user/11829662477"><img src=http://tp2.sinaimg.cn/1829662477/50/5660218407/1></a>
<a href="/user/12104931705"><img src=http://tp2.sinaimg.cn/2104931705/50/5599477433/1></a>
<a href="/user/11655038093"><img src=http://tp2.sinaimg.cn/1655038093/50/5644837216/1></a>
<a href="/user/11661196902"><img src=http://tp3.sinaimg.cn/1661196902/50/5637286119/1></a>
...
```

Good, it is referring to `sinaimg.cn`.
The first section in the path of `sinaimg` should be the UID. Check

   * <http://weibo.com/u/2104931705>
   * <http://coursegraph.com/user/12104931705>

Yes, they are the same.
Get the IDs from the image link:

```
$grep -oP '(?<=http://...\.sinaimg.cn/)\d*(?=/)' machine-learning-coursera-ml-stanford-university > id.list
$head -n3 id.list 
1829662477
2104931705
1655038093
```

Last, let's follow those users. 
Copy `follow.py` to the ROOT of `sina-automator`
(same level as `wauto.py`)
and execute it with 

```
python follow.py demo/follow-machine-learning-watchers/id.list
``` 

This script is short and is explained in comments.
The first CLI argument is the `id.list` we obtained from coursegraph.
Change the name accordingly.

## Example channel.json

Before you run the `follow.py` script, you should configure a SinaWeibo channel first. 
The following is a template. 
Save it as `conf/channel.json` (from the ROOT) 
and modify those `<XXX>` fields using your own data.
You may want to 
[apply app key](https://github.com/hupili/snsapi/wiki/Apply-for-app-key)
on SinaWeibo. 

```
[
  {
    "platform": "SinaWeiboStatus",
    "channel_name": "automator",
    "auth_info": {
      "save_token_file": "(default)",
      "callback_url": "https://api.weibo.com/oauth2/default.html",
      "cmd_fetch_code": "(local_username_password)",
      "cmd_request_url": "(dummy)",
      "login_username": "<YOUR USER NAME>",
      "login_password": "<YOUR PASSWORD>"
    },
    "app_secret": "<YOUR APP SECRET>",
    "open": "yes",
    "app_key": "<YOUR APP KEY>"
  }
]
```
