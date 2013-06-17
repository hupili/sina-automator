import time
import sys

if len(sys.argv) < 2: 
    print "usage follow.py {file_name_to_id_list}"
    sys.exit(-1)

fn_id_list = sys.argv[1]

from wauto import WeiboAutomator
wa = WeiboAutomator()

# Get ID list to follow
ids = open(fn_id_list).read().split('\n')
ids = filter(lambda x: x != '', ids)
ids = map(lambda x: int(x), ids)

# Try to get current friend list
cur_ids = []
wa.get_friends_ids(callback=lambda x: cur_ids.extend(x['ids']))
time.sleep(2)
wa.run()

# The the difference: only follow new IDs
new_ids = list(set(ids) - set(cur_ids))
print new_ids
print "Cur IDs:", len(cur_ids)
print "Intended IDs:", len(ids)
print "New IDs:", len(new_ids)

# Invoke the follow action for all IDs simultaneously.
# Don't worry about the quota limitation, we'll manage it automatically.
map(wa.follow, new_ids)

# Loop until all users are followed.
# You can call `wa.run()` at any frequency. 
# `wa` will check for quotas and only issue request if there is enough quota (From RLQ).
while wa.rlq.length() > 0:
    time.sleep(1)
    wa.run()
    print "Left IDs", wa.rlq.length()
