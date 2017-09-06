#!/usr/bin/env python3

import re
import requests
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
        #print(line)
        if re.search(attribute, line):
            match = True
            #print("found a match {0}".format(line))

        if match:
            if re.search("<div.*", line):
                div_count += 1

            if div_count > 0:
                block_text += line+"\n"

            if re.search("</div.*", line):
                div_count -= 1

            if div_count is 0:
                break;

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
    print(get_div_block(html_file, "lia-quilt-top-users-leader-board"))
    tree = ET.ElementTree(ET.fromstring(get_div_block(html_file, "lia-quilt-top-users-leader-board")))
    root = tree.getroot()

    for link in root.findall("a"):
        print(link.get("href"))




def print_community_stats(html_file):
    block0 = get_div_block(html_file, "lia-quilt-column-hero-bottom")

    print("Overall posts: {0}".format(return_tag(get_div_block(block0, "lia-vitality-metrics-display-net-overall-posts"), "span", "class", "lia-vitality-value")))
    print("Accepted solutions: {0}".format(return_tag(get_div_block(block0, "lia-vitality-metrics-display-net-accepted-solutions"), "span", "class", "lia-vitality-value")))
    print("Registered users: {0}".format(return_tag(get_div_block(block0, "lia-vitality-metrics-display-completed-registrations"), "span", "class", "lia-vitality-value")))
    print("Users online: {0}".format(return_tag(get_div_block(block0, "lia-vitality-users-online"), "span", "class", "lia-vitality-value")))



def print_profile_attr(html_file):
    print("User name {0}".format("unknown"))
    block0 = get_div_block(html_file, "lia-profile-hero-user")

    print("User name: {0}".format(return_tag(get_div_block(block0, "lia-component-users-widget-profile-user-name"), "span", "class", "")))

    #block0 = get_div_block(html_file, "lia-component-user-rank")
    #print("Rank: {0}".format(get_value(get_div_block(get_div_block(block0, "lia-component-user-rank"), "lia-component-user-rank"))))
    print("Rank: {0}".format(return_tag(get_div_block(block0, "lia-component-user-rank"), "div", "class", "lia-user-rank lia-component-user-rank")))

    block0 = get_div_block(html_file, "lia-component-quilt-user-profile-statistics")
    print("Overall posts: {0}".format(get_value(get_div_block(get_div_block(block0, "lia-statistic-net_overall_posts"), "lia-statistic-value"))))
    print("kudos: {0}".format(get_value(get_div_block(get_div_block(block0, "lia-statistic-net_kudos_weight_received"), "lia-statistic-value"))))
    print("solutions: {0}".format(get_value(get_div_block(get_div_block(block0, "lia-statistic-net_accepted_solutions"), "lia-statistic-value"))))


def main():
   r = requests.get("https://supportforums.cisco.com/t5/cisco-support-community/ct-p/5411-support-community-home")
   print_community_stats(r.text)


   r = requests.get("https://supportforums.cisco.com/t5/user/viewprofilepage/user-id/324976")
   print_profile_attr(r.text)

   r = requests.get("https://supportforums.cisco.com/t5/kudos/leaderboardpage/category-id/5411-support-community-home/timerange/one_week")
   get_helpful_users(r.text)

if __name__ == "__main__":
    main()
