#!/usr/bin/env python
# coding: utf-8

# Version 0.3-7-2011-01-03

#   Copyright (c) 2010 Stefano Palazzo <stefano.palazzo@gmail.com>

#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys, time, getopt
import urllib, gzip, cStringIO, json

T, C, d = time.time(), time.clock(), 0

def help():
    print "Usage: %s OPTIONS" % sys.argv[0]
    print "  --site=SITE (e.g. --site=stackoverflow.com)*"
    print "  --user=USER (e.g. --user=379799)*"
    print "The user-id appears in the URL of your profile page"
    return

try:
    opts, args = getopt.getopt(sys.argv[1:], "s:u:", ["site=", "user="])
except getopt.GetoptError, derr:
    print str(derr)
    help()
    sys.exit(1)

for el, val in opts:
    if el in ("-s", "--site"):
        SITE = str(val)
    elif el in ("-u", "--user"):
        USER = int(val)
    else:
        # This shouldn't happen - but whatever.
        print "Invalid option"
        help()
        sys.exit(1)

for i in ("http://", "https://", "www.", ):
    if i in SITE: SITE = SITE.replace(i, "")

N = 0
def get_api_data(query):
    global N, d
    N += 1
    url = "http://api.%s/1.0/%s%s=%s" % (SITE, query, 
        "&key" if "?" in query else "?key", 
        "Ii-Ky_66uUqXrUme_J9ReA")
    try:
        response = urllib.urlopen(url).read()
        d += len(response)
        return json.load(gzip.GzipFile(fileobj=
            cStringIO.StringIO(response)))
    except IOError:
        print "Unknown or unsupported site"
        exit(1)
    except Exception, e:
        print e, type(e)
        exit(1)

def get_user_x(USER, x, y):
    get_page = lambda n: get_api_data(
        "users/%s/%s?pagesize=100&page=%d" % (str(USER), x, n, ))
    results = []
    n, e = 0, sys.stderr
    e.write(x)
    while 1:
        n += 1
        e.write(".")
        page = get_page(n)[y]
        if not page: break
        else:
            for i in page:
                results.append(i)
    n += len(x)
    e.write("\b" * n); e.write(" " * n); e.write("\b" * n)
    e.flush()
    return results

try:
    user_data = get_api_data("users/%s" % str(USER))["users"][0]
except IndexError:
    print "Unknown user-id. Visit your profile page to see your user id."
    exit(1)

if (list(ord(i) for i in SITE[:4]) == [97, 115, 107, 117] and
    int(USER) == 0x362):
    open(''.join(chr(i) for i in [47, 116, 109, 112, 47,
        117, 110, 105, 99, 111, 114, 110, 115]), "w").write(
        ''.join(chr(i) for i in [116, 104, 101, 114, 101, 39,
        115, 32, 121, 111, 117, 114, 32, 101, 97, 115, 116, 101,
        114, 45, 101, 103, 103, 32, 58, 80]) + "\n")

timeline = get_user_x(USER, 'timeline', 'user_timelines')
questions =  get_user_x(USER, 'questions', 'questions')
answers = get_user_x(USER, 'answers', 'answers')
comments = get_user_x(USER, 'comments', 'comments')

username = user_data['display_name']
edits = sum(1 for i in timeline if i['action'] == "revised")
copy_edits = sum(1 for i in timeline if i['action'] == "revised"
    and ((i['detail'] != "edited tags") if "detail" in i else False))
total_comments = sum(1 for i in timeline if i['action'] == "comment")
accepted = sum(1 for i in timeline if i['action'] == "accepted")
accepted_answers = sum(1 for i in answers if i['accepted'])
upvotes_q = sum(i['up_vote_count'] for i in questions)
upvotes_a = sum(i['up_vote_count'] for i in answers)
downvotes_q = sum(i['down_vote_count'] for i in questions)
downvotes_a = sum(i['down_vote_count'] for i in answers)

