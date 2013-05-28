# sina-automator

Tool Chain for Making SinaWeibo Bot

## Motivation

Two major problems addressed in this project:

   * There are many synchronous API wrapper for SinaWeibo. 
   One difficulty that many people encounter is the rate limit.
   * Bot develop and deploy are usually isolated. 
   There is no convenient interactive mining environment. 

The rate limiting queue is also a prototype of 
[Asynchronous Message Queue](https://github.com/hupili/snsapi/issues/25)
mentioned several times in 
[SNSApi](https://github.com/hupili/snsapi).
We will merge into SNSAPI when it is mature enough. 

## Contents

A brief view of the contents.

   * `snsapi` -- Submodule snsapi, to gain basic asscess to SinaWeibo. 
   * `wauto.py` -- Extend SinaWeibo platform of snsapi:
   get information, follower, followee list; follow action; etc. 
   * `lbucket.py` -- LeakyBucket implementation with multiple resources;
   A rate limiting queue to manage tasks;
   A rate limiting decorator to transform any 
   synchronous Weibo operation into asynchronous rate limited operation. 
   * `bot.py` -- Interactive mining environment. 

## Usage

   * Clone this repo. 
   * Install dependencies: 
   e.g. `pip install --user -r requirements.txt`
   * Fetch submodules (SNSAPI): 
   `git submodule init` and `git submodule update`
   * Get some basic knowledge of [SNSApi](https://github.com/hupili/snsapi).
   You only need to get a flavour of how to use it.
   * Configure your SinaWeibo channel.
   A most minimal sample is as follows
   (save to `./conf/` and modify `>>XXX` fields accordingly;
   Remember to make the `callback_url` same on Sina dev platform and in SNSAPI conf). 
   Please see SNSAPI materials if you want to further learn the config entries. 

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
      "login_username": ">>YOUR_LOGIN_USERNAME",
      "login_password": ">>YOUR_LOGIN_PASSWORD"
    },  
    "app_secret": ">>YOUR_APP_SECRET",
    "open": "yes",
    "app_key": ">>YOUR_APP_KEY"
  }
]
```

   * Run `python snsapi/snscli.py` and SNSAPI will automatically authorize SinaWeibo for you. 
   If you stick to the above config file and the credentials are correctly filled in, 
   you don't have to do anything. 

Check if a `automator.token.save` is created in your current dir. 
If yes, you can now use other tools in this repo. 
See use cases below for some demos. 

## Case 1 -- Synchronous Calls with Extended Functions

If you enter Python interactive shell from `wauto.py`,
all calls will be **synchronous** and **without rate limit**.
This environment is good for those experiments that you want immediate result.

See the following console interaction for some examples. 

```
$python -i wauto.py
... (some logs) ...
>>> wa.uid
3255069542
>>> wa.follow(2862649054)
{'status': {'reposts_count': 0, 'favorited': False, 'attitudes_count': 0, 'truncated': False, 'text': u'\u88ab\u6076\u5fc3\u5230\u4e86\u3002\u4e92\u8054\u7f51\u5e26\u6765\u7684\u6548\u7387\u90fd\u88ab\u7248\u6743\u5403\u56de\u53bb\u4e86\u3002\u516c\u5e73\u4f7f\u7528\u539f\u5219\u5728\u5927\u90e8\u5206\u5730\u533a\u7684\u5927\u90e8\u5206\u5b66\u672f\u6d3b\u52a8\u6709\u6548\uff0c\u6361\u56de\u4e86\u70b9\u6548\u7387\u3002\u4e0d\u8fc7\u53d1\u8868\u8fd9\u4e00\u52a8\u4f5c\u662f\u88ab\u5f53\u6210\u5546\u4e1a\u884c\u4e3a\u7684\uff0c\u53c8\u626d\u66f2\u4e86\u3002 http://t.cn/zHq91Jw', 'created_at': 'Fri May 24 19:12:21 +0800 2013', 'mlevel': 0, 'visible': {'type': 0, 'list_id': 0}, 'idstr': '3581560131802775', 'mid': '3581560131802775', 'source': u'<a href="http://app.weibo.com/t/feed/4pduDW" rel="nofollow">\u672a\u901a\u8fc7\u5ba1\u6838\u5e94\u7528</a>', 'in_reply_to_status_id': '', 'in_reply_to_screen_name': '', 'in_reply_to_user_id': '', 'comments_count': 0, 'geo': None, 'id': 3581560131802775, 'pic_urls': []}, 'domain': '', 'avatar_large': 'http://tp3.sinaimg.cn/2862649054/180/5651992302/1', 'bi_followers_count': 11, 'block_word': 0, 'star': 0, 'id': 2862649054, 'city': '3', 'verified': False, 'follow_me': False, 'verified_reason': '', 'followers_count': 126, 'location': u'\u9999\u6e2f \u4e1c\u533a', 'mbtype': 0, 'profile_url': 'u/2862649054', 'province': '81', 'statuses_count': 460, 'description': '', 'friends_count': 223, 'online_status': 0, 'mbrank': 0, 'idstr': '2862649054', 'profile_image_url': 'http://tp3.sinaimg.cn/2862649054/50/5651992302/1', 'allow_all_act_msg': False, 'allow_all_comment': True, 'geo_enabled': True, 'name': 'snsapi_test', 'lang': 'zh-tw', 'weihao': '', 'remark': '', 'favourites_count': 0, 'screen_name': 'snsapi_test', 'url': '', 'gender': 'm', 'created_at': 'Fri Jul 06 20:21:02 +0800 2012', 'verified_type': -1, 'following': False}
>>> print wa.home_timeline(2)
<0>
[新浪娱乐] at Tue, 28 May 2013 15:33:51 HKT 
  【张艺谋加盟乐视 望媒体未来包涵和支持】今日(28日)下午，乐视网官方微博宣布，张艺谋以艺术总监和签约导演的双重身份，正式加盟@乐视影业。新浪娱乐独家获悉，张艺谋接下来除了执导歌剧《阿依达》外，还将开拍新片，届时将与CAA开启越洋征程。点击图片查看张艺谋发言全文！详细：http://t.cn/zHxVmeK
