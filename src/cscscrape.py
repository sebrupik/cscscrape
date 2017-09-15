#!/usr/bin/env python3
import re
import requests
import sqlite3
import xml.etree.ElementTree as ET


def get_div_block(html_file, attribute):
    return get_tag_block(html_file, attribute, "div")


def get_tag_block(html_file, attribute, tag_name=""):
    TAG_OPEN="<"+tag_name
    TAG_CLOSED="</"+tag_name

    block_text = ""
    div_count = 0
    match = False
    for line in html_file.splitlines():
        if re.search(attribute, line):
            match = True

        if match:
            if re.search(TAG_OPEN+".*", line):
                div_count += 1

            if div_count > 0:
                block_text += line+"\n"

            if re.search(TAG_CLOSED+".*", line):
                div_count -= 1

            if div_count is 0:
                break

    return block_text


def get_value(div_block):
    for index, value in enumerate(div_block.splitlines()):
        if index == 1:
            return value.strip()


def return_tag(tag_block, tag_name, attribute_name, attribute_value):
    tree = ET.ElementTree(ET.fromstring(tag_block))
    root = tree.getroot()

    for span in root.iter(tag_name):
        if span.get(attribute_name) == attribute_value:
            return span.text.strip()


def get_helpful_users(html_file):
    #print(get_div_block(html_file, "lia-quilt-top-users-leader-board"))
    users = []

    for line in get_div_block(html_file, "lia-quilt-top-users-leader-board").splitlines():

        if re.search("(<a).*(>)", line):
            uid = strip_uid_from_link(line)
            if uid is not None:
                if uid not in users:
                    users.append(uid)

    return users


def strip_uid_from_link(a_block):
    match = re.search(r"(user-id\/)(?P<uid>\d+)(\")", a_block)
    if match:
        return match.group(2)
    else:
        return None


def get_community_stats(html_file):
    stats = {}
    block0 = get_div_block(html_file, "lia-quilt-column-hero-bottom")

    #print("Overall posts: {0}".format(return_tag(get_div_block(block0, "lia-vitality-metrics-display-net-overall-posts"), "span", "class", "lia-vitality-value")))
    stats['overall_posts'] = return_tag(get_div_block(block0, "lia-vitality-metrics-display-net-overall-posts"), "span", "class", "lia-vitality-value")
    #print("Accepted solutions: {0}".format(return_tag(get_div_block(block0, "lia-vitality-metrics-display-net-accepted-solutions"), "span", "class", "lia-vitality-value")))
    stats['accepted_solutions'] = return_tag(get_div_block(block0, "lia-vitality-metrics-display-net-accepted-solutions"), "span", "class", "lia-vitality-value")
    #print("Registered users: {0}".format(return_tag(get_div_block(block0, "lia-vitality-metrics-display-completed-registrations"), "span", "class", "lia-vitality-value")))
    stats['users_registered'] = return_tag(get_div_block(block0, "lia-vitality-metrics-display-completed-registrations"), "span", "class", "lia-vitality-value")
    #print("Users online: {0}".format(return_tag(get_div_block(block0, "lia-vitality-users-online"), "span", "class", "lia-vitality-value")))
    stats['users_online'] = return_tag(get_div_block(block0, "lia-vitality-users-online"), "span", "class", "lia-vitality-value")

    return stats


def get_profile_attr(html_file, uid):
    user = {}
    user['uid'] = uid

    block0 = get_div_block(html_file, "lia-profile-hero-user")
    user['username'] = return_tag(get_div_block(block0, "lia-component-users-widget-profile-user-name"), "span", "class", "")
    user['rank'] = return_tag(get_div_block(block0, "lia-component-user-rank"), "div", "class", "lia-user-rank lia-component-user-rank")

    block0 = get_div_block(html_file, "lia-component-quilt-user-profile-statistics")
    user['overall_posts'] = get_value(get_div_block(get_div_block(block0, "lia-statistic-net_overall_posts"), "lia-statistic-value"))
    user['kudos'] = get_value(get_div_block(get_div_block(block0, "lia-statistic-net_kudos_weight_received"), "lia-statistic-value"))
    user['solutions'] = get_value(get_div_block(get_div_block(block0, "lia-statistic-net_accepted_solutions"), "lia-statistic-value"))

    return user


def build_database_tables(_cursor):
    #con = sqlite3.connect("csc.db")
    #_cursor = con.cursor()
    _cursor.execute("CREATE TABLE community_stats (pk INTEGER PRIMARY KEY, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, overall_posts INTEGER, accepted_solutions INTEGER, users_registered INTEGER, users_online INTEGER)")
    _cursor.execute("CREATE TABLE users (uid INTEGER PRIMARY KEY, username TEXT)")
    _cursor.execute("CREATE TABLE user_snapshot (us_pk INTEGER PRIMARY KEY, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, uid INTEGER,  rank TEXT, overall_posts INTEGER, kudos INTEGER, solutions INTEGER)")


def update_users_stats(_cursor, user_dict):
    _cursor.execute("SELECT * FROM users WHERE uid=?", (user_dict['uid'],))
    row = _cursor.fetchone()

    if row is None:
        print("Adding a new user: {0}".format(user_dict['username']))
        _cursor.execute("INSERT INTO users VALUES (?,?)", (user_dict['uid'], user_dict['username']))

    _cursor.execute("INSERT INTO user_snapshot VALUES (?,?,?,?,?,?,?)", (None, None, user_dict['uid'], user_dict['rank'], user_dict['overall_posts'], user_dict['kudos'], user_dict['solutions']))


def main():
    con = sqlite3.connect('csc.db')
    _cursor = con.cursor()
    _cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='community_stats'")
    row = _cursor.fetchone()

    if row is None:
        build_database_tables(_cursor)
        con.commit()


    r = requests.get("https://supportforums.cisco.com/t5/cisco-support-community/ct-p/5411-support-community-home")
    stats = get_community_stats(r.text)
    print(stats)
    _cursor.execute("INSERT INTO community_stats VALUES (?,?,?,?,?,?)", (None, None, stats['overall_posts'], stats['accepted_solutions'], stats['users_registered'], stats['users_online']))


    # find me the users providing soutions
    page_number = 1
    leaderboard = requests.get("https://supportforums.cisco.com/t5/kudos/leaderboardpage/category-id/5411-support-community-home/timerange/one_week/page/{0}".format(page_number))
    while leaderboard.status_code == requests.codes.ok:
        next_page_str = "https://supportforums.cisco.com/t5/kudos/leaderboardpage/category-id/5411-support-community-home/timerange/one_week/page/{0}".format(page_number)
        leaderboard = requests.get(next_page_str)
        print(page_number)
        print(leaderboard.url)
        if(leaderboard.url != next_page_str):
            print("we are being returned to the last indexed page, breaking.")
            break

        for uid in get_helpful_users(leaderboard.text):
            user = requests.get("https://supportforums.cisco.com/t5/user/viewprofilepage/user-id/{0}".format(uid))
            #print(get_profile_attr(user.text, uid))
            update_users_stats(_cursor, get_profile_attr(user.text, uid))
            con.commit()

        page_number += 1


if __name__ == "__main__":
    main()