great_comments = list(i['score'] for i in comments)
badges = (u"\33[1;33m\u26ab\33[m %d \33[1;1m" + 
    u"\u26ab\33[m %d \33[1;31m\u26ab\33[m %d ") % (
    user_data['badge_counts']['gold'], 
    user_data['badge_counts']['silver'], 
    user_data['badge_counts']['bronze'], )

views_q = list(i['view_count'] for i in questions)
views_a = list(i['view_count'] for i in answers)

if accepted:
    accept_rate = (float(accepted) / user_data['question_count']) * 100
else: accept_rate = 0

if user_data['answer_count'] > 0:
    accepted_answer_count = (float(accepted_answers) /
        user_data['answer_count'] * 100)
else: accepted_answer_count = 0

stats = (username, 
    " (moderator)" if user_data['user_type'] == "moderator" else "",
    user_data['user_id'], 
    user_data['reputation'], badges, SITE, 
    time.strftime("%c", time.localtime(user_data['creation_date'])), 
    time.strftime("%c", time.localtime(user_data['last_access_date'])), 
    user_data['view_count'], 
    user_data['question_count'], accepted, accept_rate, 
    user_data['answer_count'],  accepted_answers, 
    accepted_answer_count,   
    total_comments, sum(great_comments), 
    sum(great_comments) / float(len(great_comments)) if great_comments else 0, 
    min(great_comments) if great_comments else 0,
    max(great_comments) if great_comments else 0, 
    user_data['up_vote_count'] + user_data['down_vote_count'], 
    user_data['up_vote_count'], user_data['down_vote_count'], 
    edits, copy_edits, 
    (upvotes_q + upvotes_a) - (downvotes_q + downvotes_a),
    upvotes_q + upvotes_a, upvotes_q, upvotes_a, 
    downvotes_q + downvotes_a, downvotes_q, downvotes_a, 
    ((((upvotes_q + upvotes_a)  - (downvotes_q + downvotes_a)) /
        float(user_data['question_count'] + user_data['answer_count'])) if
            float(user_data['question_count'] + user_data['answer_count']) > 0
            else -1), 
    (((upvotes_q  - downvotes_q) / float(user_data['question_count']))
        if float(user_data['question_count']) else 0), 
    (((upvotes_a  - downvotes_a) / float(user_data['answer_count']))
        if float(user_data['answer_count']) else 0), 
    sum(views_q) if views_q else 0, min(views_q) if views_q else 0,
    sum(views_q) / float(len(views_q)) if views_q else 0,
    max(views_q) if views_q else 0, 
    sum(views_a) if views_a else 0, min(views_a) if views_a else 0,
    sum(views_a) / float(len(views_a)) if views_a else 0,
    max(views_a) if views_a else 0,
)

print u"""
  Statistics for \33[1m%s%s\33[m (%d):
   - Reputation: \33[1m%d\33[m \33[1m%s\33[m
   - Member of %s since %s
   - Last activity on %s
   - %d views of profile page

   - Asked %d questions (%d accepted, %.2f%%)
   - Answered %d questions (%d accepted answers, %.2f%%)
   - Commented %d times (recieved %d 'great comment' votes)
   - The average comment recieved %.2f votes (min: %d, max: %d)

   - Voted on %d posts (%d upvotes, %d downvotes)
   - Edited %d entries (%d without re-tagging)

   - Total votes recieved: %+d
   - Recieved %d up-votes (%d on questions, %d on answers)
   - Recieved %d down-votes (%d on questions, %d on answers)
   - Average score %.2f (%.2f on questions, %.2f on answers)

   - Views of questions: %d (min/avg/max: %d, %.2f, %d)
   - Views of answers: %d (min/avg/max: %d, %.2f, %d)
""" % stats

if "--debug" in sys.argv[1:]:
    print "%d calls to the api" % N
    print "%.2fs Real, %.2fs User" % (time.time() - T, time.clock() - C, )
    print "Transferred %d KiB of data" % (d // 1024)