<1>
[央视财经] at Tue, 28 May 2013 15:33:29 HKT 
  【收评：沪指涨1.23%收复2300 金融地产强势拉升】今日早盘，创业板大跌近3%。午后，金融、地产等权重板块企稳走强，沪指震荡上攻再上2300点。截止收盘沪指报2321.32点，涨28.24点，涨幅1.23%，成交1204亿元；深成指报9441.69点，涨181.06点，涨幅1.96%，成交1297亿元。
```

See `wauto.py` for more functions. 
You can easily add new functions with the help of Sina's api doc. 

## Case 2 -- Asynchronous Call with Rate Limit

Note that most methods in `wauto.py` are already decorated with rate limit function. 
If you `import` wauto from another Python script, the rate limit will take effect.
One example is the `bot.py` script, where we already made a minimal interactive mining env. 

Here is an example:

```
$python -i bot.py
>>> wa.rlq._tasks
[]
>>> wa.follow_by_name('李开复')
>>> wa.rlq._tasks
[<lbucket.RLQTask object at 0x2be1e90>]
>>> wa.run()
[DEBUG][20130528-154629][wauto.py][<lambda>][91]ret: {'request': '/2/friendships/create.json', 'error_code': 20506, 'error': 'already followed'}
```

The explanation for each Python command:

   * `wa.rlq._tasks` just prints out the tasks in the RateLimitQueue. 
   Normally, you don't have to tap into it. 
   Here we only want to show you some difference. 
   * `wa.follow_by_name('李开复')`. 
   The invokation of methods here is same as in `wauto.py`.
   The difference is that the "following operation" is not executed immediately. 
   Instead is is put in the RateLimitQueue, 
   which can be seen from the command below it. 
   * `wa.run()` runs tasks in the RateLimitQueue **subject to rate limiting configurations**. 
   See `SINA_BUCKETS` in `wauto.py` for our configurations.

The best practice is to run `bot.py` periodically (e.g. with cron). 
When you want to execute a set of commands, just enter `python -i bot.py`
and invoke `wa.xxxx()` there **without worrying about rate limit**.
Those commands will be buffered in the queue and executed some time when resources are available. 

## Case 3 -- Asynchronous Call with Callback

Sometimes, we want to buffer a lot of commands and wait for resources. 
After executing them, we want to collect the results somewhere for further process. 
This is done by passing a `callback` parameter to `rate_limit`-decorated methods.

Methods in `wauto.py` are decorated with a `_log` callback by default. 
So you see a log entry after invoking `wa.run()` in the last example. 
The code segment is as follows:

```
@rate_limit(buckets=POLICY_GROUP['follow'], callback=_log)
```

Now you only need to pass self-defined callback into the `wauto` methods to collect the results. 
Note that there is a `data` global variable in `bot.py`. 
You can store intermediate data there. 
It will be automatically serialized when terminating `bot.py` and 
will be loaded when you enter `bot.py` next time. 

The following sample shows you how to collect one's follower list:

```
>>> data['followers']=[]
>>> wa.get_followers(2862649054, callback=lambda x: data['followers'].extend(x['users']))
>>> wa.run()
>>> len(data['followers'])
82
>>> print data['followers'][2]['name']
约TA_微博好友私密约会
```

Explanation:

   * First line initalize an empty list in `data`
   (so that we can call `extend` on this object).
   * The second line calls `get_followers` asynchronously. 
   The callback function is to put the follower list in the end of 
   `data['followers']`.
   * The third line runs tasks in RateLimitQueue. 
   In production, this method may be periodically run by some making `bot.py` a cron job.
   Besides, you may not get results immediately.
   The buffered tasks is only run when resources are available.
   * The last two lines tests the follower list we just obtain.

## Further

   * `queue.py` is grepped from [SNSRouter](https://github.com/hupili/sns-router).
   It helps you store messages in a SQLite DB. 
   We already had a regular tasks in `bot.py`. 
   It fetches timeline and passes message to `queue.py` for storage. 
   The `Waiter` class guarantees the gap between consecutive calls to get timeline 
   is larger than 200 seconds. 
